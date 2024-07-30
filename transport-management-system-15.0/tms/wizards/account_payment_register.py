# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=super-with-arguments

from odoo import api, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        active_model = self._context.get('active_model')
        if active_model in ['tms.advance', 'tms.expense', 'tms.expense.loan']:
            records = self.env[active_model].browse(self._context.get('active_ids'))
            context = {
                'active_model': 'account.move',
                'active_ids': records.mapped('move_id').ids,
            }
            self = self.with_context(**context)
        return super(AccountPaymentRegister, self).default_get(fields_list)

    def get_context(self, records):
        return {
            'active_model': 'account.move',
            'active_ids': records.mapped('move_id').ids,
        }

    def _create_payments(self):
        active_model = self._context.get('active_model')
        change_context = False
        if active_model in ['tms.advance', 'tms.expense', 'tms.expense.loan']:
            change_context = True
            records = self.env[active_model].browse(self._context.get('active_ids'))
            context = {
                'active_model': 'account.move',
                'active_ids': records.mapped('move_id').ids,
            }
            self = self.with_context(**context)
        payments = super(AccountPaymentRegister, self)._create_payments()
        if not change_context:
            return payments
        for payment in payments:
            move = payment.line_ids.mapped(
                'full_reconcile_id.reconciled_line_ids.move_id').filtered(
                lambda m: m.journal_id.type not in ['bank', 'cash'])
            record = records.filtered(lambda l: l.move_id.id == move.id)
            record.write({
                'payment_move_id': payment.move_id.id,
                'payment_id': payment.id,
            })
        return payments
