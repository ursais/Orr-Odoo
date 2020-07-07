# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Copy SO Lines onto FSM Order
    def _field_create_fsm_order_prepare_values(self):
        res = super()._field_create_fsm_order_prepare_values()
        res.update({
            'sale_order_line_ids': [(6, 0, self.order_line.ids)],
            'request_early': self.request_early,
            'service_requirement': self.service_requirement,
            'warehouse_id': self.warehouse_id.id,
            'scheduled_date_start': self.request_early,
            'todo': self.fsm_info,
            'template_id': self.get_fsm_order_template()
        })
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_to_invoice_fsm = fields.Float(
        string='Done Quantity',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    @api.depends('qty_delivered_method', 'qty_delivered_manual', 'analytic_line_ids.so_line', 'analytic_line_ids.unit_amount', 'analytic_line_ids.product_uom_id')
    def _compute_qty_delivered(self):
        res = super()._compute_qty_delivered()
        for order in self:
            if order.qty_delivered:
                order.qty_to_invoice_fsm = order.qty_delivered
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        # Append sol to FSO if exist
        if res and res.order_id and res.order_id.fsm_order_ids:
            for fsm_id in res.order_id.fsm_order_ids:
                fsm_id.sale_order_line_ids = [(4, res.id)]
        return res