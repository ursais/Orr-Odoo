# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMBranch(models.Model):
    _inherit = 'fsm.branch'

    analytic_tag_id = fields.Many2one(
        'account.analytic.tag',
        string='Analytic Tag',
    )
