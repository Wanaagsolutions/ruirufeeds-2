# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    l10n_mx_edi_trailer_type = fields.Selection(
        selection=[
            ("CTR001", "Caballete"),
            ("CTR002", "Caja"),
            ("CTR003", "Caja Abierta"),
            ("CTR004", "Caja Cerrada"),
            ("CTR005", "Caja De Recolección Con Cargador Frontal"),
            ("CTR006", "Caja Refrigerada"),
            ("CTR007", "Caja Seca"),
            ("CTR008", "Caja Transferencia"),
            ("CTR009", "Cama Baja o Cuello Ganso"),
            ("CTR010", "Chasis Portacontenedor"),
            ("CTR011", "Convencional De Chasis"),
            ("CTR012", "Equipo Especial"),
            ("CTR013", "Estacas"),
            ("CTR014", "Góndola Madrina"),
            ("CTR015", "Grúa Industrial"),
            ("CTR016", "Grúa"),
            ("CTR017", "Integral"),
            ("CTR018", "Jaula"),
            ("CTR019", "Media Redila"),
            ("CTR020", "Pallet o Celdillas"),
            ("CTR021", "Plataforma"),
            ("CTR022", "Plataforma Con Grúa"),
            ("CTR023", "Plataforma Encortinada"),
            ("CTR024", "Redilas"),
            ("CTR025", "Refrigerador"),
            ("CTR026", "Revolvedora"),
            ("CTR027", "Semicaja"),
            ("CTR028", "Tanque"),
            ("CTR029", "Tolva"),
            ("CTR031", "Volteo"),
            ("CTR032", "Volteo Desmontable"),
        ],
        string="Trailer Type For Waybill",
    )
    l10n_mx_edi_sct_permit_type = fields.Selection(
        selection=[
            ("TPAF01", "Autotransporte Federal de carga general."),
            ("TPAF02", "Transporte privado de carga."),
            ("TPAF03", "Autotransporte Federal de Carga Especializada de materiales y residuos peligrosos."),
            ("TPAF04", "Transporte de automóviles sin rodar en vehículo tipo góndola."),
            ("TPAF05", "Transporte de carga de gran peso y/o volumen de hasta 90 toneladas."),
            ("TPAF06", "Transporte de carga especializada de gran peso y/o volumen de más 90 toneladas."),
            ("TPAF07", "Transporte Privado de materiales y residuos peligrosos."),
            ("TPAF08", "Autotransporte internacional de carga de largo recorrido."),
            ("TPAF09", "Autotransporte internacional de carga especializada de materiales y residuos peligrosos de "
                       "largo recorrido."),
            ("TPAF10", "Autotransporte Federal de Carga General cuyo ámbito de aplicación comprende la franja "
                       "fronteriza con Estados Unidos."),
            ("TPAF11", "Autotransporte Federal de Carga Especializada cuyo ámbito de aplicación comprende la franja "
                       "fronteriza con Estados Unidos."),
            ("TPAF12", "Servicio auxiliar de arrastre en las vías generales de comunicación."),
            ("TPAF13", "Servicio auxiliar de servicios de arrastre, arrastre y salvamento, y depósito de vehículos en"
                       " las vías generales de comunicación."),
            ("TPAF14", "Servicio de paquetería y mensajería en las vías generales de comunicación."),
            ("TPAF15", "Transporte especial para el tránsito de grúas industriales " +
                "con peso máximo de 90 toneladas."),
            ("TPAF16", "Servicio federal para empresas arrendadoras servicio público federal."),
            ("TPAF17", "Empresas trasladistas de vehículos nuevos."),
            ("TPAF18", "Empresas fabricantes o distribuidoras de vehículos nuevos."),
            ("TPAF19", "Autorización expresa para circular en los caminos y puentes de jurisdicción federal con "
                       "configuraciones de tractocamión doblemente articulado."),
            ("TPAF20", "Autotransporte Federal de Carga Especializada de fondos y valores."),
            ("TPTM01", "Permiso temporal para navegación de cabotaje"),
            ("TPTA01", "Concesión y/o autorización para el servicio regular nacional y/o internacional para empresas "
                       "mexicanas"),
            ("TPTA02", "Permiso para el servicio aéreo regular de empresas extranjeras"),
            ("TPTA03", "Permiso para el servicio nacional e internacional no regular de fletamento"),
            ("TPTA04", "Permiso para el servicio nacional e internacional no regular de taxi aéreo"),
            ("TPXX00", "Permiso no contemplado en el catálogo."),
        ],
        string="SCT Permit Type",
    )
    l10n_mx_edi_sct_permit_number = fields.Char(
        string="SCT Permit Number",
    )
    l10n_mx_edi_environment_insurance_id = fields.Many2one(
        comodel_name="res.partner",
        string="Environment Insurance",
    )
    l10n_mx_edi_environment_insurance_policy = fields.Char(
        string="Environment Insurance Policy Number",
    )
