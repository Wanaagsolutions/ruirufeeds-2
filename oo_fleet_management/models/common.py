
from odoo import fields, models

DOCUMENTS_APPLICABLE_ON = [
    ('driver', 'Driver'), ('trip', 'Trip'), ('truck', 'Truck')]


class FleetRoute(models.Model):
    _name = 'fleet.route'
    _description = 'Fleet Route'

    name = fields.Char(string='Name', required=True)
    pickup_location = fields.Char('Pickup Location', required=True)
    drop_location = fields.Char('Drop Off Location', required=True)
    pickup_city = fields.Char('Pickup City', required=True)
    drop_city = fields.Char(string='Drop Off City', required=True)
    distance = fields.Float(string='Distance (KM)', required=True)
    pickup_country_id = fields.Many2one(
        'res.country', string='Pickup Country', required=True)
    drop_country_id = fields.Many2one(
        'res.country', string='Drop Off Country', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    
    company_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Company Truck Income Account",
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', company_id),\
                            ('user_type_id', 'in', %s)]" % [self.env.ref('account.data_account_type_revenue').id,
                                                            self.env.ref('account.data_account_type_other_income').id])
    contractor_truck_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Contractor Truck Income Account",
        domain=lambda self: "[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', company_id),\
                            ('user_type_id', 'in', %s)]" % [self.env.ref('account.data_account_type_revenue').id,
                                                            self.env.ref('account.data_account_type_other_income').id])


class FleetDocumentType(models.Model):
    _name = 'fleet.document.type'
    _description = 'Fleet Document Type'

    name = fields.Char(string='Name', required=True)
    applicable_on = fields.Selection(
        string='Applicable On', selection=DOCUMENTS_APPLICABLE_ON, required=True)
    mandatory = fields.Boolean(string='Mandatory')

    def _make_default_entry(self):
        self.ensure_one()
        return {
            'document_id': self.id,
        }


class PartnerRelationship(models.Model):
    _name = 'partner.relationship'
    _description = 'Partner Relationships'

    name = fields.Char(string='Name', required=True)
