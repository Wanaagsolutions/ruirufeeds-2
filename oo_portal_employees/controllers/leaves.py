# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from dateutil.parser import parse
from odoo import _, http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class LeavesPortal(CustomerPortal):
    def _leaves_domain(self):
        return [('employee_id', '!=', False), ('employee_id.user_partner_id', '=', request.env.user.partner_id.id)]
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'leave_count' in counters:
            leaves_model = request.env['hr.leave'].with_user(2)
            values['leave_count'] = leaves_model.search_count(self._leaves_domain()) or '0'
        return values

    def _leaves_get_page_view_values(self, leave, access_token, **kwargs):
        if not leave.access_token:
            leave.access_token = uuid4().hex
        user = request.env.user.with_user(2)
        portal_leave_manager = user.has_group('oo_portal_employees.group_portal_employee_leave_manager')
        backend_leave_manager = user.has_group('hr_holidays.group_hr_holidays_responsible')
        
        values = {
            'page_name': 'leave',
            'leave': leave,
            'leave_types': request.env['hr.leave.type'].get_days_all_request(),
            'is_readonly': bool(leave),
            'can_approve': (portal_leave_manager or backend_leave_manager) and leave.state not in ['draft', 'refuse', 'validate'],
            'can_refuse': (portal_leave_manager or backend_leave_manager) and leave.state not in ['draft', 'refuse'],
            'can_cancel': portal_leave_manager or backend_leave_manager,
        }
        return self._get_page_view_values(leave, access_token, values, 'my_leaves_history', False, **kwargs)
    
    def _check_access_rights(self, leave_id, access_token):
        try:
            leave_sudo = self._document_check_access('hr.leave', leave_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return leave_sudo

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        leaves_model = request.env['hr.leave'].with_user(2)

        domain = self._leaves_domain()
        
        searchbar_sortings = {
            'create_date': {'label': _('Create Date'), 'order': 'create_date desc'},
            'date_from': {'label': _('Leave Date'), 'order': 'date_from desc'},
            'type': {'label': _('Leave Type'), 'order': 'holiday_status_id asc'},
            'state': {'label': _('Leave Status'), 'order': 'state asc'},
            'duration': {'label': _('Duration'), 'order': 'duration_display asc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('date_from', '>', date_begin), ('date_to', '<=', date_end)]

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        leaves_count = leaves_model.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=leaves_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        leaves = leaves_model.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_leaves_history'] = leaves.ids[:100]

        values.update({
            'date': date_begin,
            'leaves': leaves,
            'leave_types':  request.env['hr.leave.type'].get_days_all_request(),
            'page_name': 'leave',
            'pager': pager,
            'default_url': '/my/leaves',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
            'is_readonly': kw.get('is_readonly', True)
        })
        return request.render("oo_portal_employees.portal_my_leaves", values)

    @http.route(['/my/leaves/<int:leave_id>'], type='http', auth="user", website=True)
    def portal_my_leave_details(self, leave_id=None, access_token=None, report_type=None, download=False, **kw):
        leave_sudo = leave_id and self._check_access_rights(leave_id, access_token) or request.env['hr.leave'].with_user(2)

        values = self._leaves_get_page_view_values(leave_sudo, access_token, **kw)
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=leave_sudo, report_type=report_type, report_ref='hr_payroll.action_report_payslip', download=download)
        return request.render("oo_portal_employees.portal_leave_page", values)
    
    @http.route(['/leaves/<int:leave_id>/cancel'], type='http', auth="user", website=True)
    def portal_leave_cancel(self, leave_id=None, access_token=None, report_type=None, download=False, **kw):
        leave_sudo = self._check_access_rights(leave_id, access_token)
        if not leave_sudo.can_cancel:
            raise ValidationError("You're not allowed to perform this action.")
        leave_sudo.with_user(2).action_cancel()
        return request.redirect('my/leaves')

    @http.route(['/leaves/<int:leave_id>/refuse'], type='http', auth="user", website=True)
    def portal_leave_refuse(self, leave_id=None, access_token=None, **kw):
        leave_sudo = self._check_access_rights(leave_id, access_token)
        if not leave_sudo.can_approve:
            raise ValidationError("You're not allowed to perform this action.")
        leave_sudo.with_user(2).action_refuse()
        return request.redirect('my/leaves')

    @http.route(['/leaves/<int:leave_id>/approve'], type='http', auth="user", website=True)
    def portal_leave_approve(self, leave_id=None, access_token=None, **kw):
        leave_sudo = self._check_access_rights(leave_id, access_token)
        if not leave_sudo.can_approve:
            raise ValidationError("You're not allowed to perform this action.")
        leave_sudo.with_user(2).action_approve()
        return request.redirect('my/leaves')
    
    @http.route(['/my/leaves/new'], type='http', auth="user", website=True)
    def portal_leave_new(self, **kw):
        leave_model = request.env['hr.leave'].with_user(2)
        employee = request.env['hr.employee'].with_user(2).search([('user_partner_id', '=', request.env.user.partner_id.id)], limit=1)
        if not employee:
            raise ValidationError('Missing required employee for this user.')
        kw.update({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': int(kw['holiday_status_id']),
            'state': 'draft',
            'date_from': parse(kw['date_from']),
            'date_to': parse(kw['date_to']),
        })
        _logger.info(f'creating new leave for employee {employee.name} with data {kw}')
        leave = leave_model.with_context(leave_skip_date_check=True).create(kw)
        leave.with_user(2).action_confirm()
        kw.clear()
        return request.redirect('my/leaves')

