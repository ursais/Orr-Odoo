# -*- coding: utf-8 -*-
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import Warning


class StockMove(models.Model):
    _inherit = "stock.move"

    no_of_lines = fields.Float(string='No. of Lines')

    def compute_operation_lines(self):
        """
        This function will split Detailed operation lines as requested.
        And will split qty equally among all lines based on
        Initial demand and No of lines fields
        :return:
        """
        if self and self.no_of_lines > 0.0:
            if len(self.move_line_ids) > 0:
                raise Warning('Warning! \nPlease remove all move lines to Compute!')
            else:
                line_qty = (self.product_uom_qty / self.no_of_lines)
                initial_demand = self.product_uom_qty
                if self.no_of_lines > initial_demand:
                    raise Warning('Warning! \nNo of Lines can not be more than Initial Demand!')
                # If not serialize product
                if self.product_id.tracking != 'serial':
                    for i in range(0, int(self.no_of_lines)):
                        self.env['stock.move.line'].create(
                            self._prepare_move_line_vals(quantity=line_qty))
                else:
                    # No of lines should be same as Initial demand
                    if self.no_of_lines != initial_demand:
                        raise Warning('Warning! \nNo of Lines should match Initial Demand for Product Tracking '
                                      '"Serial"!')
                    else:
                        for i in range(0, int(self.no_of_lines)):
                            self.env['stock.move.line'].create(
                                self._prepare_move_line_vals(quantity=line_qty))
        else:
            raise Warning('Warning! \nPlease enter valid No. of Lines to Compute!')

    def unlink_move_lines(self):
        if self.move_line_ids:
            # Unlink all lines
            self.move_line_ids.unlink()

        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        # Return Current view
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    dye_lot = fields.Char(string='Dye Lot')
