# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Attendance from Web-My Account using Portal User as Employee',
    'version': '1.0',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Website',
    'summary':  """This module allow you to employee(s) who are not real users of system but portal users / external user and it will allow to record check in and checkout as attendance""",
    'description': """
        Odoo Portal Employee Attendance
     """,
    'depends': [
        'hr_attendance',
        'portal',
        ],
    'data': [
      'security/security.xml',
      'security/ir.model.access.csv',
      'views/website_portal_templates.xml',
      'views/assets.xml',
     ],

    'assets': {
        'web_editor.assets_frontend': [
        'static/src/scss/hr_attendance.scss',
        ],
    },

    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
