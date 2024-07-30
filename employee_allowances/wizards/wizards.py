from odoo import models, fields


class FineAllocation(models.TransientModel):
    _name = 'fine.allocation'
    _description = 'Fines Allocation'

    '''
    When confirming a payslip, the fine records associated to that employees payslip are deleted.
    For inheritance issues, that functionality is implemented in hr_ke module under hr_payroll,
    a function called action_payslip_done().
    '''

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    fine_amount = fields.Float(string='Amount')
    deduction_id = fields.Many2one(
        'ke.deductions.type', string='Deduction Type', required=True)
    rule_id = fields.Many2one(
        related='deduction_id.rule_id', string="Salary Rule")

    def action_allocate_fine(self):
        record = self.env['ke.batch.deduction'].browse(
            self._context.get('active_ids', []))
        record.deduction_ids = [(5, 0, 0)]

        for rec in self.employee_ids:
            vals = {
                'deduction_type_id': self.deduction_id.id,
                'amount': rec.fine_amount,
                'employee_id': rec.id,
                'deduction_id': record.id
            }

            self.env['ke.batch.deduction.ids'].sudo().create(vals)
            rec.fine_amount = 0


class HrOvertime(models.TransientModel):
    _name = 'overtime.allocation'
    _description = 'Overtime Allocation'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    overtime_hours = fields.Float(string='OVertime Hours', digits=(12, 1))
    contract_id = fields.Many2one(
        'hr.contract', string='Contract', related='employee_ids.contract_id')

    def action_allocate_overtime(self):
        # get the id of the current open record
        overtime_record = self.env['ke.overtime'].browse(
            self._context.get('active_ids', []))

        # for everytime this action is called, clear the employee_list_ids lines to avoid duplication
        overtime_record.employee_list_ids = [(5, 0, 0)]

        # create values and append them to the lines for each employee
        for employee in self.employee_ids:
            vals = {
                'Emp_name': employee.id,
                'contract_id': employee.contract_id.id,
                'worked_hours': employee.overtime_hours
            }
            overtime_record.employee_list_ids = [(0, 0, vals)]
            employee.overtime_hours = 0


class HrBonusAndCommission(models.TransientModel):
    _name = 'bonus.allocation'
    _description = 'Bonus and Commission allocation in batch for employees'

    '''We use relation to contracts, since this operation should only be possible to employees with a contract.'''

    contract_ids = fields.Many2many('hr.contract', string='Employee Contract')

    cash_allowance_id = fields.Many2one(
        'ke.cash.allowances.type', string='Allowance Type', required=True)
    rule_id = fields.Many2one(
        related='cash_allowance_id.rule_id', string="Salary Rule")

    allowance_amount = fields.Float(string='Amount', default=0.0)

    def action_allocate_bonus(self):
        for rec in self.contract_ids:
            vals = {
                'contract_id': rec.id,
                'company_id': rec.company_id.id,
                'cash_allowance_id': self.cash_allowance_id.id,
                'computation': 'fixed',
                'fixed': rec.allowance_amount,
            }
            self.env['ke.cash_allowances'].sudo().create(vals)
            rec.allowance_amount = 0
