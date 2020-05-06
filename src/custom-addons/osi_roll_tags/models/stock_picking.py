# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    hide_roll_tags_button = fields.Boolean(compute='_compute_picking_type_id')

    def _compute_picking_type_id(self):
        for picking_id in self:
            if picking_id.picking_type_id:
                if picking_id.picking_type_id.code == 'incoming':
                    picking_id.hide_roll_tags_button = False
                else:
                    picking_id.hide_roll_tags_button = True
            else:
                picking_id.hide_roll_tags_button = True
            

    def print_roll_tags(self):
        return self.env.ref('osi_roll_tags.action_roll_tags').\
            report_action(self)
