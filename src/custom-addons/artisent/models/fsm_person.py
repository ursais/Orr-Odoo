# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class FSMPerson(models.Model):
    _name = 'fsm.person'
    _inherit = ['fsm.person', 'mail.thread', 'mail.activity.mixin']
