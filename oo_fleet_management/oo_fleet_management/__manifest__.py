# -*- coding: utf-8 -*-
{
    'name': "Fleet Management",

    'summary': """
        Fleet management module.""",

    'description': """
        Manage fleet attributes such as:
            - Drivers (Including driver trip shorts and driver short repayments)
            - Trucks
            - Suppliers
            - Customers
            - Trips / Journeys
            - Customer Orders
            - Documents (Driver, truck and trip)
            - Trip Routes and rates per route
            - Subcontracted trucks with supplier rates
    """,

    'author': "Teclea Ltd",
    'website': "http://www.teclea.com",
    'license': 'LGPL-3',
    'category': 'Customizations',
    'version': '15.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['analytic', 'hr_expense'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        
        'reports/nomination.xml',
        
        'data/sequence.xml',
        'data/mail_data.xml',
        'data/server_action.xml',
        
        'wizards/wizard.xml',
        
        'views/common_masters.xml',
        'views/accounts.xml',
        'views/fleet_order.xml',
        'views/fleet_trip.xml',
        'views/fleet_truck.xml',
        'views/stock.xml',
        'views/hr.xml',
        'views/res_partner.xml',
        'views/res_config.xml',
        'views/workshop.xml',
        'views/charge_sheet.xml',
        'views/menus.xml',
    ],
    'application': True,
}
