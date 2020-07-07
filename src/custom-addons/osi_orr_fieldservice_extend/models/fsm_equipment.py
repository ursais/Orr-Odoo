# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class FSMEquipment(models.Model):
    _inherit = 'fsm.equipment'

    @api.multi
    def action_view_fsm_order(self):
        self.ensure_one()
        action = self.env.ref(
            'fieldservice.action_fsm_operation_order').read()[0]
        fsm_order_rec = self.env['fsm.order'].search([
            ('location_id', '=', self.location_id.id),
            ('equipment_id', '=', self.id)])
        action['domain'] = [('id', 'in',
                             fsm_order_rec and fsm_order_rec.ids)]
        return action

    @api.multi
    def action_view_fsm_recurring(self):
        self.ensure_one()
        action = self.env.ref(
            'fieldservice_recurring.action_fsm_recurring').read()[0]
        fsm_recurring_rec = self.env['fsm.recurring'].search([
            ('location_id', '=', self.location_id.id),
            ('equipment_id', '=', self.id)])
        action['domain'] = [('id', 'in',
                             fsm_recurring_rec and fsm_recurring_rec.ids)]
        return action
