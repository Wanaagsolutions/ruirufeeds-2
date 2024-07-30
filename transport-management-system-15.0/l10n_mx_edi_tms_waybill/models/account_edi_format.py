# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        res = super()._l10n_mx_edi_get_invoice_cfdi_values(invoice)

        def _prepare_locations(invoice, loc_type):
            waybill = invoice.waybill_ids
            if loc_type == 'origin':
                partner = waybill.departure_address_id
                location_type = "Origen"
                loc_id = "OR" + str(partner.id).zfill(6)
                date = min(waybill.travel_ids.mapped("date_start"))
                distance = False
            else:
                partner = waybill.arrival_address_id
                location_type = "Destino"
                loc_id = "DE" + str(partner.id).zfill(6)
                date = max(waybill.travel_ids.mapped("date_end"))
                distance = waybill.travel_ids[0].distance_route
                if not distance:
                    raise UserError(_('The travel distance is not set.'))
            if not date:
                raise UserError(_('The travel dates are not set.'))
            data = {
                "type": location_type,
                "id": loc_id,
                "partner": partner,
                "date": date.strftime('%Y-%m-%dT%H:%M:%S'),
                "distance": distance,
            }
            return data
        if not invoice.waybill_ids:
            return res
        travel = invoice.waybill_ids.travel_ids[0]
        res.update({
            "locations": [
                _prepare_locations(invoice, "origin"),
                _prepare_locations(invoice, "destination"),
            ],
            "trailers": travel.trailer1_id + travel.trailer2_id,
            "figures": [{
                "type": "01",  # 01 Operador
                "partner": travel.employee_id.address_home_id,
                "driver": travel.employee_id,
            }],
        })
        return res
