# -*- coding: utf-8 - *-

from odoo import models, fields, api


PARTNER_TYPE = [
    ('driver', 'Driver'),
    ('supplier', 'Supplier'),
    ('subcontractor', 'SubContractor'),
    ('customer', 'Customers')
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection(string='Partner Type', selection=PARTNER_TYPE, required=True, default='customer')
    national_no = fields.Char(string='National ID')
    licence_no = fields.Char(string='Driver Licence No')
    employment_date = fields.Date(string="Employment Date")
    passport_no = fields.Char(string='Driver Passport No')
    relationship_id = fields.Many2one('partner.relationship', string='Relationship')

    driver_shorts_ids = fields.One2many('fleet.driver.shorts', 'driver_id')
    driver_shorts_payments_ids = fields.One2many('fleet.driver.payments', 'driver_id')
    driver_documents_ids = fields.One2many('fleet.driver.document', 'driver_id')
    customer_documents_ids = fields.One2many('fleet.customer.document', 'driver_id')


class FleetDriverShorts(models.Model):
    _name = 'fleet.driver.shorts'
    _description = 'Fleet Driver Shorts'

    date = fields.Date(string='Date', required=True)
    trip_id = fields.Many2one('fleet.trip', string='Trip', required=True)
    product_id = fields.Many2one('product.product', string='Cargo Load', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    price_rate = fields.Float(string='Price Rate', required=True)
    amount = fields.Float(string='Total Amount', compute='_compute_amount')
    driver_id = fields.Many2one('res.partner', string='Driver')
    amount = fields.Char(compute='_compute_amount', string='amount')

    @api.depends('price_rate', 'quantity')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.quantity * rec.price_rate


class FleetDriverPayments(models.Model):
    _name = 'fleet.driver.payments'
    _description = 'Fleet Driver Payments'

    date = fields.Date(string='Date', required=True)
    trip_id = fields.Many2one('fleet.trip', string='Trip', required=True)
    product_id = fields.Many2one('product.prodcut', string='Product', required=True)
    amount = fields.Float(string='Amount Paid', required=True)

    driver_id = fields.Many2one('res.partner', string='Driver')


class FleetDocuments(models.Model):
    _name = 'fleet.driver.document'
    _description = 'Fleet Documents'

    name = fields.Char(string='Name', required=True)
    file = fields.Binary(string='File', required=True)
    doc_type = fields.Many2one('fleet.document.type', string='Document Type', required=True)
    expiration_date = fields.Date(string='Expiration Date')

    driver_id = fields.Many2one('res.partner', string='Driver')

class FleetCustomerDocuments(models.Model):
    _name = 'fleet.customer.document'
    _description = 'Fleet Customer Documents'

    name = fields.Char(string='Name', required=True)
    file = fields.Binary(string='File', required=True)
    doc_type = fields.Many2one('fleet.document.type', string='Document Type', required=True)
    driver_id = fields.Many2one('res.partner', string='Driver')

