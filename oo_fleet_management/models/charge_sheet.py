import copy
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FleetChargeSheet(models.Model):
    _name = 'fleet.charge.sheet'
    _description = 'Fleet Charge Sheet'

    name = fields.Char(string='Name', required=True,
                       readonly=True, default='/', copy=False)
    date = fields.Date(string='Date', required=True,
                       default=fields.Date.today())
    driver_id = fields.Many2one('hr.employee',
                                string='Driver', required=True, 
                                domain="[('is_driver', '=', True), ('company_id', 'in', (company_id, False))]")
    charge_ids = fields.One2many(
        'fleet.charge.sheet.line', inverse_name='charge_id', string='Charge List')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.company_id.fleet_currency_id, required=True)
    state = fields.Selection(string='Status',
                             selection=[('draft', 'Draft'), ('done',
                                                             'Done'), ('cancelled', 'Cancelled')],
                             default='draft')
    total_amount = fields.Monetary(
        'Total Amount', currency_field='currency_id', compute='_compute_total_amount')
    move_ids = fields.Many2many(
        'account.move', string='Journal Entries', readonly=True, copy=False)
    recoverable_id = fields.Many2one(
        'fleet.driver.recoverable', string='Recoverable Move', copy=False)

    @api.depends('charge_ids', 'charge_ids.price_total')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.charge_ids.mapped('price_total'))

    def _add_driver_recoverable_charge(self, move):
        return self.env['fleet.driver.recoverable'].create({
            'driver_id': self.driver_id.id,
            'name': f"{self.name} | {','.join(self.charge_ids.mapped('product_id.name'))}",
            'date': self.date,
            'charge_id': self.id,
            'move_id': move.id,
            'amount': self.currency_id._convert(
                self.total_amount, self.company_id.fleet_currency_id, self.company_id, self.date)
        })

    def _prepare_move_lines(self):
        line_ids = [(0, 0, {
            'name': self.name,
            'debit': self.total_amount,
            'credit': 0,
            'amount_currency': self.total_amount,
            'currency_id': self.currency_id.id,
            'account_id': self.company_id.fleet_driver_recoverable_account_id.id
        })]
        for line in self.charge_ids:
            line_ids.append((0, 0, {
                'name': self.name,
                'debit': 0,
                'credit': line.price_total,
                'amount_currency': -line.price_total,
                'currency_id': self.currency_id.id,
                'account_id': line.product_id.expense_account_id.id
            }))
        return line_ids

    def _prepare_move_vals(self):
        self.ensure_one()
        return {
            'journal_id': self.charge_ids[0].product_id.categ_id.property_stock_journal.id,
            'company_id': self.company_id.id,
            'date': self.date,
            'move_type': 'entry',
            'state': 'draft',
            'ref': f'Driver Recoverables {self.name}',
            'name': '/',
            'currency_id': self.currency_id.id,
            'line_ids': self._prepare_move_lines()
        }

    def _create_driver_charge_recoverable(self):
        for rec in self:
            move = self.env['account.move'].create(rec._prepare_move_vals())
            move._inverse_amount_total()
            recoverable_id = rec._add_driver_recoverable_charge(move)
            rec.write({
                'move_ids': [(6, 0, move.ids)],
                'recoverable_id': recoverable_id.id
            })
            move._post()

    def action_confirm(self):
        for rec in self:
            if not rec.charge_ids:
                raise ValidationError('Missing charge items!')
            
            name = rec.name == '/' and self.env['ir.sequence'].next_by_code(
                'fleet.charge.sheet.sequence') or rec.name
            rec.write({'state': 'done', 'name': name})
            rec._create_driver_charge_recoverable()

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_get_account_moves(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account.action_move_journal_line')
        action['domain'] = [('id', 'in', self.move_ids.ids)]
        return action


class FleetChargeSheetLine(models.Model):
    _name = 'fleet.charge.sheet.line'
    _description = 'Fleet Charge Sheet Line'

    charge_id = fields.Many2one('fleet.charge.sheet', string='Charge Sheet')
    currency_id = fields.Many2one(
        related='charge_id.currency_id', string='Currency')
    company_id = fields.Many2one(
        related='charge_id.company_id', string='Company')
    truck_id = fields.Many2one('fleet.truck', string='Truck')
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    price_unit = fields.Monetary(
        string='Price Unit', required=True, currency_field='currency_id')
    price_total = fields.Monetary(string='Amount',
                                  required=True,
                                  currency_field='currency_id',
                                  compute='_compute_price_total')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.price_unit = rec.product_id.list_price

    @api.depends('price_unit', 'quantity')
    def _compute_price_total(self):
        for rec in self:
            rec.price_total = rec.price_unit * rec.quantity
