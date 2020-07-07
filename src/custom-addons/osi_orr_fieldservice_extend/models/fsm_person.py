# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class FSMPerson(models.Model):
    _inherit = 'fsm.person'

    def _default_team_id(self):
        team_ids = self.env['fsm.team'].\
            search([('company_id', 'in', (self.env.user.company_id.id,
                                          False))],
                   order='sequence asc', limit=1)
        if team_ids:
            return team_ids[0]
        else:
            raise ValidationError(_(
                "You must create an FSM team first."))

    team_id = fields.Many2one('fsm.team', string='Team',
                              default=lambda self: self._default_team_id())
