# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fleet_income_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.fleet_income_journal_id', readonly=False,
        string="Fleet Income Journal",
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ('sale', 'general'))]",
        help='The accounting journal where fleet revenue will be registered')
    
    fleet_income_company_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.fleet_income_company_truck_account_id",
        string="Company Truck Income Account",
        readonly=False,
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('account_type', '=', 'income')]")
    fleet_income_contractor_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.fleet_income_contractor_truck_account_id",
        string="Contractor Truck Income Account",
        readonly=False,
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('account_type', '=', 'income')]")
    fleet_email_from = fields.Char(string="Fleet Email from", related="company_id.fleet_email_from", readonly=False)
    fleet_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        related='company_id.fleet_expense_journal_id',
        readonly=False,
        string="Fleet Expenses Journal",
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ('purchase', 'general'))]",
        help='The accounting journal where fleet expenses will be registered')
    
    fleet_expense_contractor_truck_debit_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.fleet_expense_contractor_truck_debit_account_id",
        string="Contractor Truck Debit Expense Account",
        readonly=False,
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('account_type', '=', 'expense   ')]")
    
    @api.onchange('fleet_expense_journal_id')
    def _onchange_fleet_expense_journal_id(self):
        self.fleet_expense_contractor_truck_debit_account_id = self.fleet_expense_journal_id.default_account_id

    @api.onchange('fleet_income_journal_id')
    def _onchange_fleet_income_journal_id(self):
        self.fleet_income_company_truck_account_id = self.fleet_income_journal_id.default_account_id
        self.fleet_income_contractor_truck_account_id = self.fleet_income_journal_id.default_account_id