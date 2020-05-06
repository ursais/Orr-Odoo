# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    hide_roll_tags_button = fields.\
        Boolean(compute='_compute_picking_type_id')

    def _compute_picking_type_id(self):
        for lot_id in self:
            move = self.env['stock.move.line'].\
                search([('lot_name', '=', lot_id.name)],
                       order="date desc")
            if move:
                lot_id.hide_roll_tags_button = False
            else:
                lot_id.hide_roll_tags_button = True
                
    def print_last_roll_tag(self):
        move = self.env['stock.move.line'].\
            search([('lot_name', '=', self.name)], order="date desc")[0]
        return self.env.ref('osi_roll_tags.action_roll_tags_sn').\
            report_action(move)
