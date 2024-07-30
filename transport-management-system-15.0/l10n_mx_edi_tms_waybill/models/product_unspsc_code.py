# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductUnspscCode(models.Model):
    _inherit = "product.unspsc.code"

    l10n_mx_edi_waybill_type = fields.Selection(
        selection=[
            ("0", "No Dangerous Material"),
            ("1", "Dangerous Material"),
            ("0,1", "Optional Dangerous Material"),
            ("uom", "Unit of Measure"),
        ],
        string="Type of Code",
        help="Field to indicate if the product is dangerous material",
    )
