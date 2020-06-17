# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class MaterialRequisition(models.TransientModel):
    _inherit = "material.purchase.requisition.wizard"

    @api.multi
    def action_create_reservation(self):
        res = super().action_create_reservation()
        material_req_obj = self.env['material.purchase.requisition']
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        job_order = self.env[active_model].browse(active_ids)
        if res.get('domain'):
            material_req_rec = material_req_obj.browse(
                res.get('domain')[0][2])
            so_rec = job_order.sale_line_id.order_id
            material_req_rec.analytic_account_id = so_rec.analytic_account_id
            if self.operation_type == 'create':
                for line in material_req_rec.requisition_line_ids:
                    line.write({'requisition_type': 'purchase'})  # To do
            elif self.operation_type == 'exist':
                pass  # To do
        return res
