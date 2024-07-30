# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=file-not-used

{
    "name": "TMS Waybill Complement for Mexico",
    "version": "15.0.1.0.6",
    "category": "Transport",
    "author": "Jarsa Sistemas",
    "website": "https://www.jarsa.com.mx/page/transport-management-system",
    "depends": [
        "tms",
        "l10n_mx_edi_extended",
    ],
    "summary": "Add Waybill Complement to TMS",
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/tms_waybill_template.xml",
        "data/decimal_precision_data.xml",
        "views/tms_waybill_view.xml",
        "views/res_partner_view.xml",
        "views/tms_transportable_view.xml",
        "views/tms_travel_view.xml",
        "views/fleet_vehicle_view.xml",
        "views/report_account_invoice.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
