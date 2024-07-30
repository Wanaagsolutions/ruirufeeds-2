# -*- coding: utf-8 - *-

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

TRUCK_TYPES = [('company', 'Company Owned'), ('contractor', 'Contractor Owned')]
TRUCK_OWNERSHIP = [('company', 'Company Owned'), ('contractor', 'Contractor Owned')]


class FleetOrder(models.Model):
    _name = 'fleet.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _description = 'Fleet Orders'

    name = fields.Char(string='Name', default='', copy=False, tracking=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True,
                                 domain="[('partner_type', '=', 'customer'), ('company_id', 'in', (company_id, False))]",
                                 tracking=True, index=True)
    product_id = fields.Many2one('product.product', string='Cargo', required=True,
                                 domain="[('is_fleet_product', '=', True), ('company_id', 'in', (company_id, False))]",
                                 tracking=True, index=True)
    product_uom_id = fields.Many2one('uom.uom', string='Uom', required=True, tracking=True)
    transaction_uom_id = fields.Many2one('uom.uom', string='Transaction Uom', 
                                         required=True, tracking=True)
    ar_rate = fields.Monetary(string='AR Rate', currency_field='currency_id', required=True, tracking=True)
    shortage_rate = fields.Monetary(string='Shortage Rate', currency_field='currency_id', required=True, tracking=True)
    quantity = fields.Float(string='Quantity', tracking=True)
    transactional_quantity = fields.Float(string='Converted Quantity', compute='_compute_transactional_quantity')
    date = fields.Date(string='Date', required=True, default=fields.Date.today(), tracking=True, index=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    cost = fields.Monetary('Total Cost', currency_field='currency_id')
    trip_ids = fields.Many2many('fleet.trip', string='Trips', copy=False)
    trip_count = fields.Integer(string='Trip Count', compute="_compute_trip_count", copy=False, tracking=True)
    move_ids = fields.Many2many('account.move', string='Order Moves', copy=False)
    invoice_count = fields.Integer(string='Invoice Count', compute="_compute_move_count")
    bills_count = fields.Integer(string='Invoice Count', compute="_compute_move_count")
    loading_location = fields.Char(string='Loading Location', required=True, tracking=True)
    loading_country_id = fields.Many2one('res.country', string='Loading Country', required=True, tracking=True)
    loading_city = fields.Char(string='Loading City', required=True, tracking=True)
    offloading_location = fields.Char(string='Offloading Location', required=True, tracking=True)
    offloading_country_id = fields.Many2one('res.country', string='Offloading Country', required=True, tracking=True)
    offloading_city = fields.Char(string='Offloading City', required=True)
    nomination_docs_ids = fields.One2many('fleet.order.nomination.docs', 'order_id',
                                          string='Nomination Docs', copy=False, tracking=True)
    state = fields.Selection(string='Status',
                             selection=[
                                 ('draft', 'Draft'),
                                 ('nomination_sent',
                                  'Nomination Docs Sent'),
                                 ('order', 'Order'),
                                 ('done', 'Done'),
                                 ('cancelled', 'Cancelled')],
                             default='draft', copy=False, tracking=True, index=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda s: s.env.company.id)
    has_new_trips = fields.Boolean(string='Has New Trips', readonly=True, copy=False)
    has_nominations = fields.Boolean(string='Has New Nominations', compute='_compute_has_new_nominations')
    customer_order_no = fields.Char(string='Customer Order No')
    
    
    @api.depends('transaction_uom_id', 'quantity', 'product_uom_id')
    def _compute_transactional_quantity(self):
        for rec in self:
            converted = rec.product_uom_id._compute_quantity(
                qty=rec.quantity, to_unit=rec.transaction_uom_id, raise_if_failure=False)
            rec.transactional_quantity = converted or rec.quantity

    @api.depends('nomination_docs_ids', 'nomination_docs_ids.is_nominated')
    def _compute_has_new_nominations(self):
        for rec in self:
            rec.has_nominations = not all(rec.nomination_docs_ids.mapped('is_nominated'))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_uom_id = rec.product_id.uom_id.id
            rec.transaction_uom_id = rec.product_id.uom_id.id

    @api.depends('trip_ids')
    def _compute_trip_count(self):
        for rec in self:
            rec.trip_count = len(rec.trip_ids)

    @api.depends('move_ids')
    def _compute_move_count(self):
        for rec in self:
            rec.invoice_count = len(rec.move_ids.filtered(lambda m: m.move_type == 'out_invoice'))
            rec.bills_count = len(rec.move_ids.filtered(lambda m: m.move_type == 'in_invoice'))

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.order.sequence')
        return super().create(vals)

    def _send_mail(self):
        self.ensure_one()
        template_id=self.env.ref('oo_fleet_management.fleet_email_template_nomination').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
            ctx = {
                'default_model': 'fleet.order',
                'default_res_id': self.id,
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "mail.mail_notification_paynow",
                'proforma': self.env.context.get('proforma', False),
                'force_email': True,
                'model_description': self.with_context(lang=lang).name,
            }
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }
            
    def action_send_nomination_docs(self):
        self.ensure_one()
        if not self.nomination_docs_ids:
            raise ValidationError('Please attach nominated trucks before sending.')
        nomination_docs = self.nomination_docs_ids.filtered(lambda n: not n.is_nominated)
        nomination_docs.mapped('truck_id').update_status('nominated')
        nomination_docs.write({'is_nominated': True})
        self.write({'state': 'nomination_sent', 'has_new_trips': True})
        return self._send_mail() 

    def action_reset_to_draft(self):
        for rec in self:
            rec.nomination_docs_ids.mapped('truck_id').update_status('available')
            rec.nomination_docs_ids.unlink()
            rec.write({'state': 'draft', 'has_new_trips': False})
            _logger.info(f'Reset order {rec.name} to draft')

    def action_create_trips(self):
        mandatory_docs = self.env['fleet.document.type'].search([('mandatory', '=', True), ('applicable_on', '=', 'trip')])
        for rec in self:
            trips = self.env['fleet.trip']
            for nomination in rec.nomination_docs_ids.filtered(lambda n: not n.trip_id):
                total_compartments = sum(nomination.truck_component_ids.mapped('total_compartments')) + 1
                vals = nomination._prepare_trip_values()
                vals.update({
                    'shortage_rate': rec.shortage_rate,
                    'truck_capacity': nomination.truck_capacity,
                    'start_odoometer': nomination.truck_id.mileage,
                    'trip_document_ids': [(0, 0, doc._make_default_entry()) for doc in mandatory_docs],
                    'cargo_seal_ids': [(0, 0, {'compartment': f'Compartment {i}'}) for i in range(1, total_compartments)]
                })

                _logger.info(f'Creating trips for order {rec.name} with vals: {vals}')

                trip = self.env['fleet.trip'].create(vals)
                trip.create_analytic_account_and_tags()
                # rec.nomination_docs_ids.write({'trip_id': trip.id}) # ? No idea why i had it this way
                nomination.write({'trip_id': trip.id})
                trips |= trip
            rec.write({'state': 'order', 'trip_ids': [(4, trip_id) for trip_id in trips.ids], 'has_new_trips': False})

    def action_cancel_order(self):
        for rec in self:
            trips = rec.trip_ids.filtered(lambda t: t.state not in ('draft', 'cancelled'))
            if trips:
                raise ValidationError('Please cancel all open trips before cancelling this order')
            rec.nomination_docs_ids.mapped('truck_id').update_status('available')
            rec.trip_ids.action_cancel_trip()
            rec.write({'state': 'cancelled', 'has_new_trips': False})
            _logger.info(f'Cancelled order {rec.name}')

    def action_get_trips(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trips',
            'res_model': 'fleet.trip',
            'domain': [('id', 'in', self.trip_ids.ids)],
            'view_mode': 'tree,form',
            'context': {'create': 0},
            'target': 'current'
        }
    
    def action_post_entries(self):
        for rec in self:
            moves = rec.move_ids.filtered(lambda m: m.state == 'draft')
            moves and moves.action_post()
            _logger.info(f"Posted order draft moves {moves.mapped('name')}")
            

    def action_view_moves_by_movetype(self):
        move_type = self._context.get('move_type')
        invoice_action_map = {
            'in_invoice': 'account.action_move_in_invoice_type',
            'out_invoice': 'account.action_move_out_invoice_type',
        }

        moves = self.move_ids.filtered(lambda m: m.move_type == move_type)
        action = self.env["ir.actions.actions"]._for_xml_id(f'{invoice_action_map[move_type]}')

        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        elif len(moves) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = moves.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {'default_move_type': move_type}
        if len(self) == 1:
            context.update({'default_partner_id': self.partner_id.id})
        action['context'] = context
        return action

    def action_order_revenue(self):
        self.ensure_one()
        accounts = self.trip_ids.truck_id.analytic_account_id
        tags = self.trip_ids.analytic_tag_id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order Revenue',
            'res_model': 'account.analytic.line',
            'domain': [('tag_ids', 'in', tags.ids), ('account_id', 'in', accounts.ids)],
            'view_mode': 'tree,form',
            'target': 'current'
        }

