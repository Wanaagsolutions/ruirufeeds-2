# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


PARTNER_TYPE = [
    ('supplier', 'Supplier'),
    ('subcontractor', 'SubContractor'),
    ('customer', 'Customers')
]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection(string='Partner Type', selection=PARTNER_TYPE, required=True, default='customer')
    customer_documents_ids = fields.One2many('fleet.customer.document', 'partner_id')
    national_no = fields.Char(string='National ID')


class ResCompany(models.Model):
    _inherit = 'res.company'

    fleet_income_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Fleet Income Journal",
        domain="[('company_id', '=', id), ('type', 'in', ('sale', 'general'))]",
        help='The accounting journal where fleet revenue will be registered')
    
    fleet_income_contractor_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Contractor Truck Income Account",
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', id),\
                             ('user_type_id', 'in', %s)]" % [self.env.ref('account.data_account_type_revenue').id,
                                                             self.env.ref('account.data_account_type_other_income').id])
    fleet_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Contractor Bills Journal",
        domain="[('company_id', '=', id), ('type', 'in', ('purchase', 'general'))]",
        help='The accounting journal where truck contractor bills will be registered')
    
    fleet_hr_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Fleet Truck Expenses Journal",
        domain="[('company_id', '=', id), ('type', 'in', ('cash', 'bank', 'purchase'))]",
        help='The accounting journal where fleet truck hr expenses will be registered')
    
    fleet_contractor_shorts_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Fleet Contractor Shorts Journal",
        domain="[('company_id', '=', id), ('type', 'in', ('cash', 'bank', 'purchase'))]",
        help='The accounting journal where fleet contractor truck shorts will be registered')
        
    fleet_expense_contractor_truck_debit_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Contractor Truck Debit Expense Account",
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', id),\
                             ('user_type_id', '=', %s)]" % self.env.ref('account.data_account_type_expenses').id)

    fleet_driver_recoverable_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Company Truck Shorts Debit Account",
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', id)]")
    
    fleet_email_from= fields.Char(string="Fleet Email From")
    fleet_currency_id = fields.Many2one('res.currency', string='Fleet Currency', default=lambda self: self.currency_id.id)
    fleet_expense_partner_id = fields.Many2one('res.partner', string='Expenses Vendor')
    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fleet_income_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.fleet_income_journal_id', readonly=False,
        string="Fleet Income Journal",
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ('sale', 'general'))]",
        help='The accounting journal where fleet revenue will be registered')
    
    fleet_income_contractor_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.fleet_income_contractor_truck_account_id",
        string="Contractor Truck Income Account",
        readonly=False,
        required=True,
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', company_id),\
                             ('user_type_id', 'in', %s)]" % [self.env.ref('account.data_account_type_revenue').id,
                                                             self.env.ref('account.data_account_type_other_income').id])
    
    fleet_email_from = fields.Char(string="Fleet Email From", related="company_id.fleet_email_from", readonly=False)
    
    fleet_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.fleet_expense_journal_id',
        readonly=False,
        string="Fleet Contractor Bills Journal",
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ('purchase', 'general'))]",
        help='The accounting journal where fleet contractor bills will be registered')
    
    fleet_hr_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.fleet_hr_expense_journal_id',
        readonly=False,
        string="Fleet Truck Expenses Journal",
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ('cash', 'bank', 'purchase'))]",
        help='The accounting journal where fleet truck hr expenses will be registered')

    fleet_contractor_shorts_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Fleet Contractor Shorts Journal",
        related="company_id.fleet_contractor_shorts_journal_id",
        readonly=False,
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ('sale', 'general'))]",
        help='The accounting journal where fleet contractor shorts will be registered')
    
    fleet_expense_contractor_truck_debit_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.fleet_expense_contractor_truck_debit_account_id",
        string="Contractor Truck Debit Expense Account",
        readonly=False,
        required=True,
        help="Debit account for contractor truck expenses",
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', company_id),\
                             ('user_type_id', '=', %s)]" % self.env.ref('account.data_account_type_expenses').id)

    fleet_driver_recoverable_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.fleet_driver_recoverable_account_id",
        string="Company Truck Shorts Debit Account",
        readonly=False,
        required=True,
        help="Debit account for company truck shorts",
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', company_id)]")
    
    fleet_currency_id = fields.Many2one('res.currency',
                                                 string='Fleet Currency', 
                                                 readonly=False,
                                                 required=True,
                                                 related="company_id.fleet_currency_id")
    fleet_expense_partner_id = fields.Many2one('res.partner',
                                               string='Expenses Vendor', 
                                               readonly=False,
                                               required=True,
                                               related="company_id.fleet_expense_partner_id")
