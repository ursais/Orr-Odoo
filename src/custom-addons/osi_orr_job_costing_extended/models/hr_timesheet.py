# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    fsm_order_id = fields.Many2one(
        'fsm.order',
        string='FSM Order',
    )
    type_id = fields.Many2one(
        'fsm.order.type', string='Type')
