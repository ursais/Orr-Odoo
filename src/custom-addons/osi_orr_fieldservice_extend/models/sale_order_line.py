# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _field_create_fsm_recurring_prepare_values(self):
        values = super(
            SaleOrderLine, self)._field_create_fsm_recurring_prepare_values()
        recurr_group_rec = self.env['fsm.recurring.group'].search(
            [('name', '=', self.order_id.name)], limit=1)
        if not recurr_group_rec:
            recurr_group_rec = self.env['fsm.recurring.group'].create(
                {'name': self.order_id.name})
        if recurr_group_rec:
            values.update({'group_id': recurr_group_rec.id})
        return values
