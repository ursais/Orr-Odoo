"""Stock Quantity."""
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class StockQuantityReport(models.TransientModel):
    """Stock Quantity Report."""

    _name = 'stock.quantity.report'
    _description = 'Stock Quantity Report'

    category_id = fields.Many2one(
        'product.category',
        string='Category',
        required=True)
    qty_on_hand = fields.Float("On Hand Quantity", required=True)
    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number')

    def scrap_report_view(self):
        """Get the Scrap report details."""
        self.ensure_one()

        form_view_id = self.env.ref('osi_scrap_automation.view_scrap_stock_quant_form').id
        tree_view_id = self.env.ref('osi_scrap_automation.view_scrap_stock_quant_tree').id
        domain = [
            ('product_id.categ_id', '=', self.category_id.id),
            ('quantity', '<=', self.qty_on_hand),
            ('quantity', '>', 0)]
        if self.lot_id:
            domain.append(('lot_id', '=', self.lot_id.id))
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': _('Scrap Report'),
            'res_model': 'stock.quant',
            'domain': domain,
        }
        return action
