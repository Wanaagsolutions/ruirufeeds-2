# -*- coding: utf-8 -*-

import datetime
import werkzeug
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class MyAttendance(http.Controller):
    
    @http.route(['/my/sign_in_attendance'], type='http', auth="user", website=True)
    def sign_in_attendace(self, **post):
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render("odoo_portal_attendance.not_allowed_attendance")
        check_in = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        no_check_out_attendances = request.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False),
                ])
        if employee:
            vals = {
                    'employee_id': employee.id,
                    'check_in': check_in,
                    'check_in_web': True,
                    }
            if no_check_out_attendances:
                return werkzeug.utils.redirect('/my')
            else:
                attendance = request.env['hr.attendance'].sudo().create(vals)
            values = {
                    'attendance': attendance,
                    'employee': employee
                }
        else:
            values = {}
        return request.render('odoo_portal_attendance.sign_in_attendance', values)

    @http.route(['/my/sign_out_attendance'], type='http', auth="user", website=True)
    def sign_out_attendance(self, **post):
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render("odoo_portal_attendance.not_allowed_attendance")
        no_check_out_attendances = request.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False),
                ])
        check_out = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        attendance = no_check_out_attendances.write({'check_out': check_out})
        values = {
                    'attendance': no_check_out_attendances,
                    'employee': employee
                }
        return request.render('odoo_portal_attendance.sign_out_attendance', values)


class CustomerPortal(CustomerPortal):
    
    @http.route()
    def account(self, **kw):
        response = super(CustomerPortal, self).account(**kw)
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render("odoo_portal_attendance.not_allowed_attendance")
        attendance_obj = request.env['hr.attendance']
        
        attendance_count = attendance_obj.sudo().search_count(
            [('employee_id', '=', employee.id),
             ])
        response.qcontext.update({
                'attendance_count': attendance_count,
        })
        return response
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        attendance_obj = request.env['hr.attendance']
        
        attendance_count = attendance_obj.sudo().search_count(
            [('employee_id', '=', employee.id),
             ])
        values.update({
            'attendance_count': attendance_count,
        })
        return values
    
    @http.route(['/my/attendances', '/my/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendances(self, page=1, sortby=None, **kw):
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render("odoo_portal_attendance.not_allowed_attendance")
        attendance_obj = http.request.env['hr.attendance']
        
        domain = [
            ('employee_id', '=', employee.id),
        ]
        # count for pager
        attendance_count = attendance_obj.sudo().search_count(domain)
        
        # pager
        # pager = request.website.pager(
        pager = portal_pager(
            url="/my/attendances",
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )

        attendances = attendance_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'attendances': attendances,
            'page_name': 'attendance',
            'pager': pager,
            'default_url': '/my/attendances',
            'employee': employee
            
        })
        return request.render("odoo_portal_attendance.display_attendances", values)

    @http.route(['/my/attendance_record', '/my/attendance_record/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendance_record(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render("odoo_portal_attendance.not_allowed_attendance")
        attendances = request.env['hr.attendance'].sudo()

        domain = [('employee_id.user_partner_id', '=', request.env.user.partner_id.id)]

        searchbar_sortings = {
            'create_date': {'label': _('Date'), 'order': 'create_date desc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        attendance_count = attendances.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/attendance_record",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            step=self._items_per_page,
            total=attendance_count,
            page=page,
        )
        # content according to pager and archive selected
        attendances = attendances.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_services_history'] = attendances.ids[:100]

        values.update({
            'date': date_begin,
            'attendances': attendances,
            'page_name': 'attendance',
            'pager': pager,
            'default_url': '/my/attendance_record',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("odoo_portal_attendance.portal_attendance_records", values)
