# -*- coding: utf-8 -*-
{
    'name': "Employee P9 Form",

    'summary': """
       Generate Employee P9 Form""",

    'description': """
    """,

    'author': "Eric Waweru",
    'website': "http://www.yourcompany.com",

    'category': 'Extra Tools',
    'version': '16.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_ke'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        
        'reports/misc.xml',
        'reports/templates.xml',
        'reports/main.xml',
        'reports/report.xml',
        
        'wizards/p9.xml',        
    ],

}
