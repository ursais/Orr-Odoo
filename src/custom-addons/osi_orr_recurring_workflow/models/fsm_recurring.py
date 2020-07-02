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

    def _prepare_order_values(self, date=None):
        res = super()._prepare_order_values(date)
        if self.fsm_equipment_id:
            res['fsm_equipment_id'] = self.fsm_equipment_id.id
        if self.agreement_id:
            res['agreement_id'] = self.agreement_id.id
        import pdb; pdb.set_trace()
        if self.sale_line_id:
            res['sale_order_line_ids'] = [(6, 0, [self.sale_line_id.id])]
        return res
    
