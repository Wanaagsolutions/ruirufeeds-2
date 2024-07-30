# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class TmsWaybill(models.Model):
    _inherit = "tms.waybill"

    l10n_mx_edi_international = fields.Selection(
        string="International",
        selection=[
            ("Sí", "Sí"),
            ("No", "No")
        ],
        compute="_compute_l10n_mx_edi_international",
        help="Technical field used to define if the waybill is national or international.",
        store=True,
    )
    l10n_mx_edi_international_type = fields.Selection(
        string="International Type",
        selection=[
            ("Prohibited", "Prohibited"),
            ("Salida", "Salida")
        ],
        compute="_compute_l10n_mx_edi_international",
        help="Technical field used to define if an international freight is an import or an export",
        store=True,
    )
    l10n_mx_edi_foreign_country_id = fields.Many2one(
        comodel_name="res.country",
        string="Foreign Country",
        help="Technical field used to define the foreign country of the waybill.",
        store=True,
        compute="_compute_l10n_mx_edi_international",
    )
    l10n_mx_edi_transport_type = fields.Selection(
        selection=[
            ("01", "Federal Motor Carrier"),
            ("02", "Maritime Transport"),
            ("03", "Air Transport"),
            ("04", "Railway transport"),
            ("05", "Duct"),
        ],
        string="Transport Type",
        help="Select the transport type if a freight is international.",
        default="01",
    )
    l10n_mx_edi_station_type = fields.Selection(
        selection=[
            ("01", "National Origin"),
            ("02", "Intermedia"),
            ("03", "National Final Destination"),
        ],
        string="Station Type",
        help="Select the station type if a freight is by ship, plane or train.",
    )
    l10n_mx_edi_departure_station_id = fields.Many2one(
        comodel_name="l10n_mx_edi.station",
        string="Departure Station",
        help="Select the Departure Station",
    )
    l10n_mx_edi_departure_station_ids = fields.Many2many(
        comodel_name="l10n_mx_edi.station",
        string="Departure Stations",
        help="Technical field used to get the allowed stations for departure",
        compute="_compute_l10m_mx_edi_departure_station_ids",
    )
    l10n_mx_edi_departure_port_type = fields.Selection(
        selection=[
            ('Height', 'Height'),
            ('Cabotage', 'Cabotage'),
        ],
        string="Departure Port Type",
        help="Conditional attribute to register the type of port by which they are documented the "
             "goods or merchandise by sea.",
    )
    l10n_mx_edi_departure_date = fields.Datetime(
        string="Departure Date",
    )
    l10n_mx_edi_arrival_station_id = fields.Many2one(
        comodel_name="l10n_mx_edi.station",
        string="Arrival Station",
        help="Select the Arrival Station",
    )
    l10n_mx_edi_arrival_station_ids = fields.Many2many(
        comodel_name="l10n_mx_edi.station",
        string="Arrival Stations",
        help="Technical field used to get the allowed stations for arrival",
        compute="_compute_l10m_mx_edi_arrival_station_ids",
    )
    l10n_mx_edi_arrival_port_type = fields.Selection(
        selection=[
            ('Height', 'Height'),
            ('Cabotage', 'Cabotage'),
        ],
        string="Arrival Port Type",
        help="Conditional attribute to register the type of port by which they are documented the "
             "goods or merchandise by sea.",
    )
    l10n_mx_edi_arrival_date = fields.Datetime(
        string="Arrival Date",
    )
    l10n_mx_edi_cargo_insurance_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cargo Insurance Partner",
    )
    l10n_mx_edi_cargo_insurance_policy = fields.Char(
        string="Cargo Insurance Policy",
    )
    l10n_mx_edi_insurance_fee = fields.Monetary(
        string="Insurance Fee",
    )

    @api.depends("departure_address_id", "l10n_mx_edi_transport_type")
    def _compute_l10m_mx_edi_departure_station_ids(self):
        for rec in self:
            stations = False
            if rec.departure_address_id and self.l10n_mx_edi_transport_type in ['02', '03', '04']:
                stations = rec.departure_address_id.mapped(
                    'l10n_mx_edi_station_ids.l10n_mx_edi_station_id').filtered(
                        lambda s: s.l10n_mx_edi_transport_type == self.l10n_mx_edi_transport_type)
            rec.l10n_mx_edi_departure_station_ids = stations

    @api.depends("arrival_address_id", "l10n_mx_edi_transport_type")
    def _compute_l10m_mx_edi_arrival_station_ids(self):
        for rec in self:
            stations = False
            if rec.arrival_address_id and self.l10n_mx_edi_transport_type in ['02', '03', '04']:
                stations = rec.arrival_address_id.mapped(
                    'l10n_mx_edi_station_ids.l10n_mx_edi_station_id').filtered(
                        lambda s: s.l10n_mx_edi_transport_type == self.l10n_mx_edi_transport_type)
            rec.l10n_mx_edi_arrival_station_ids = stations

    @api.depends(
        "departure_address_id",
        "arrival_address_id",
        "departure_address_id.country_id",
        "arrival_address_id.country_id")
    def _compute_l10n_mx_edi_international(self):
        for rec in self:
            international = 'No'
            international_type = False
            mx_country = self.env.ref('base.mx')
            foreign_country_id = False
            if (rec.departure_address_id.country_id and rec.
                    departure_address_id.country_id != mx_country):
                international = 'Sí'
                international_type = 'Prohibited'
                foreign_country_id = rec.departure_address_id.country_id.id
            if (rec.arrival_address_id.country_id and rec.
                    arrival_address_id.country_id != mx_country):
                international = 'Sí'
                international_type = 'Salida'
                foreign_country_id = rec.arrival_address_id.country_id.id
            rec.update({
                "l10n_mx_edi_international": international,
                "l10n_mx_edi_international_type": international_type,
                "l10n_mx_edi_foreign_country_id": foreign_country_id,
            })

    @api.onchange("l10n_mx_edi_transport_type")
    def _onchange_l10n_mx_edi_transport_type(self):
        if not self.l10n_mx_edi_transport_type or self.l10n_mx_edi_transport_type in ["01", "05"]:
            self.l10n_mx_edi_station_type = False
        if not self.l10n_mx_edi_transport_type or self.l10n_mx_edi_transport_type != "02":
            self.l10n_mx_edi_departure_port_type = False
            self.l10n_mx_edi_arrival_port_type = False

    @api.onchange("l10n_mx_edi_international")
    def _onchange_l10n_mx_edi_international(self):
        if self.l10n_mx_edi_international == 'No':
            self.l10n_mx_edi_transport_type = False
            self.l10n_mx_edi_departure_port_type = False
            self.l10n_mx_edi_arrival_port_type = False

    @api.onchange("departure_address_id", "arrival_address_id", "l10n_mx_edi_transport_type")
    def _onchange_stations(self):
        departure = self.departure_address_id
        arrival = self.arrival_address_id
        transport_type = self.l10n_mx_edi_transport_type in ['02', '03', '04']
        if departure and arrival and transport_type:
            if not departure.l10n_mx_edi_station_ids.filtered(
                    lambda s: s.l10n_mx_edi_transport_type == self.l10n_mx_edi_transport_type):
                return {
                    "warning": {
                        'title': _('Warning'),
                        'message': _("You need to define the Station in the Departure Address."),
                    }
                }
            if not arrival.l10n_mx_edi_station_ids.filtered(
                    lambda s: s.l10n_mx_edi_transport_type == self.l10n_mx_edi_transport_type):
                return {
                    "warning": {
                        'title': _('Warning'),
                        'message': _("You need to define the Station in the Arrival Address."),
                    }
                }
