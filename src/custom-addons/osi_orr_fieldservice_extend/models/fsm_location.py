# Tasks
# Agreement
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    fso_count = fields.Integer(string='FSM Orders',
                                       compute='_compute_fso_count')

    @api.multi
    def _compute_fso_count(self):
        for loc in self:
            loc.fso_count = self.env['fsm.order'].search_count([('location_id', '=', loc.id)])

    @api.multi
    def action_view_fso(self):
        action = self.env.ref('fieldservice.action_fsm_operation_order').read()[0]
        order_ids = self.env['fsm.order'].search([('location_id', '=', self.id)])
        if len(order_ids) > 1:
            action['domain'] = [('id', 'in', order_ids.ids)]
        elif order_ids:
            action['views'] = [(self.env.ref('fieldservice.fsm_order_form').id,
                                'form')]
            action['res_id'] = order_ids[0]
        return action

    so_count = fields.Integer(string='Sales Orders',
                                       compute='_compute_so_count')

    @api.multi
    def _compute_so_count(self):
        for loc in self:
            loc.so_count = self.env['sale.order'].search_count([('fsm_location_id', '=', loc.id)])

    @api.multi
    def action_view_so(self):
        action = self.env.ref('sale.action_orders').read()[0]
        order_ids = self.env['sale.order'].search([('fsm_location_id', '=', self.id)])
        if len(order_ids) > 1:
            action['domain'] = [('id', 'in', order_ids.ids)]
        elif order_ids:
            action['views'] = [(self.env.ref('sale.view_order_form').id,
                                'form')]
            action['res_id'] = order_ids[0]
        return action

    rfso_count = fields.Integer(string='Recurring FSM Orders',
                                       compute='_compute_rfso_count')

    @api.multi
    def _compute_rfso_count(self):
        for loc in self:
            loc.rfso_count = self.env['fsm.recurring'].search_count([('location_id', '=', loc.id)])

    @api.multi
    def action_view_rfso(self):
        action = self.env.ref('fieldservice_recurring.action_fsm_recurring').read()[0]
        order_ids = self.env['fsm.recurring'].search([('location_id', '=', self.id)])
        if len(order_ids) > 1:
            action['domain'] = [('id', 'in', order_ids.ids)]
        elif order_ids:
            action['views'] = [(self.env.ref('fieldservice_recurring.fsm_recurring_form_view').id,
                                'form')]
            action['res_id'] = order_ids[0]
        return action

    agreement_count = fields.Integer(string='Agreements',
                                     compute='_compute_agreement_count')

    @api.multi
    def _compute_agreement_count(self):
        for loc in self:
            loc.agreement_count = self.env['agreement'].search_count([('fsm_location_id', '=', loc.id)])

    @api.multi
    def action_view_agreements(self):
        action = self.env.ref('agreement.agreement_action').read()[0]
        order_ids = self.env['agreement'].search([('fsm_location_id', '=', self.id)])
        if len(order_ids) > 1:
            action['domain'] = [('id', 'in', order_ids.ids)]
        elif order_ids:
            action['views'] = [(self.env.ref('agreement_legal.partner_agreement_form_view').id,
                                'form')]
            action['res_id'] = order_ids[0]
        return action
