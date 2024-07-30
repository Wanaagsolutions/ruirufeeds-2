# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
from lxml import etree
from lxml.objectify import fromstring

from odoo import models, tools

CFDI_XSLT_CARTAPORTE_CADENA = "l10n_mx_edi_tms_waybill/data/3.3/cadenaoriginal_3_3.xslt"


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_mx_edi_decode_cfdi(self, cfdi_data=None):
        """If the CFDI was signed, try to adds the schemaLocation correctly"""
        def get_node(cfdi_node, attribute, namespaces):
            if hasattr(cfdi_node, 'Complemento'):
                node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
                return node[0] if node else None

        def get_cadena(cfdi_node, template):
            if cfdi_node is None:
                return None
            cadena_root = etree.parse(tools.file_open(template))
            return str(etree.XSLT(cadena_root)(cfdi_node))

        if not cfdi_data:
            signed_edi = self._get_l10n_mx_edi_signed_edi_document()
            if signed_edi:
                cfdi_data = base64.decodebytes(signed_edi.attachment_id.with_context(bin_size=False).datas)
        result = super()._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi_data)
        if not cfdi_data:
            return result
        if isinstance(cfdi_data, str):
            cfdi_data = cfdi_data.replace(
                'xmlns__cartaporte20', 'xmlns:cartaporte20')
        cfdi = fromstring(cfdi_data)
        if 'cartaporte20' not in cfdi.nsmap:
            return result
        cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
            cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
            'http://www.sat.gob.mx/CartaPorte20',
            'http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd'
        )
        cartaporte_node = get_node(
            cfdi,
            'cartaporte20:CartaPorte[1]',
            {'cartaporte20': 'http://www.sat.gob.mx/CartaPorte20'},
        )
        result.update({
            'cfdi_node': cfdi,
            'cadena': get_cadena(cfdi, CFDI_XSLT_CARTAPORTE_CADENA),
            'cartaporte_node': cartaporte_node,
            'hasattr': hasattr,
        })
        return result
