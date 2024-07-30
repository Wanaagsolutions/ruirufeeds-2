# -*- coding: utf-8 - *-

from odoo import fields, models
from odoo.addons.account.models.product import ACCOUNT_DOMAIN

TRUCK_TYPES = [("trailer", "Trailer"), ("tanker", "Tanker")]
EXPENSE_TYPES = [("mileage", "Mileage"), ("fuel", "Fuel"), ("toll", "Toll"), ("repair", "Repairs"), ("other", "Other")]


class ProductCategory(models.Model):
    _inherit = "product.category"


    property_contractor_account_expense_categ_id = fields.Many2one('account.account', company_dependent=True,
        string="Contractor Expense Account",
        domain=ACCOUNT_DOMAIN,
        help="The expense is accounted for when a vendor bill is validated, except in anglo-saxon accounting with perpetual inventory valuation in which case the expense (Cost of Goods Sold account) is recognized at the customer invoice validation.")
    
    fleet_prepaid_account_expense_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Fleet Prepaid Expense Account",
        help="Keep this field empty to use the default value from the product category. If anglo-saxon accounting with automated valuation method is configured, the expense account on the product category will be used.",
    )



class ProductTemplate(models.Model):
    _inherit = "product.template"

    expected_short_rate = fields.Float(string="Expected Short Rate")
    is_fleet_product = fields.Boolean(string="Fleet Product")
    truck_type = fields.Selection(string="Truck Type", selection=TRUCK_TYPES)
    allowed_shortage = fields.Float(string="Allowed Shortage in %")
    property_contractor_account_expense_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Contractor Expense Account",
        domain=ACCOUNT_DOMAIN,
        help="Keep this field empty to use the default value from the product category. If anglo-saxon accounting with automated valuation method is configured, the expense account on the product category will be used.",
    )
    has_driver_recoverable = fields.Boolean(string='Driver Recoverable')
    fleet_prepaid_account_expense_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Fleet Prepaid Expense Account",
        help="Keep this field empty to use the default value from the product category. If anglo-saxon accounting with automated valuation method is configured, the expense account on the product category will be used.",
    )
    expense_type = fields.Selection(string='Expense Type', selection=EXPENSE_TYPES, default='other')
    

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    @property
    def contractor_expense_account_id(self):
        return self.property_contractor_account_expense_id or self.categ_id.property_contractor_account_expense_categ_id

    @property
    def expense_account_id(self):
        return self.property_account_expense_id or self.categ_id.property_account_expense_categ_id
    
    @property
    def fleet_prepaid_account_expense_id(self):
        return self.fleet_prepaid_account_expense_id or self.categ_id.fleet_prepaid_account_expense_id



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    truck_id = fields.Many2one(related='account_analytic_id.truck_id', string='Truck')
    

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move=move)
        account_id = self.product_id.expense_account_id
        if self.account_analytic_id and self.account_analytic_id.truck_id.ownership == 'contractor':
            account_id = self.product_id.contractor_expense_account_id
        res['account_id'] = account_id.id
        return res
