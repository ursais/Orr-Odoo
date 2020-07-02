# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.rrule import rruleset
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _


class FSMRecurringOrder(models.Model):
    _inherit = 'fsm.recurring'

    def _get_default_agreement(self):
        if self.sale_line_id:
            self.agreement_id = self.sale_line_id.order_id.agreement_id

    fsm_equipment_id = fields.Many2one('fsm.equipment', 'Equipment')
    agreement_id = fields.Many2one('agreement', 'Agreement', default=lambda self: self._get_default_agreement())
