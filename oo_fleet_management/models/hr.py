# -*- coding: utf-8 - *-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    national_no = fields.Char(string='National ID')
    is_driver = fields.Boolean("Is Driver")
    licence_no = fields.Char(string='Driver Licence No')
    employment_date = fields.Date(string="Employment Date")
    passport_no = fields.Char(string='Driver Passport No')
    relationship_id = fields.Many2one(
        'partner.relationship', string='Relationship')
    driver_recoverable_ids = fields.One2many(
        'fleet.driver.recoverable', 'driver_id')
    driver_documents_ids = fields.One2many(
        'fleet.driver.document', 'driver_id')
    driver_next_of_kin_ids = fields.One2many('fleet.driver.kins', 'driver_id')


class FleetDriverRecoverables(models.Model):
    _name = 'fleet.driver.recoverable'
    _description = 'Fleet Driver Recoverables'

    date = fields.Date(string='Date', required=True)
    driver_id = fields.Many2one('hr.employee', string='Driver')
    company_id = fields.Many2one(
        related='driver_id.company_id', string='Company')
    currency_id = fields.Many2one(
        related='company_id.fleet_currency_id', string='Currency')
    amount = fields.Monetary(string='Total Amount',
                             currency_field='currency_id')
    trip_id = fields.Many2one('fleet.trip', string='Trip')
    move_id = fields.Many2one('account.move', string="Related Journal")
    charge_id = fields.Many2one('fleet.charge.sheet', string='Charge Sheet')
    expense_id = fields.Many2one('hr.expense', string='Related Expense')
    name = fields.Char(string='Description', required=True)


class FleetDocuments(models.Model):
    _name = 'fleet.driver.document'
    _description = 'Fleet Documents'

    name = fields.Char(string='Name', required=True)
    file = fields.Binary(string='File', required=True)
    doc_type = fields.Many2one(
        'fleet.document.type', string='Document Type', required=True)
    expiration_date = fields.Date(string='Expiration Date')
    driver_id = fields.Many2one('hr.employee', string='Driver')


class FleetCustomerDocuments(models.Model):
    _name = 'fleet.customer.document'
    _description = 'Fleet Customer Documents'

    name = fields.Char(string='Name', required=True)
    file = fields.Binary(string='File', required=True)
    doc_type = fields.Many2one(
        'fleet.document.type', string='Document Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')


