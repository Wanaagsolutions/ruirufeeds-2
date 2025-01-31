# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        domain="[('user_ids', '=', uid)]",
        compute="_compute_operating_unit_id",
        store=True,
    )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        lines = super()._prepare_move_line_default_vals(write_off_line_vals)
        for line in lines:
            line["operating_unit_id"] = self.operating_unit_id.id
        if not self._context.get("active_model"):
            return lines
        invoices = self.env[self._context.get("active_model")].browse(
            self._context.get("active_ids")
        )
        invoices_ou = invoices.operating_unit_id
        if invoices and len(invoices_ou) == 1 and invoices_ou != self.operating_unit_id:
            destination_account_id = self.destination_account_id.id
            for line in lines:
                if line["account_id"] == destination_account_id:
                    line["operating_unit_id"] = invoices_ou.id
        return lines
