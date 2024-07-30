# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo import api, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _load_xsd_complements(self, content):
        content = super()._load_xsd_complements(content)
        complements = [
            ["http://www.sat.gob.mx/CartaPorte20",
             "http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd"],
        ]
        for complement in complements:
            xsd = {'namespace': complement[0], 'schemaLocation': complement[1]}
            node = etree.Element('{http://www.w3.org/2001/XMLSchema}import', xsd)
            content.insert(0, node)
        return content
