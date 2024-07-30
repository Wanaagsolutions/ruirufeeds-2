from odoo import fields, models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    truck_id = fields.Many2one('fleet.truck', string='Truck')
    

class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'
    
    is_closed = fields.Boolean(string='Is Closed', help='If coming from a fleet, this tag is closed and cannot be expensed')
    trip_id = fields.Many2one('fleet.trip', string='Trip')
    truck_id = fields.Many2one(related='trip_id.truck_id', string='Truck')


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    trip_id = fields.Many2one('fleet.trip', string='Trip', readonly=True)
    trip_pod_number = fields.Char(string='Proof of Delivery Number', related='trip_id.pod_number')
    trip_order_id = fields.Many2one('fleet.order', string='Trip Order', related='trip_id.order_id')
    trip_offloading_date = fields.Datetime(string='Trip Offloading Date', related='trip_id.offloading_date')
    trip_truck_id = fields.Many2one('fleet.truck', string='Trip Truck', related='trip_id.truck_id')
    trip_route_id = fields.Many2one('fleet.route', string='Trip Route', related='trip_id.route_id')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    trip_id = fields.Many2one('fleet.trip', string='Fleet Trip', readonly=True)
    trip_pod_number = fields.Char(string='Proof of Delivery Number', related='trip_id.pod_number')
    truck_id = fields.Many2one(related='analytic_account_id.truck_id', string='Truck')
    
    @api.onchange('product_id', 'analytic_account_id')
    def _onchange_product_truck_account(self):
        for rec in self:
            if rec.analytic_account_id.truck_id:
                if rec.analytic_account_id.truck_id.ownership == 'company':
                    if rec.product_id.can_be_expensed:
                        rec.account_id = rec.product_id.fleet_prepaid_account_expense_id or rec._get_computed_account()
                    else:
                        rec.account_id = rec._get_computed_account()
                else:
                    rec.account_id = rec.product_id.contractor_expense_account_id
            else:
                rec.account_id = rec._get_computed_account()
