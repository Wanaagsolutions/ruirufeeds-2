# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.osv import expression


class L10nMXEdiPackaging(models.Model):
    _name = 'l10n_mx_edi.packaging'
    _description = "Mexican EDI Packaging"

    code = fields.Char(
        help="Code defined in the SAT to this record.",
        required=True,
    )
    name = fields.Char(
        help="Name defined in the SAT catalog to this record.",
        required=True,
    )
    active = fields.Boolean(
        help="If the packaging has expired it could be disabled to do not allow select the record.",
        default=True,
    )

    def name_get(self):
        # OVERRIDE
        return [(packaging.id, "%s %s" % (packaging.code, packaging.name or '')) for packaging in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        # OVERRIDE
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name), ('code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
