# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmOrderGroup(models.Model):
    _name = 'fsm.order.group'
    _description = 'FSM Order Group'

    name = fields.Char('Name')