class FleetNominationDocs(models.Model):
    _name = 'fleet.order.nomination.docs'
    _description = 'Fleet Nomination docs'

    truck_id = fields.Many2one('fleet.truck', string='Truck',
                               required=True,
                               domain="[('truck_type', '=', 'horse'), ('company_id', 'in', (company_id, False))]")
    truck_component_ids = fields.Many2many('fleet.truck',
                                           string='Trailer / Tankers',
                                           required=True, 
                                           domain="[('truck_type', '!=', 'horse'), ('company_id', 'in', (company_id, False))]")
    date = fields.Date(string='Date', default=fields.Date.today(), required=True)
    driver_id = fields.Many2one('hr.employee', string='Driver', required=True, domain="[('is_driver', '=', True), ('company_id', 'in', (company_id, False))]")
    uom_id = fields.Many2one('uom.uom', string='Uom', related='order_id.transaction_uom_id')
    truck_capacity = fields.Float(string='Truck Capacity')
    order_id = fields.Many2one('fleet.order', string='Order')
    company_id = fields.Many2one(related='order_id.company_id', string='Company')
    is_nominated = fields.Boolean(string='Is Nominated', default=False)
    trip_id = fields.Many2one('fleet.trip', string='Related Trip')
    
    
    @api.onchange('truck_id')
    def _onchange_truck_id(self):
        for rec in self:
            components = self.env['fleet.truck'].search([('parent_id', '=', rec.truck_id.id), ('truck_type', '!=', 'horse')])
            rec.truck_component_ids = components and [(6, 0, components.ids)] or False
            rec.driver_id = rec.truck_id.driver_id.id

    @api.onchange('truck_id', 'truck_id.load_capacity', 'truck_component_ids')
    def _onchange_compute_truck_capacity(self):
        for rec in self:
            converted = 0   
            capacity_and_uom = rec.truck_component_ids.mapped(lambda t: (t.load_capacity, t.load_uom_id))
            for load, uom in capacity_and_uom:
                converted += uom._compute_quantity(qty=load, to_unit=rec.uom_id, raise_if_failure=False)
            rec.truck_capacity = converted

    def _prepare_trip_values(self):
        self.ensure_one()
        return {
            'name': f'{self.order_id.name} - {self.truck_id.name}',
            'order_id': self.order_id.id,
            'date': fields.Date.today(),
            'driver_id': self.driver_id.id,
            'partner_id': self.order_id.partner_id.id,
            'product_id': self.order_id.product_id.id,
            'truck_id': self.truck_id.id,
            'start_odoometer': self.truck_id.mileage,
            'truck_capacity': self.truck_capacity,
            'loaded_qty': self.truck_capacity,
        }

    def unlink(self):
        for rec in self:
            if rec.trip_id and rec.trip_id.status != 'cancelled':
                raise ValidationError('Cannot delete a nomination with an active trip. Delete/Archive the trip first!')
            rec.truck_id.update_status('available')
        return super().unlink()
    