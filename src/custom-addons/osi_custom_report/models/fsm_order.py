# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'
    
    style = fields.Many2one(
        'report.template.settings',
        'FSM Order Style',
        help="Select Style to use when printing the FSM Order",
        default=lambda self: self.env.user.company_id.fsm_style or\
            self.env.user.company_id.df_style)
