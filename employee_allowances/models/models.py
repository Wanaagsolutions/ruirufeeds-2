from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def clear_amount(self):
        for rec in self:
            rec.overtime_hours = 0
            rec.fine_amount = 0

    fine_amount = fields.Float(string='Amount')
    deduction_id = fields.Many2one(
        'ke.deductions.type', string='Deduction Type')
    rule_id = fields.Many2one(
        related='deduction_id.rule_id', string="Salary Rule")
    overtime_hours = fields.Float(string='Overtime Hours')
    contract_id = fields.Many2one('hr.contract', string='Contract')

    bank_id = fields.Many2one(
        'res.bank', string='Bank', related='bank_account_id.bank_id')
    acc_number = fields.Char(string='Account Number')
    partner_id = fields.Many2one(
        'res.partner', string='Account Holder', related='bank_account_id.partner_id')
    acc_holder_name = fields.Char(
        string='Account Holder Name', related='bank_account_id.acc_holder_name')
    bank_currency_id = fields.Many2one(
        'res.currency', string='Bank Currency', related='bank_account_id.currency_id')


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def clear_amount(self):
        for rec in self:
            rec.allowance_amount = 0

    cash_allowance_id = fields.Many2one(
        'ke.cash.allowances.type', string='Allowance Type')
    allowance_amount = fields.Float(string='Amount')

    rule_id = fields.Many2one(string='Salary Rule',
                              related='cash_allowance_id.rule_id')

    @api.model
    def contract_expiry(self):
        expiry_date = datetime.now().date() + timedelta(days=14)
        contracts = self.env['hr.contract'].search([('state', '=', 'open'), ('date_end', '=', expiry_date)])

        for contract in contracts:
            mail_content = "Hello  " + contract.employee_id.parent_id.name + ",<br>Your employee " + \
                contract.employee_id.name + \
                "contract is going to expire in 14 Days. Please review it and possibly renew."

            main_content = {
                'subject': _('%s Contract Expiry') % (contract.employee_id.name),
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': contract.employee_id.parent_id.work_email,
            }
            self.env['mail.mail'].create(main_content).send()


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super().action_payslip_done()

        for record in self:
            deductions = self.env['ke.deductions'].search(
                [('employee_id', '=', record.employee_id.id)]).filtered(lambda r: not r.deduction_id.is_recurring)

            allowances = self.env['ke.cash_allowances'].search(
                [('contract_id', '=', record.contract_id.id)]).filtered(lambda r: not r.cash_allowance_id.is_recurring)

            if deductions:
                deductions.unlink()
            if allowances:
                allowances.unlink()

            record.write({'state': 'done'})
        return res


class KeCashAllowanceType(models.Model):
    _inherit = 'ke.cash.allowances.type'

    is_recurring = fields.Boolean(
        string='Recurring Allowance', help='This type of allowance is recurrent every month.')


class KeDeductionType(models.Model):
    _inherit = 'ke.deductions.type'

    is_recurring = fields.Boolean(
        string='Recurring Deduction', help='This type of deduction is recurrent every month.')


class KeBatchDeduction(models.Model):
    _name = 'ke.batch.deduction'
    _description = 'Batch Deduction Allocation'

    def action_confirm_deductions(self):
        for rec in self:
            if not rec.deduction_ids:
                raise ValidationError(
                    'You must have atleast one employee selected to continue with this operation!')
            for line in rec.deduction_ids:
                vals = {
                    'deduction_id': line.deduction_type_id.id,
                    'computation': 'fixed',
                    'fixed': line.amount,
                    'employee_id': line.employee_id.id,
                }
                self.env['ke.deductions'].sudo().create(vals)
            rec.write({'state': 'confirm'})

    name = fields.Char(string='Brief Title', required=True)
    note = fields.Text(string='Note')
    date = fields.Date(string='Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')
    deduction_ids = fields.One2many(
        'ke.batch.deduction.ids', 'deduction_id', string='Deduction Ids')
    details = fields.Html(string='Details')


class KeBatchDeductionIds(models.Model):
    _name = 'ke.batch.deduction.ids'
    _description = 'Batch Deduction Ids'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True)
    deduction_type_id = fields.Many2one(
        'ke.deductions.type', string='Deduction Type', required=True)
    rule_id = fields.Many2one(
        related='deduction_type_id.rule_id', string="Salary Rule")
    amount = fields.Float(string='Amount')
    deduction_id = fields.Many2one('ke.batch.deduction', string='Deduction Id')
