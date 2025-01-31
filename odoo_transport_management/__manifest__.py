# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Transport Management and Delivery Routes',
    'price': 59.00,
    'category': 'Warehouse',
    'summary': 'This module allow you to manage Transport information of your delivery orders and Routes of Delivery.',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'license': 'Other proprietary',
    'website': 'https://www.probuse.com',
    'live_test_url':'https://youtu.be/giLmEnhwbMY',
    'currency': 'EUR',
    'version': '2.1',
    'description':"""Odoo Transport Management. This module allow create picking information 
Odoo Transport Management
Odoo Transport
Transport Management
Picking Transport Entry   
Transport Entry
Inventory/Picking Transport Entry
Inventory/Picking Transport Entry/Picking Transport Entry
Transport
Transport/Picking Transport Entry
Transport/Picking Transport Entry/Picking Transport Entry
Transport/Route Locations
Transport/Transport Routes
Transport/Transport Routes/Route Locations
Transport/Transport Routes/Transport Routes
Transport/Transporters
Transport/Transporters/Transporters
Transport Routes
Transport/Vehicles
Transport/Vehicles/Vehicles
Route Locations
Transporters
transport management
odoo transport management
transport
Transport
Inventory/Picking Transport Entry
-- Inventory/Picking Transport Entry/Picking Transport Entry
Transport
-- Transport/Picking Transport Entry
-- -- Transport/Picking Transport Entry/Picking Transport Entry
-- Transport/Route Locations
-- -- Transport/Transport Routes/Route Locations
-- Transport/Transport Routes
-- -- Transport/Transport Routes/Transport Routes
-- Transport/Transporters
-- -- Transport/Transporters/Transporters
-- Transport/Vehicles
-- -- Transport/Vehicles/Vehicles
""",
    'images': ['static/description/img1.jpeg'],
    'depends': ['sale_management',
                'stock',
                'sale_stock',
                'fleet',
                'delivery',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/transport_view.xml',
        'views/sale_view.xml',
        'views/stock_picking_view.xml',
        'views/sale_report.xml',
        'views/delivery_report.xml',
        'views/account_invoice_view.xml',
        'views/partner_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/picking_transport_info_view.xml',
        'views/transporter_route_view.xml',
        'views/route_location_view.xml',
        'report/picking_transport_report.xml',
        'data/transport_sequence.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
