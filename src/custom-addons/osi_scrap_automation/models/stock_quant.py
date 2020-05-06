"""Stock Quantity."""
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models, _


class StockQuant(models.Model):
    """Stock Quant."""

    _inherit = 'stock.quant'

    category_id = fields.Many2one(
        'product.category',
        related='product_id.categ_id',
        string='Category',
        readonly=True)

    def _scrap_order(self):
        stock_scrap = self.env['stock.scrap']

        scrap_ids = []
        active_ids = self._context.get('active_ids') or []
        for rec in self.browse(active_ids):
            scrap_id = stock_scrap.create({
                'product_id': rec.product_id.id,
                'scrap_qty': rec.quantity,
                'product_uom_id': rec.product_id.uom_id.id})
            scrap_ids.append(scrap_id.id)

        form_view_id = self.env.ref('stock.stock_scrap_form_view').id
        tree_view_id = self.env.ref('stock.stock_scrap_tree_view').id
        domain = [('id', 'in', scrap_ids)]
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': _('Scrap'),
            'res_model': 'stock.scrap',
            'domain': domain,
        }
        return action
