# -*- coding: utf-8 -*-
{
    'name': "Allowances | Deductions Allocation",

    'summary': """
        Employee Allowances""",

    'description': """
        Fine Employees, Allocate bonuses and commissions to employees.
        This also include all other types of deductions and allowances.
        Manage Employee Overtime allowances.
        Send email notification to an employee's manager 14 Days prior to the employee's contract expiry.
    """,

    'author': "Eric Waweru",
    'website': "http://www.yourcompany.com",

    'category': 'Extra Tools',
    'version': '16.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_ke'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',

        'wizards/fine_wizard.xml',
        'wizards/overtime_wizard.xml',
        'wizards/bonus_wizard.xml',

        'views/overtime.xml',
        'views/deductions.xml',
        'views/views.xml',
        'reports/sal_adv_and_non_cash_ben_report.xml',
    ],
    'license': 'LGPL-3',

}
