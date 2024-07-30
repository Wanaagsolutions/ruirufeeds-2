# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class TmsTravel(models.Model):
    _inherit = "tms.travel"

    l10n_mx_edi_configuration = fields.Selection(
        selection=[
            ("VL", "Vehículo ligero de carga (2 llantas en el eje delantero y 2 llantas en el eje trasero)"),
            ("C2", "Camión Unitario (2 llantas en el eje delantero y 4 llantas en el eje trasero)"),
            ("C3", "Camión Unitario (2 llantas en el eje delantero y 6 o 8 llantas en los dos ejes traseros)"),
            ("C2R2", "Camión-Remolque (6 llantas en el camión y 8 llantas en remolque)"),
            ("C3R2", "Camión-Remolque (10 llantas en el camión y 8 llantas en remolque)"),
            ("C2R3", "Camión-Remolque (6 llantas en el camión y 12 llantas en remolque)"),
            ("C3R3", "Camión-Remolque (10 llantas en el camión y 12 llantas en remolque)"),
            ("T2S1", "Tractocamión Articulado (6 llantas en el tractocamión, 4 llantas en el semirremolque)"),
            ("T2S2", "Tractocamión Articulado (6 llantas en el tractocamión, 8 llantas en el semirremolque)"),
            ("T2S3", "Tractocamión Articulado (6 llantas en el tractocamión, 12 llantas en el semirremolque)"),
            ("T3S1", "Tractocamión Articulado (10 llantas en el tractocamión, 4 llantas en el semirremolque)"),
            ("T3S2", "Tractocamión Articulado (10 llantas en el tractocamión, 8 llantas en el semirremolque)"),
            ("T3S3", "Tractocamión Articulado (10 llantas en el tractocamión, 12 llantas en el semirremolque)"),
            ("T2S1R2", "Tractocamión Semirremolque-Remolque (6 llantas en el tractocamión, 4 llantas en el "
                       "semirremolque y 8 llantas en el remolque)"),
            ("T2S2R2", "Tractocamión Semirremolque-Remolque (6 llantas en el tractocamión, 8 llantas en el "
                       "semirremolque y 8 llantas en el remolque)"),
            ("T2S1R3", "Tractocamión Semirremolque-Remolque (6 llantas en el tractocamión, 4 llantas en el "
                       "semirremolque y 12 llantas en el remolque)"),
            ("T3S1R2", "Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 4 llantas en el "
                       "semirremolque y 8 llantas en el remolque)"),
            ("T3S1R3", "Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 4 llantas en el "
                       "semirremolque y 12 llantas en el remolque)"),
            ("T3S2R2", "Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 8 llantas en el "
                       "semirremolque y 8 llantas en el remolque)"),
            ("T3S2R3", "Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 8 llantas en el "
                       "semirremolque y 12 llantas en el remolque)"),
            ("T3S2R4", "Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 8 llantas en el "
                       "semirremolque y 16 llantas en el remolque)"),
            ("T2S2S2", "Tractocamión Semirremolque-Semirremolque (6 llantas en el tractocamión, 8 llantas en el "
                       "semirremolque delantero y 8 llantas en el semirremolque trasero)"),
            ("T3S2S2", "Tractocamión Semirremolque-Semirremolque (10 llantas en el tractocamión, 8 llantas en el "
                       "semirremolque delantero y 8 llantas en el semirremolque trasero)"),
            ("T3S3S2", "Tractocamión Semirremolque-Semirremolque (10 llantas en el tractocamión, 12 llantas en el "
                       "semirremolque delantero y 8 llantas en el semirremolque trasero)"),
            ("OTROEVGP", "Especializado de carga Voluminosa y/o Gran Peso"),
            ("OTROSG", "Servicio de Grúas"),
            ("GPLUTA", "Grúa de Pluma Tipo A"),
            ("GPLUTB", "Grúa de Pluma Tipo B"),
            ("GPLUTC", "Grúa de Pluma Tipo C"),
            ("GPLUTD", "Grúa de Pluma Tipo D"),
            ("GPLATA", "Grúa de Plataforma Tipo A"),
            ("GPLATB", "Grúa de Plataforma Tipo B"),
            ("GPLATC", "Grúa de Plataforma Tipo C"),
            ("GPLATD", "Grúa de Plataforma Tipo D"),
        ],
        string="Configuration",
    )
