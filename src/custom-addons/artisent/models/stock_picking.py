# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    @api.multi
    def button_validate(self):
        for rec in self:
            if rec.picking_type_id.require_vehicle_id:
                if rec.fsm_vehicle_id:
                    picking = \
                        rec.with_context(vehicle_id=rec.fsm_vehicle_id.id)
                    res = super().button_validate()
                else:
                    raise UserError(_(
                        "You must provide the vehicle for this picking type."))
            res = super().button_validate()
        return res
