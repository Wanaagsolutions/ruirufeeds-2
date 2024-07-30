# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_mx_edi_station_ids = fields.One2many(
        comodel_name="res.partner.l10n_mx_edi.station",
        inverse_name="partner_id",
        string="Stations",
        help="Define stations depending on transport type of this partner.",
    )


class ResPartnerL10nMxEdiStation(models.Model):
    _name = "res.partner.l10n_mx_edi.station"
    _description = "Stations related to partner by transport type."

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
    )
    l10n_mx_edi_transport_type = fields.Selection(
        selection=[
            ("02", "Maritime Transport"),
            ("03", "Air Transport"),
            ("04", "Railway Transport"),
        ],
        string="Transport Type",
        required=True,
    )
    l10n_mx_edi_station_id = fields.Many2one(
        comodel_name="l10n_mx_edi.station",
        string="Station",
        required=True,
    )
