from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError


class FleetWorkshop(models.Model):
    _name = 'fleet.workshop'
    _description = 'Fleet Workshop'

    name = fields.Char(string='Name', default='/', readonly=True, copy=False)
    truck_id = fields.Many2one('fleet.truck', string='Truck', 
                               required=True,
                               domain="[('company_id', 'in', (company_id, False))]")
    date = fields.Date(string='Date', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection(string='Status',
                             selection=[('draft', 'Draft'), ('in_progress', 'In Progress'),
                                        ('done', 'Done'), ('cancelled', 'Cancelled')],
                             default='draft',
                             readonly=True)
    scrap_ids = fields.One2many(
        comodel_name='stock.scrap', inverse_name='workshop_id', string='Materials')
    analytic_account_id = fields.Many2one(
        related='truck_id.analytic_account_id', string='Analytic Account')
    analytic_tag_id = fields.Many2one(
        'account.analytic.tag', string='Trip', copy=False)
    location_id = fields.Many2one('stock.location', string='Location',
                                  domain="[('usage', '=', 'internal'), ('company_id', 'in', [company_id, False])]",
                                  check_company=True,
                                  required=True)
    stock_move_ids = fields.Many2many(
        'stock.move', string='Stock Moves', readonly=True, copy=False)
    move_ids = fields.Many2many(
        'account.move', string='Moves', readonly=True, copy=False)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            warehouse = self.env['stock.warehouse'].search(
                [('company_id', '=', self.company_id.id)], limit=1)
            if self.location_id.company_id != self.company_id:
                self.location_id = warehouse.lot_stock_id
        else:
            self.location_id = False

    def action_draft(self):
        self.write({'state': 'draft'})

    def _validate_scrap_quantities(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        ctx = dict(self.env.context)
        for line in self.mapped('scrap_ids').filtered(lambda s: s.product_id.type == 'product'):
            available_qty = sum(self.env['stock.quant']._gather(line.product_id,
                                                                line.location_id,
                                                                line.lot_id,
                                                                line.package_id,
                                                                line.owner_id,
                                                                strict=True).mapped('quantity'))
            scrap_qty = line.product_uom_id._compute_quantity(
                line.scrap_qty, line.product_id.uom_id)
            if float_compare(available_qty, scrap_qty, precision_digits=precision) <= 0:
                ctx.update({
                    'default_product_id': line.product_id.id,
                    'default_location_id': line.location_id.id,
                    'default_scrap_id': line.id,
                    'default_quantity': scrap_qty,
                    'default_product_uom_name': line.product_id.uom_name
                })
                return {
                    'name': line.product_id.display_name + ': Insufficient Quantity To Scrap',
                    'view_mode': 'form',
                    'res_model': 'stock.warn.insufficient.qty.scrap',
                    'view_id': self.env.ref('stock.stock_warn_insufficient_qty_scrap_form_view').id,
                    'type': 'ir.actions.act_window',
                    'context': ctx,
                    'target': 'new'
                }

    def action_start(self):
        for rec in self:
            if not rec.scrap_ids:
                raise ValidationError('Missing Scrap lines')
            rec._validate_scrap_quantities()
            name = rec.name == '/' and self.env['ir.sequence'].next_by_code(
                'fleet.workshop.sequence') or rec.name
            rec.write({
                'state': 'in_progress',
                'name': name
            })
            rec.scrap_ids.write({
                'company_id': rec.company_id.id,
                'origin': rec.name,
                'date_done': rec.date,
                'location_id': rec.location_id.id,
            })

    def _modify_move_lines(self):
        # There is a dependent warehouse module that leads to this hack
        moves = self.env['account.move']
        for scrap in self.scrap_ids:
            moves |= self.env['account.move'].search([('ref', 'like', scrap.name)], limit=1)
        moves.button_draft()
        moves.mapped('line_ids').filtered(lambda m: m.debit > 0).write({
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_id.ids)]
        })
        moves._post()
        
    def action_complete(self):
        for rec in self:
            for line in rec.scrap_ids:
                line.action_validate()
            rec.write({
                'stock_move_ids': [(6, 0, rec.scrap_ids.mapped('move_id').ids)],
                'move_ids': [(6, 0, rec.scrap_ids.mapped('move_id').mapped('account_move_ids').ids)],
                'state': 'done'
            })
            rec._modify_move_lines()

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_get_stock_move_lines(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'stock.stock_move_line_action')
        action['domain'] = [('move_id', 'in', self.stock_move_ids.ids)]
        return action

    def action_get_account_moves(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account.action_move_journal_line')
        action['domain'] = [
            ('id', 'in', self.stock_move_ids.mapped('account_move_ids').ids)]
        return action


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    workshop_id = fields.Many2one('fleet.workshop', string='Fleet Workshop')
