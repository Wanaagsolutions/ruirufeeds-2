# -*- coding: utf-8 - *-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


TRUCK_OWNERSHIP = [('company', 'Company Owned'), ('contractor', 'Contractor Owned')]
TRUCK_TYPES = [('horse', 'Horse'), ('trailer', 'Trailer'), ('tanker', 'Tanker')]


class FleetTruck(models.Model):
    _name = 'fleet.truck'
    _description = 'Fleet Trucks'

    name = fields.Char(string='Reg No', required=True, index=True)
    supplier_id = fields.Many2one('res.partner', string='Owned By', required=True,
                                  domain=[('partner_type', '=', 'supplier')])
    driver_id = fields.Many2one('hr.employee', string='Driver', required=False,
                                domain=[('is_driver', '=', True)])
    active = fields.Boolean(string='Active', default=True)
    make = fields.Char(string="Make", required=True)
    model = fields.Char(string="Model", required=True)
    manufacture_year = fields.Char(string='Manufacture Year', required=True)
    logbook_no = fields.Char(string='Log Book No', required=True)
    engine_no = fields.Char(string='Engine No')
    engine_cc = fields.Char(string='Engine CC')
    chasis_no = fields.Char(string='Chasis No', required=True)
    wheel_no = fields.Integer(string='Wheels No', required=True)
    load_capacity = fields.Float(string='Load Capacity')
    load_uom_id = fields.Many2one('uom.uom', string='Load UOM')
    main_tank_capacity = fields.Float(string='Main Tank Capacity')
    safari_tank_capacity = fields.Float(string='Safari Tank Capacity')
    mileage = fields.Integer(string='Mileage')
    ownership = fields.Selection(string='Ownership', selection=TRUCK_OWNERSHIP, required=True)
    truck_type = fields.Selection(string='Truck Type', selection=TRUCK_TYPES, required=True)
    home_location = fields.Char(string='Home Location')
    gearbox_type = fields.Char(string='Gear Box Type')
    purchase_date = fields.Date(string='Purchase Date')
    reg_date = fields.Date(string='Registration Date')
    target_km = fields.Float(string='Target Monthly Kilometers')
    max_tonnage = fields.Float(string='Truck Max Tonnage')
    service_after_km = fields.Float(string='Service After Kilometers')
    truck_model = fields.Char(string='Model')
    state = fields.Selection(string='Truck Status',
                             selection=[('nominated', 'Nominated'),
                                        ('available', 'Available'),
                                        ('in_active', 'In Active'),
                                        ('in_trip', 'In Trip')],
                             default='available')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', copy=False, readonly=True)
   # parent_id = fields.Many2one(comodel_name='fleet.truck', string='Parent Horse',
                                #domain=[('truck_type', '=', 'horse')])#
    total_compartments = fields.Integer(string='Total Compartment')
    truck_documents_ids = fields.One2many('fleet.truck.document', 'truck_id', string='Truck Documents')
    company_id = fields.Many2one('res.company', string='Company')
    
    @api.constrains('name')
    def _constrains_name(self):
        for rec in self:
            if self.search([('name', '=', rec.name), ('id', '!=', rec.id)]):
                raise ValidationError(f'Truck with Reg No {rec.name} already exists!')
    
    @api.onchange('ownership', 'company_id')
    def _onchange_ownership(self):
        for rec in self:
            rec.supplier_id = False
            if rec.ownership == 'company':
                rec.supplier_id = rec.company_id.partner_id or self.env.company.partner_id

    @api.constrains('truck_type')
    def _constrains_truck_type(self):
        for rec in self:
            if rec.truck_type == 'horse':
                rec.parent_id = rec.id

    def action_analytic_account(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analytic Account',
            'res_id': self.analytic_account_id.id,
            'res_model': 'account.analytic.account',
            'domain': [('id', '=', self.analytic_account_id.id)],
            'view_mode': 'form',
            'target': 'current'
        }
    
    def update_status(self, status):
        to_update = self.env['fleet.truck']
        for rec in self:
            to_update |= self.search([('parent_id', '=', rec.id)])
        to_update.write({'state': status})
    
    def update_mileage(self, mileage):
        to_update = self.env['fleet.truck']
        for rec in self:
            to_update |= self.search([('parent_id', '=', rec.id)])
        to_update.write({'mileage': mileage})

    def make_available(self):
        self.update_status('available')
        

class FleetTruckDocuments(models.Model):
    _name = 'fleet.truck.document'
    _description = 'Fleet Truck Documents'

    truck_id = fields.Many2one('fleet.truck', string='Main Truck', domain=[('truck_type', '=', 'horse')])
    name = fields.Char(string='Name', required=True)
    file = fields.Binary(string='File', required=True)
    doc_type = fields.Many2one('fleet.document.type', string='Document Type', required=True)
    expiration_date = fields.Date(string='Expiration Date')