class FleetDriverKins(models.Model):
    _name = 'fleet.driver.kins'
    _description = 'Fleet Driver Next of Kins'

    name = fields.Char(string='Name', required=True)
    national_no = fields.Char(string='National ID')
    phone = fields.Char(string='Phone Number')
    relationship_id = fields.Many2one(
        'partner.relationship', string='Relationship')
    driver_id = fields.Many2one('hr.employee', string='Driver')


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    truck_id = fields.Many2one(
        related='analytic_account_id.truck_id', string='Truck')
    short_recoverable = fields.Float(string='Short Recoverable')
    has_driver_recoverable = fields.Boolean(
        string='Has Driver Recoverable', compute='_compute_has_driver_recoverable')
    driver_recoverable_balance = fields.Float(
        string='Driver Recoverable Balance')

    @api.onchange('truck_id', 'analytic_tag_ids', 'currency_id')
    def _onchange_truck_id(self):
        for rec in self:
            rec.employee_id = rec.analytic_tag_ids and rec.analytic_tag_ids[
                0].trip_id.driver_id or rec.truck_id.driver_id.id
            amount = sum(
                rec.employee_id.driver_recoverable_ids.mapped('amount'))
            amount = rec.company_id.fleet_currency_id._convert(
                amount, rec.currency_id, rec.company_id, rec.date)
            rec.driver_recoverable_balance = amount

    @api.depends('product_id', 'product_id.has_driver_recoverable', 'analytic_account_id')
    def _compute_has_driver_recoverable(self):
        for rec in self:
            if rec.analytic_account_id.truck_id.ownership == 'company' and rec.product_id.has_driver_recoverable:
                rec.has_driver_recoverable = True
            else:
                rec.has_driver_recoverable = False

    @api.onchange('product_id', 'analytic_account_id', 'truck_id')
    def _onchange_analytic_product_id(self):
        for rec in self:
            if rec.truck_id.ownership == 'company':
                rec.account_id = rec.product_id.expense_account_id
            else:
                rec.account_id = rec.product_id.contractor_expense_account_id

    def _get_expense_account_source(self):
        if self.truck_id:
            if self.truck_id.ownership == 'company':
                return self.product_id.fleet_prepaid_account_expense_id
            else:
                partner_id = self.truck_id.supplier_id
                account_src = partner_id.property_account_payable_id or partner_id.parent_id.property_account_payable_id
                return account_src
        else:
            return super()._get_expense_account_source()

    def _get_expense_account_destination(self):
        if self.truck_id:
            vendor = self.company_id.fleet_expense_partner_id
            return vendor.property_account_payable_id.id or vendor.parent_id.property_account_payable_id.id
        else:
            return super()._get_expense_account_destination()

    def _prepare_driver_recoverable_move(self, company_currency, date, name, partner=False):
        if self.short_recoverable:
            taxes = self.tax_ids.with_context(round=True).compute_all(
                self.short_recoverable, self.currency_id)
            balance = self.currency_id._convert(
                taxes['total_excluded'], company_currency, self.company_id, date)
            amount_currency = taxes['total_excluded']
            src_account = self.company_id.fleet_driver_recoverable_account_id
            recoverable_move = {
                'name': name,
                'debit': balance < 0 and -balance,
                'credit': balance > 0 and balance,
                'account_id': src_account.id,
                'date_maturity': date,
                'amount_currency': -amount_currency,
                'currency_id': self.currency_id.id,
                'expense_id': self.id,
                'partner_id': partner,
                'exclude_from_invoice_tab': True,
            }
            return recoverable_move

    def _add_driver_recoverable_payment(self):
        self.env['fleet.driver.recoverable'].create({
            'driver_id': self.employee_id.id,
            'date': self.date,
            'name': self.name,
            'expense_id': self.id,
            'amount': -self.currency_id._convert(
                self.short_recoverable, self.company_id.fleet_currency_id, self.company_id, self.date)
        })

    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + \
                ': ' + expense.name.split('\n')[0][:64]
            partner_id = self.company_id.fleet_expense_partner_id.id

            if expense.truck_id:
                move_line_name = f'{expense.truck_id.name}: {expense.product_id.name}'

            if expense.truck_id.ownership == 'contractor':
                partner_id = expense.truck_id.supplier_id
                partner_id = partner_id.id

            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()

            account_date = expense.date or expense.sheet_id.accounting_date or fields.Date.context_today(
                expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            unit_amount = expense.unit_amount or expense.total_amount
            quantity = expense.quantity if expense.unit_amount else 1
            taxes = expense.tax_ids.with_context(round=True).compute_all(
                unit_amount, expense.currency_id, quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0

            # source move line
            balance = expense.currency_id._convert(
                taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(
                    tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(
                        tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(
                        tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(
                        base_amount, company_currency, expense.company_id, account_date)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
                'exclude_from_invoice_tab': True,
            }
            recoverable_shorts_move = self._prepare_driver_recoverable_move(
                company_currency, account_date, move_line_name)
            if recoverable_shorts_move:
                move_line_dst['debit'] -= recoverable_shorts_move['debit']
                move_line_dst['credit'] -= recoverable_shorts_move['credit']
                move_line_dst['amount_currency'] -= recoverable_shorts_move['amount_currency']
                move_line_values.append(recoverable_shorts_move)
            move_line_values.append(move_line_dst)
            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense

    def action_move_create(self):
        res = super().action_move_create()
        for rec in self.filtered('short_recoverable'):
            rec._add_driver_recoverable_payment()
        return res

    def action_submit_expenses(self):
        for rec in self:
            if rec.short_recoverable > abs(rec.driver_recoverable_balance) or rec.short_recoverable < 0:
                raise ValidationError(
                    'Shorts Recoverable cannot be greater than total driver short balance!')
        return super().action_submit_expenses()


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        company = self.env['res.company'].browse(
            self.default_get(['company_id'])['company_id'])
        return company.fleet_hr_expense_journal_id.id

    @api.model
    def _default_bank_journal_id(self):
        company = self.env['res.company'].browse(
            self.default_get(['company_id'])['company_id'])
        return company.fleet_hr_expense_journal_id.id

    journal_id = fields.Many2one('account.journal',
                                 string='Expense Journal',
                                 states={'done': [('readonly', True)], 'post': [('readonly', True)]},
                                 check_company=True,
                                 domain="[('type', 'in', ['cash', 'bank', 'purchase']), ('company_id', '=', company_id)]",
                                 default=_default_journal_id,
                                 help="The journal used when the expense is done.")
    bank_journal_id = fields.Many2one('account.journal',
                                      string='Bank Journal',
                                      states={'done': [('readonly', True)], 'post': [('readonly', True)]},
                                      check_company=True, domain="[('type', 'in', ['cash', 'bank', 'purchase']), ('company_id', '=', company_id)]",
                                      default=_default_bank_journal_id,
                                      help="The payment method used when the expense is paid by the company.")
