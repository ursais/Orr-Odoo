# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

    sale_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Sale Order Line")
    product_id = fields.Many2one(
        'product.product', 'Product', ondelete='cascade',
        domain=[('type', 'in', ['product', 'consu', 'service'])], required=True,
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.fsm_order_id:
            if res.fsm_order_id.sale_id:
                res.sale_id = res.fsm_order_id.sale_id
        if res.sale_id and not res.sale_order_line_id:
            sol = self.env['sale.order.line'].create(self._get_sol_vals(res))
            res.fsm_order_id.write({'sale_order_line_ids': [(4, sol.id)]})
            res.sale_line_id = sol
        return res

    def _get_sol_vals(self, stock_request):
        return {
            'name': stock_request.product_id.name,
            'product_id': stock_request.product_id.id,
            'order_id': stock_request.sale_id.id,
            'price_unit': stock_request.product_id.list_price,
            'product_uom_qty': stock_request.product_uom_qty,
            'customer_lead': 0.0,
            'status': 'done',
            'tax_id': [(4, self.env.ref('avatax_connector.avatax').id)]
        }

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.sale_id:
            res.update({
                'sale_id': self.sale_id.id,
            })
        return res

    def _prepare_procurement_group_values(self):
        res = super()._prepare_procurement_group_values()
        if self.fsm_order_id:
            if self.fsm_order_id.sale_id:
                res.update({'sale_id': self.fsm_order_id.sale_id.id})
        return res

    @api.onchange('product_id')
    def _set_sol_domain(self):
        if self.fsm_order_id.sale_id:
            return {
                    'domain' : {
                    'sale_order_line_id' : [('order_id', '=', self.fsm_order_id.sale_id.id)]}
                    }
        else:
            return {}

    @api.onchange('sale_order_line_id')
    def onchange_sale_order_line_id(self):
        if self.sale_order_line_id:
            self.product_id = self.sale_order_line_id.product_id


# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    sale_id = fields.Many2one('sale.order', string="Sale Order")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.fsm_order_id:
            if res.fsm_order_id.sale_id:
                res.sale_id = res.fsm_order_id.sale_id
        return res

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        # Can SM from a SR on an FSO have more than one SR?
        if res.stock_request_ids:
            res.sale_line_id = res.stock_request_ids[0].sale_order_line_id
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fsm_order_id = fields.Many2one(related="group_id.fsm_order_id",
                                   string="Field Service Order", store=True, copy=True)

class StockRequest(models.AbstractModel):
    _inherit = "stock.request.abstract"
    
    product_id = fields.Many2one(
        'product.product', 'Product', ondelete='cascade',
        domain=[('type', 'in', ['product', 'consu', 'service'])], required=True,
    )
