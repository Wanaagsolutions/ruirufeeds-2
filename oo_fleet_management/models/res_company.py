# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    fleet_income_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Fleet Income Journal",
        domain="[('company_id', '=', id), ('type', 'in', ('sale', 'general'))]",
        help='The accounting journal where fleet revenue will be registered')
    
    fleet_income_company_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Company Truck Income Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('account_type', '=', 'income')]")
    fleet_income_contractor_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Contractor Truck Income Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('account_type', '=', 'income')]")
    fleet_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Fleet Expenses Journal",
        domain="[('company_id', '=', id), ('type', 'in', ('purchase', 'general'))]",
        help='The accounting journal where fleet expenses will be registered')
    
    fleet_expense_contractor_truck_debit_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Contractor Truck Debit Expense Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('account_type', '=', 'expense')]")
    fleet_email_from= fields.Char(string="Fleet Email from")
