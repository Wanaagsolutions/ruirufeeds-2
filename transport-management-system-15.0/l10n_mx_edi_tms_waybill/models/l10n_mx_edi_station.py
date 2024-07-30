# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.osv import expression


class L10nMXEdiStation(models.Model):
    _name = 'l10n_mx_edi.station'
    _description = "Mexican EDI Station"

    l10n_mx_edi_transport_type = fields.Selection(
        selection=[
            ("02", "Maritime Transport"),
            ("03", "Air Transport"),
            ("04", "Railway Transport"),
        ],
        string="Transport Type",
        required=True,
    )
    code = fields.Char(
        help="Code defined in the SAT to this record.",
        required=True,
    )
    name = fields.Char(
        help="Name defined in the SAT catalog to this record.",
        required=True,
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
    )
    active = fields.Boolean(
        help="If the station has expired it could be disabled to do not allow select the record.",
        default=True,
    )

    def name_get(self):
        # OVERRIDE
        return [(station.id, "%s %s" % (station.code, station.name or '')) for station in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        # OVERRIDE
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
