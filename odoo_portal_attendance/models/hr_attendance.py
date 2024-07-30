# -*- coding: utf-8 -*-
from odoo import models, fields


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    check_in_web = fields.Boolean(
        'Check In Web',
        default=False, 
        copy=True, 
        required=False
    )
