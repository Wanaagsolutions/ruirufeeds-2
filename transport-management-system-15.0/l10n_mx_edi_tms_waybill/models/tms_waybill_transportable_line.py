# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.l10n_mx_edi_extended.models.account_move import CUSTOM_NUMBERS_PATTERN


class TmsWaybillTransportableLine(models.Model):
    _inherit = "tms.waybill.transportable.line"

    l10n_mx_edi_merchandise_value = fields.Monetary(
        string="Merchandise Value",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.user.company_id.currency_id,
    )
    l10n_mx_edi_uuid = fields.Char(
        string="UUID",
    )
    l10n_mx_edi_tare = fields.Float(
        string='Tare(Kg)',
    )
    l10n_mx_edi_customs_number = fields.Char(
        help='Optional field for entering the customs information in the case '
        'of first-hand sales of imported goods or in the case of foreign trade'
        ' operations with goods or services.\n'
        'The format must be:\n'
        ' - 2 digits of the year of validation followed by two spaces.\n'
        ' - 2 digits of customs clearance followed by two spaces.\n'
        ' - 4 digits of the serial number followed by two spaces.\n'
        ' - 1 digit corresponding to the last digit of the current year, '
        'except in case of a consolidated customs initiated in the previous '
        'year of the original request for a rectification.\n'
        ' - 6 digits of the progressive numbering of the custom.',
        string='Customs number',
    )

    def _l10n_mx_edi_get_custom_numbers(self):
        self.ensure_one()
        if self.l10n_mx_edi_customs_number:
            return [num.strip() for num in self.l10n_mx_edi_customs_number.split(',')]
        return []

    @api.constrains('l10n_mx_edi_customs_number')
    def _check_l10n_mx_edi_customs_number(self):
        invalid_lines = self.env['tms.waybill.transportable.line']
        for line in self:
            custom_numbers = line._l10n_mx_edi_get_custom_numbers()
            if any(not CUSTOM_NUMBERS_PATTERN.match(custom_number) for custom_number in custom_numbers):
                invalid_lines |= line

        if not invalid_lines:
            return

        raise ValidationError(_(
            "Custom numbers set on transportable lines are invalid and should have a pattern like: "
            "15  48  3009  0001234:\n%(invalid_message)s",
            invalid_message='\n'.join('%s (id=%s)' % (
                line.l10n_mx_edi_customs_number, line.id) for line in invalid_lines),
            )
        )
