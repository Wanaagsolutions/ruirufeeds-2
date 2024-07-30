# -*- coding: utf-8 -*-
import logging
from odoo import service, api, models, fields


_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']

    def _get_report_base_filename(self):
        self.ensure_one()
        return f'{self.employee_id.name} - {self.name}'


class HrHoliday(models.Model):
    _inherit = 'hr.leave'

    access_token = fields.Char(string='Access Token')

    def _get_report_base_filename(self):
        self.ensure_one()
        return f'{self.employee_id.name} - {self.name}'

    def _get_template_with_type(self, notification_type):
        notification_map = {
            'create': 'oo_portal_employees.oo_leave_create_mail',
            'approve': 'oo_portal_employees.oo_leave_approve_mail',
            'refuse': 'oo_portal_employees.oo_leave_refuse_mail',
        }
        return notification_map[notification_type]

    def send_email(self, notification_type='create'):
        template = self.env.ref(self._get_template_with_type(notification_type))
        values = {
            'email_from': self.employee_id.user_id.partner_id.email,
            'email_to': self.employee_id.leave_manager_id.partner_id.email
        }
        template.send_mail(self.id,
                           force_send=True,
                           email_values=values,
                           email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature')

        _logger.info('Sent leave notification email')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.send_email()
        return res

    def action_approve(self):
        res = super().action_approve()
        for rec in self:
            rec.send_email(notification_type='approve')
        return res

    def action_refuse(self):
        res = super().action_refuse()
        for rec in self:
            rec.send_email(notification_type='refuse')
        return res
