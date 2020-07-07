# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmRecurringGroup(models.Model):
    _name = 'fsm.recurring.group'
    _description = 'FSM Recurring Group'

    name = fields.Char('Name')
