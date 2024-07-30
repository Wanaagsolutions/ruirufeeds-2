# -*- coding: utf-8 - *-
import logging

from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

DOCUMENTS_APPLICABLE_ON = [
    ('driver', 'Driver'), ('trip', 'Trip'), ('truck', 'Truck')]


INVOICE_TYPE_MAP = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
}

_logger = logging.getLogger(__name__)


class FleetTrip(models.Model):
    _name = 'fleet.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    _description = 'Fleet Order Trips'

    name = fields.Char(string='Name', required=True,
                       readonly=True, tracking=True, index=True)
    order_id = fields.Many2one('fleet.order', string='Order No', required=True,
                               readonly=True, tracking=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True,
                                 readonly=True, 
                                 domain="[('partner_type', '=', 'customer'), ('company_id', 'in', (company_id, False))]",
                                 tracking=True, index=True)
    product_id = fields.Many2one('product.product', string='Cargo', required=True,
                                 readonly=True, tracking=True, index=True)
    cargo_truck_type = fields.Selection(
        string='Cargo Truck Type', related='product_id.truck_type')
    product_uom_id = fields.Many2one(
        related='order_id.transaction_uom_id', string='Uom')
    truck_id = fields.Many2one(
        'fleet.truck', string='Truck', tracking=True, index=True, domain="[('company_id', 'in', (company_id, False))]")
    truck_ownership = fields.Selection(
        string='Truck Ownership', related='truck_id.ownership')
    driver_id = fields.Many2one('hr.employee', string='Driver', required=True,
                                domain="[('is_driver', '=', True), ('company_id', 'in', (company_id, False))]",
                                tracking=True, index=True)
    date = fields.Date(string='Trip Start Date', required=True, tracking=True, index=True)
    end_date = fields.Date(string='Trip End Date')
    route_id = fields.Many2one('fleet.route', string='Route', tracking=True, 
                               domain="[('company_id', 'in', (company_id, False))]")
    distance = fields.Float(string='Trip Distance',
                            related='route_id.distance')
    pickup_location = fields.Char(
        string='Pickup Location', related='route_id.pickup_location')
    drop_location = fields.Char(
        string='Drop Off Location', related='route_id.drop_location')
    pickup_city = fields.Char(string='Pickup City',
                              related='route_id.pickup_city')
    drop_city = fields.Char(string='Drop Off City',
                            related='route_id.drop_city')
    pickup_country_id = fields.Many2one(
        'res.country', string='Pickup Country', related='route_id.pickup_country_id')
    drop_country_id = fields.Many2one(
        'res.country', string='Drop Off Country', related='route_id.drop_country_id')
    start_odoometer = fields.Float(string='Starting Odoometer', tracking=True)
    end_odoometer = fields.Float(string='Ending Odoometer', tracking=True)
    ap_type = fields.Selection(string='Ap Type', required=True, default='percentage', selection=[
                               ('percentage', 'Percentage (%)'), ('per_unit', 'Amount Per Unit')], tracking=True)
    ap_rate = fields.Float(string='AP Rates', tracking=True)
    currency_id = fields.Many2one(
        related='order_id.currency_id', string='Currency')
    loaded_qty = fields.Float(string='Loaded QTY', tracking=True)
    loaded_qty_20 = fields.Float(string='Loaded QTY @20', tracking=True)
    offloaded_qty = fields.Float(string='Off Loaded QTY', tracking=True)
    offloaded_qty_20 = fields.Float(string='Off Loaded QTY @20', tracking=True)
    short_qty = fields.Float(
        readonly=True, string='Abnormal Shortage', digits=(5, 4))
    cargo_seal_ids = fields.One2many(
        'fleet.trip.seal', inverse_name='trip_id', string='Cargo Seals')
    trip_document_ids = fields.One2many(
        'fleet.trip.document', inverse_name='trip_id', string='Trip Documents')
    loading_date = fields.Datetime('Loading Date', tracking=True)
    offloading_date = fields.Datetime('Offloading Date', tracking=True)
    state = fields.Selection(string='Status',
                             selection=[('draft', 'Yard Location'),
                                        ('loading', 'Loading'),
                                        ('in_progress', 'In Progress'),
                                        ('completed', 'Completed'),
                                        ('invoiced', 'Invoiced'),
                                        ('cancelled', 'Cancelled')],
                             default='draft', copy=False, tracking=True)
    truck_capacity = fields.Float(string='Truck Capacity', readonly=True)
    analytic_tag_id = fields.Many2one(
        'account.analytic.tag', string='Trip Analytics Tag', copy=False, readonly=True)
    yard_location = fields.Char(string='Truck Yard Location')
    pod_number = fields.Char(string='Proof of Delivery Number')
    allowable_shortage = fields.Float(
        string='Allowable Shortage', readonly=True, compute='_compute_allowable_shortage')
    company_id = fields.Many2one(
        related='order_id.company_id', string='Company')
    shortage_rate = fields.Monetary(
        string='Shortage Rate', currency_field='currency_id', required=True, tracking=True)

    @property
    def is_tanker_cargo(self):
        return self.cargo_truck_type == 'tanker'

    @api.constrains('pod_number')
    def _constrains_pod_number(self):
        for rec in self.filtered('pod_number'):
            dups = self.search_count(
                [('id', '!=', rec.id),
                 ('pod_number', '=', rec.pod_number),
                 ('state', '!=', 'cancelled')])
            if dups:
                raise ValidationError(
                    'Two trips cannot have the same proof of delivery number')

    @api.onchange('route_id')
    def _onchange_route_id(self):
        for rec in self:
            rec.end_odoometer = rec.start_odoometer + rec.distance

    @api.depends('product_id', 'product_id.allowed_shortage', 'loaded_qty_20')
    def _compute_allowable_shortage(self):
        for rec in self:
            rec.allowable_shortage = rec.product_id.allowed_shortage * 0.01 * rec.loaded_qty_20

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('fleet.trip.sequence')
        if vals.get('name'):
            vals['name'] = f"{name} {vals['name']}"
        else:
            vals['name'] = name
        return super().create(vals)

    def _can_close_states(self):
        return {'invoiced', 'cancelled'}

    def _check_odoometer_readings(self):
        for rec in self:
            if float_is_zero(rec.start_odoometer, precision_digits=2):
                raise ValidationError(
                    'Please add a valid start odoometer readings.')

            if float_is_zero(rec.start_odoometer, precision_digits=2) or \
                    float_is_zero(rec.end_odoometer, precision_digits=2):
                raise ValidationError(
                    'Please add a valid start or end odoometer readings.')

            if float_compare(rec.end_odoometer, rec.start_odoometer, precision_digits=2) <= 0:
                raise ValidationError(
                    'End Odoometer must be greater than start Odoometer')

    @api.onchange('offloading_date')
    def _onchange_offloading_date(self):
        for rec in self:
            if not rec.end_date:
                rec.end_date = rec.offloading_date.date()

    @api.constrains('loading_date', 'offloading_date')
    def _constrains_loading_offloading_date(self):
        for rec in self:
            if rec.offloading_date and rec.offloading_date < rec.loading_date:
                raise ValidationError(
                    'Offloading date must be greater than loading date')

    def _check_loaded_quantities(self):
        for rec in self:
            if float_is_zero(rec.loaded_qty, precision_digits=2) or \
                    self.is_tanker_cargo and float_is_zero(rec.loaded_qty_20, precision_digits=2):
                raise ValidationError(
                    'Loaded Quantities must be greater than 0!')

    def _check_offloaded_quantities(self):
        for rec in self:
            if float_is_zero(rec.offloaded_qty, precision_digits=2) or \
                    self.is_tanker_cargo and float_is_zero(rec.offloaded_qty_20, precision_digits=2):
                raise ValidationError(
                    'OffLoaded Quantities must be greater than 0!')
            if float_compare(rec.offloaded_qty_20, rec.loaded_qty_20, precision_digits=2) > 0:
                raise ValidationError(
                    'Offloaded Quantities must be less than loaded quantities!')

    def action_start_trip(self):
        for rec in self:
            rec.write({'state': 'loading'})

    def action_mark_loaded(self):
        for rec in self:
            rec._check_loaded_quantities()
            rec.truck_id.update_status('in_trip')
            rec.write({'state': 'in_progress'})
            _logger.info(f'Started trip {rec.name}')

    def _calculate_driver_short(self):
        for rec in self.filtered(lambda t: t.cargo_truck_type == 'tanker'):
            short_qty = (rec.loaded_qty_20 - rec.offloaded_qty_20) - \
                (rec.product_id.allowed_shortage * 0.01 * rec.loaded_qty_20)
            if short_qty > 0:
                rec.short_qty = short_qty
                _logger.info(
                    f'Driver {rec.driver_id.name} incurred short {rec.short_qty}')

    def _add_driver_recoverable_payment(self, move):
        self.ensure_one()
        if self.truck_id.ownership == 'contractor':
            # Only consider contractor trucks as company trucks are recovered from expenses
            amount = self.short_qty * self.shortage_rate
            amount = self.currency_id._convert(
                amount, self.company_id.fleet_currency_id, self.company_id, fields.Date.today())
            je = self.env['fleet.driver.recoverables'].create({
                'driver_id': self.driver_id.id,
                'date': self.date,
                'name': f'{self.name} - {self.product_id.name}',
                'trip_id': self.id,
                'move_id': move.id,
                'amount': -amount
            })
            _logger.info(
                f'Driver {self.driver_id.name} short paid from contractor je {je.id}')

    def create_analytic_account_and_tags(self):
        analytic_model = self.env['account.analytic.tag']
        account_model = self.env['account.analytic.account']

        for rec in self:
            if not rec.truck_id.analytic_account_id:
                account_id = account_model.create({
                    'name': f'Truck: {rec.truck_id.name}',
                    'truck_id': rec.truck_id.id
                })
                rec.truck_id.analytic_account_id = account_id.id
                _logger.info(
                    f'Created truck analytic account {account_id.name}')

            if not rec.analytic_tag_id:
                rec.analytic_tag_id = analytic_model.create({
                    'name': f'Trip: {rec.name}',
                    'trip_id': rec.id
                }).id
                _logger.info(
                    f'Created trip analytic tag {rec.analytic_tag_id.name}')

    def action_complete_trip(self):
        for rec in self:
            rec._check_odoometer_readings()
            rec._check_offloaded_quantities()
            if rec.truck_id.ownership == 'contractor' and float_is_zero(rec.ap_rate, precision_digits=2) or rec.ap_rate < 0:
                raise ValidationError('The Ap Rate must be greater than 0!')

            if not rec.trip_document_ids:
                raise ValidationError('Please add trip documents!')

            rec.truck_id.update_status('available')
            rec.truck_id.update_mileage(rec.end_odoometer)
            rec._calculate_driver_short()
            rec.write({'state': 'completed'})
            _logger.info(f'Completed trip {rec.name}')

    def action_reset_to_progress(self):
        self.write({'state': 'in_progress'})

    def action_cancel_trip(self):
        for rec in self:
            rec.truck_id.update_status('available')
            rec.analytic_tag_id.write({'is_closed': True})
            rec.write({'state': 'cancelled'})
            _logger.info(f'Cancelled trip {rec.name}')

    def _prepare_invoice_line_vals(self):
        self.ensure_one()
        default_account_id = self.company_id.fleet_income_journal_id.default_account_id
        route_account_id = self.route_id.company_truck_account_id
        price_unit = self.order_id.ar_rate
        qty = self.is_tanker_cargo and self.loaded_qty_20 or self.loaded_qty

        if self.truck_id.ownership == 'contractor':
            default_account_id = self.company_id.fleet_income_contractor_truck_account_id
            route_account_id = self.route_id.contractor_truck_account_id
            price_unit = (
                self.ap_rate * 0.01 * self.order_id.ar_rate) if self.ap_type == 'percentage' else self.ap_rate

        account_id = route_account_id.id or default_account_id.id

        return {
            'name': f'{self.name} - {self.product_id.name}',
            'account_id': account_id,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.order_id.transaction_uom_id.id,
            'price_unit': price_unit,
            'tax_ids':  [(6, 0, self.product_id.taxes_id.ids)],
            'analytic_account_id': self.truck_id.analytic_account_id.id,
            'analytic_tag_ids': [(4, self.analytic_tag_id.id)],
            'trip_id': self.id
        }

    def prepare_move_vals(self, move_type='out_invoice'):
        self.ensure_one()
        journal_id = self.company_id.fleet_income_journal_id
        partner_id = self.partner_id
        if move_type == 'in_invoice':
            journal_id = self.company_id.fleet_expense_journal_id
            partner_id = self.truck_id.supplier_id

        return {
            'move_type': move_type,
            'state': 'draft',
            'company_id': self.company_id.id,
            'partner_id': partner_id.id,
            'invoice_date': self.end_date,
            'ref': self.name,
            'name': '/',
            'currency_id': self.order_id.currency_id.id,
            'journal_id': journal_id.id,
            'trip_id': self.id,
        }

    def create_invoice(self):
        moves = self.env['account.move']
        for rec in self:
            vals = rec.prepare_move_vals(move_type='out_invoice')
            vals['invoice_line_ids'] = [
                (0, 0, rec._prepare_invoice_line_vals())]
            invoice = self.env['account.move'].create(vals)
            rec.order_id.write({'move_ids': [(4, invoice.id)]})
            moves |= invoice
            _logger.info(f'Trip {self.name} invoice created {invoice.id}')
        return moves

    def create_bill(self):
        moves = self.env['account.move']
        for rec in self.filtered(lambda t: t.truck_id.ownership == 'contractor'):
            vals = rec.prepare_move_vals(move_type='in_invoice')
            vals['invoice_line_ids'] = [
                (0, 0, rec._prepare_invoice_line_vals())]
            bill = self.env['account.move'].create(vals)
            rec.order_id.write({'move_ids': [(4, bill.id)]})
            moves |= bill
            _logger.info(f'Trip {self.name} bill created {bill.id}')
        return moves

    def _get_shorts_entry_defaults(self):
        self.ensure_one()
        company_id = self.order_id.company_id
        if self.truck_id.ownership == 'company':
            src_partner = False
            dest_partner = self.partner_id
            journal = company_id.fleet_income_journal_id
            src_account = company_id.fleet_driver_recoverable_account_id
            dest_account = dest_partner.property_account_receivable_id or \
                dest_partner.parent_id.property_account_receivable_id
        else:
            src_partner = self.truck_id.supplier_id
            dest_partner = self.partner_id

            journal = company_id.fleet_contractor_shorts_journal_id
            src_account = src_partner.property_account_payable_id or src_partner.parent_id.property_account_payable_id
            dest_account = dest_partner.property_account_receivable_id or \
                dest_partner.parent_id.property_account_receivable_id

        return {
            'journal_id': journal,
            'src_account_id': src_account,
            'dest_account_id': dest_account,
            'src_partner_id': src_partner,
            'dest_partner_id': dest_partner,
        }

    def _create_trip_shorts_recoverable_entry(self):
        moves = self.env['account.move']
        for rec in self.filtered(lambda t: t.short_qty and t.cargo_truck_type == 'tanker'):
            defaults = rec._get_shorts_entry_defaults()
            amount = rec.short_qty * rec.shortage_rate
            amount_currency = 0
            if rec.company_id.fleet_currency_id != rec.currency_id:
                amount_currency = amount

            values = {
                'journal_id': defaults['journal_id'].id,
                'company_id': rec.company_id.id,
                'date': self.end_date,
                'move_type': 'entry',
                'state': 'draft',
                'ref': f'Trip Shorts {rec.name}',
                'name': '/',
                'currency_id': rec.currency_id.id,
                'line_ids': [(0, 0, {
                    'name': rec.name,
                    'debit': amount,
                    'credit': 0,
                    'amount_currency': amount_currency,
                    'currency_id': rec.currency_id.id,
                    'account_id': defaults['src_account_id'].id,
                    'partner_id': defaults['src_partner_id'] and defaults['src_partner_id'].id,
                }),
                    (0, 0, {
                        'name': rec.name,
                        'debit': 0,
                        'credit': amount,
                        'amount_currency': amount_currency * -1,
                        'currency_id': rec.currency_id.id,
                        'account_id': defaults['dest_account_id'].id,
                        'partner_id': defaults['dest_partner_id'] and defaults['dest_partner_id'].id,
                    })]
            }
            move = self.env['account.move'].create(values)
            move._inverse_amount_total()
            self._add_driver_recoverable_payment(move)

            rate = rec.currency_id._convert(
                rec.shortage_rate, rec.company_id.fleet_currency_id, rec.company_id, fields.Date.today())
            self.env['fleet.driver.recoverable'].create({
                'driver_id': rec.driver_id.id,
                'date': rec.date,
                'trip_id': rec.id,
                'move_id': move.id,
                'name': f'{rec.name} | {rec.product_id.name}',
                'amount': rate * rec.short_qty
            })
            moves |= move
        return moves

    def create_prepaid_expense_vals(self):
        moves = self.env['account.move']
        for rec in self:
            lines = self.create_prepaid_expense_entry()
            if not lines:
                continue
            values = {
                'journal_id': rec.company_id.fleet_income_journal_id.id,
                'company_id': rec.company_id.id,
                'date': self.end_date,
                'move_type': 'entry',
                'state': 'draft',
                'ref': f'Prepaid Expense {rec.name}',
                'name': '/',
                'currency_id': rec.company_id.fleet_currency_id.id,
                'line_ids': lines
            }

            move = self.env['account.move'].create(values)
            move._inverse_amount_total()
            moves |= move
        return moves

    def create_prepaid_expense_entry(self):
        self.ensure_one()
        line_ids = self.env['account.move.line'].search([
            ('analytic_tag_ids', 'in', self.analytic_tag_id.ids),
            ('analytic_account_id', '=', self.truck_id.analytic_account_id.id),
            ('move_id.state', '=', 'posted'),
            ('product_id.can_be_expensed', '=', True)
        ])
        if not line_ids:
            return

        prepaid_expense_line_ids = []
        for line in line_ids:
            amount_currency = line.currency_id._convert(abs(line.amount_currency), self.company_id.fleet_currency_id, self.company_id, line.date)
            balance = self.company_id.fleet_currency_id._convert(amount_currency, self.company_id.currency_id, self.company_id, line.date)
            
            prepaid_expense_line_ids.append((0, 0, {
                'name': f'{line.name} - Prepaid',
                'debit': 0,
                'credit': abs(balance),
                'amount_currency': -abs(amount_currency),
                'currency_id': self.currency_id.id,
                'account_id': line.account_id.id,
                'analytic_tag_ids': [(4, self.analytic_tag_id.id)],
                'analytic_account_id': self.truck_id.analytic_account_id.id
            }))
            prepaid_expense_line_ids.append(
                (0, 0, {
                    'name': f'{line.name} - Prepaid',
                    'debit': abs(balance),
                    'credit': 0,
                    'amount_currency': abs(amount_currency),
                    'currency_id': self.currency_id.id,
                    'account_id': line.product_id.expense_account_id.id,
                    'analytic_tag_ids': [(4, self.analytic_tag_id.id)],
                    'analytic_account_id': self.truck_id.analytic_account_id.id
                }))
        return prepaid_expense_line_ids

    def action_finalize_trip(self):
        moves = self.env['account.move']
        for rec in self.filtered(lambda t: t.state == 'completed'):
            moves |= rec.create_invoice()
            moves |= rec.create_bill()
            moves |= rec._create_trip_shorts_recoverable_entry()
            moves |= rec.create_prepaid_expense_vals()

            rec.write({'state': 'invoiced'})
            rec.analytic_tag_id.write({'is_closed': True})
            _logger.info(f'Trip {rec.name} invoiced and closed')
        moves.filtered(lambda m: m.state == 'draft')._post()

    def action_batch_invoice_trips(self):
        if self.filtered(lambda t: t.state != 'completed'):
            raise ValidationError('Only completed trips can be invoiced!')
        if len(self.mapped('partner_id')) > 1:
            raise ValidationError(
                'Only select trips belonging to the same customer')

        # since all trips belong to the same customer we can get move details from one of the trips
        move_vals = self[0].prepare_move_vals()
        move_vals['invoice_line_ids'] = [
            (0, 0, r._prepare_invoice_line_vals()) for r in self]
        move = self.env['account.move'].create(move_vals)
        self.mapped('order_id').write({'move_ids': [(4, move.id)]})
        self.mapped('analytic_tag_id').write({'is_closed': True})
        self.create_bill()
        self.write({'state': 'invoiced'})

    def action_trip_revenue(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gross Margin',
            'res_model': 'account.analytic.line',
            'domain': [('tag_ids', 'in', self.analytic_tag_id.id)],
            'view_mode': 'tree,form',
            'target': 'current'
        }


class FleetTripSeals(models.Model):
    _name = 'fleet.trip.seal'
    _description = 'Fleet Trip Seal'

    compartment = fields.Char(string='Compartment', required=True)
    top_seal = fields.Char(string='Top Seal')
    bottom_seal = fields.Char(string='Bottom Seal')
    trip_id = fields.Many2one('fleet.trip', string='Trip', required=True)


class FleetTripDocument(models.Model):
    _name = 'fleet.trip.document'
    _description = 'Fleet Trip Document'

    trip_id = fields.Many2one('fleet.trip', string='Trip')
    document_id = fields.Many2one(
        'fleet.document.type', string='Document Name')
    document_ids = fields.Many2many('ir.attachment', string='Upload Documents')
