
from odoo import models


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'


    def expense_into_trip(self, expense_line):
        for tag in expense_line.analytic_tag_ids:
            trip  = self.env['fleet.trip'].search([('analytic_tag_id', '=', tag.id)], limit=1)
            if not trip:
                continue
            trip.write({'expense_ids': [(0, 0, {
                'name': expense_line.name,
                'currency_id': expense_line.currency_id.id,
                'amount': expense_line.total_amount,
                'hr_expense_id': expense_line.id
            })]})
    
    def action_sheet_move_create(self):
        res = super().action_sheet_move_create()
        for rec in self:
            for line in rec.expense_line_ids.filtered('analytic_account_id'):
                self.expense_into_trip(line)
        return res
    
    def action_unpost(self):
        res = super().action_unpost()
        to_delete = self.env['fleet.trip.expense']
        for rec in self:
            for line in rec.expense_line_ids.filtered('analytic_account_id'):
                trip_expense = self.env['fleet.trip.expense'].search([('hr_expense_id', '=', line.id)])
                to_delete |= trip_expense
        to_delete and to_delete.unlink()
        return res