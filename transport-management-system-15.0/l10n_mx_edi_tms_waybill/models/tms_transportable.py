# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TmsTransportable(models.Model):
    _inherit = "tms.transportable"

    unspsc_code_id = fields.Many2one(
        comodel_name="product.unspsc.code",
        string="UNSPSC Code",
        domain=[("applies_to", "=", "product"), ("l10n_mx_edi_waybill_type", "!=", False)],
    )
    l10n_mx_edi_waybill_type = fields.Selection(
        related="unspsc_code_id.l10n_mx_edi_waybill_type",
        store=True,
    )
    l10n_mx_edi_dimensions = fields.Char(
        string="Dimensions",
        help="Optional attribute to express the measures of the packaging of the goods "
             "and / or merchandise that are moved in the different means of transport. "
             "The length, height and width must be recorded in centimeters or in inches"
             ", these values separated by a diagonal, i.e. 30/40 / 30cm.",
    )
    l10n_mx_edi_dangerous_material_id = fields.Many2one(
        comodel_name="l10n_mx_edi.dangerous.material",
        string="Dangerous Material",
    )
    l10n_mx_edi_packaging_id = fields.Many2one(
        comodel_name="l10n_mx_edi.packaging",
        string="Packaging",
    )
    l10n_mx_edi_weight_factor = fields.Float(
        string="Weight Factor (Kg)",
        help="Factor to convert quantity to Kg (e.g. 1.0 for 1 Kg, 0.5 for 500 g, etc.)",
        digits="Weight Factor (l10n_mx_edi_tms_waybill)",
    )
    l10n_mx_edi_tariff_fraction_id = fields.Many2one(
        comodel_name="l10n_mx_edi.tariff.fraction",
        string="Tariff Fraction",
        help="It is used to express the key of the tariff fraction corresponding to the description of the product to "
             "export."
    )

    @api.constrains("l10n_mx_edi_dimensions")
    def _check_l10n_mx_edi_dimensions(self):
        for rec in self:
            if rec.l10n_mx_edi_dimensions:
                pattern = "([0-9]{1,3}[/]){2}([0-9]{1,3})(cm|plg)"
                regex = re.compile(pattern)
                if not regex.match(rec.l10n_mx_edi_dimensions):
                    raise UserError(_(
                        "The dimensions must be in the format: 999/999/999cm or 999/999/999plg"))
