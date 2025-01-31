# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
from collections import OrderedDict
from odoo import fields, http, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.http import request, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR
from pprint import pprint
import logging




_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    @http.route(['/approve/expense/<int:id>'], type='http', auth="public", website=True)
    def approve_expense_form(self, id, **kw):
        values = {
            'user': request.env.user
        }
        observacion = ''
        rec = http.request.env['hr.expense'].sudo().browse(id)

        if rec:
            if any(expense.state != 'draft' or expense.sheet_id for expense in rec):
                observacion = "¡You cannot report the same line twice!"
            elif len(rec.mapped('employee_id')) != 1:
                observacion = "You cannot report expenses for different employees on the same report."
            else:
                # rec = rec.filtered(lambda x: x.payment_mode == 'own_account') or rec.filtered(
                #     lambda x: x.payment_mode == 'company_account')

                expense_sheet_val = {
                    'name': rec.name,
                    'employee_id': rec.employee_id and rec.employee_id.id or False,
                    'user_id': rec.employee_id.expense_manager_id and rec.employee_id.expense_manager_id.id or False,
                    'message_main_attachment_id': rec.message_main_attachment_id and rec.message_main_attachment_id.id or False,
                    'expense_line_ids': [(4, rec.id)] or False,
                }

                expense_sheet = http.request.env['hr.expense.sheet'].sudo().create(expense_sheet_val)
                expense_sheet.action_submit_sheet()
                expense_sheet.approve_expense_sheets()
                observacion = "Everything in order with this expense and Report Created and Sent"

                # [(4, self.id)] or False,

        values.update({
            'msg': observacion
        })

        return request.render("portal_user_expense_submit.approve_expense", values)

    @http.route(['/update/expense/<int:id>'], type='http', auth="public", website=True)
    def update_expense_form(self, id, **kw):
        rec = http.request.env['hr.expense'].sudo().browse(id)

        values = {
            'id': rec.id,
            'commentary': rec.commentary,
            'error': {},
            'error_message': [],
        }

        return request.render("portal_user_expense_submit.update_expense", values)

    @http.route(['/update/expense/submit'], type='http', auth="public", website=True)
    def update_expense_process(self, **POST):

        #We look for the record
        rec = http.request.env['hr.expense'].sudo().browse(POST['id'])

        #We update Values
        rec.commentary = POST['commentary']

        values = {
            'user': request.env.user,
            'msg': 'Your Comment has been entered.',
        }

        return request.render("portal_user_expense_submit.approve_expense", values)
      
    @http.route(['/expense/expense_sheet_form/<int:order>'], type='http', auth="public", website=True)
    def my_sheet_expense(self, order):
        values = {}
        expense_sheet_data = http.request.env['hr.expense.sheet'].sudo().search([])
        expense_sheet_form=expense_sheet_data.browse(order)
        values.update({
            'page_name': 'form_expense',
            'expense_sheet_form':expense_sheet_form
        })

        return http.request.render('portal_user_expense_submit.expences_sheet_form_view', values)
