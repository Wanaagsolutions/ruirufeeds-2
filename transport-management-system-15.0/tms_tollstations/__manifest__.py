# Copyright 2016-2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Highway tollstations',
    'summary': 'Highway tollstations',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'category': 'Transport',
    'version': '15.0.1.0.1',
    "license": "LGPL-3",
    'depends': ['tms'],
    'data': [
        'views/tms_expense_line_view.xml',
        'views/tms_toll_data_view.xml',
        'views/fleet_vehicle_view.xml',
        'wizards/tms_toll_import.xml',
        'reports/report_highway.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
