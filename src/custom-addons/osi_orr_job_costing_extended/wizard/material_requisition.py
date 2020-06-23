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
            job_costing_rec = self.env['job.costing'].search([
                ('project_id', '=', job_order.project_id.id),
                ('analytic_id', '=', material_req_rec.analytic_account_id.id),
            ], limit=1)
            if self.operation_type == 'create' or self.operation_type == 'exist':
                for line in material_req_rec.requisition_line_ids:
                    job_cost_line_rec = self.env['job.cost.line'].search([
                        ('direct_id', '=', job_costing_rec.id),
                        ('product_id', '=', line.product_id.id),
                    ], limit=1)
                    seller_vendors = line.product_id.seller_ids.mapped('name')
                    line.write(
                        {'requisition_type': 'purchase',
                         'custom_job_costing_id': job_costing_rec.id,
                         'custom_job_costing_line_id': job_cost_line_rec.id,
                         'partner_id': [(6, 0, seller_vendors.ids)]
                         })
        return res
