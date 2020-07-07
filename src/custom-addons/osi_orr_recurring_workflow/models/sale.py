# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for order in self:
            agreement_id = self.env['agreement'].\
                    search([('sale_id', '=', order.id)])
            for recurring_id in order.fsm_recurring_ids:
                recurring_id.agreement_id = agreement_id
            for line_id in order.order_line:
                line_id.fsm_equipment_id.agreement_id = agreement_id
                for sp_id in agreement_id.serviceprofile_ids:
                    if sp_id.product_id == line_id.product_id.product_tmpl_id:
                        line_id.fsm_equipment_id.serviceprofile_id = sp_id
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    fsm_equipment_id = fields.Many2one('fsm.equipment', 'Equipment')
    fsm_location_id = fields.Many2one(related='order_id.fsm_location_id', store=True)

    def _field_create_fsm_recurring_prepare_values(self):
        res =  super()._field_create_fsm_recurring_prepare_values()
        if self.fsm_equipment_id:
            res['fsm_equipment_id'] = self.fsm_equipment_id.id
        if self.order_id:
            if self.order_id.agreement_id:
                res['agreement_id'] = self.order_id.agreement_id.id
        return res
