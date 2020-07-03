# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRecurringOrder(models.Model):
    _inherit = 'fsm.recurring'

    group_id = fields.Many2one('fsm.recurring.group', string='Group ID')
