# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class JobCostEstimate(models.TransientModel):
    _inherit = 'job.cost.estimate'

    @api.multi
    def create_estimation(self):
        """Overrite this method for populate analytic account, reference"""
        active_id = self.env['job.costing'].browse(
            self._context.get('active_id'))
        job_estimate_obj = self.env['sale.estimate.job']
        partner_id = self.partner_id
        pricelist_id = self.price_list_id
        company_id = active_id.company_id.id
        currency_id = active_id.currency_id.id
        project_id = active_id.project_id.id

        for rec in self:
            vals = {
                'partner_id': partner_id.id,
                'pricelist_id': pricelist_id.id,
                'estimate_date': fields.Date.today(),
                'company_id': company_id,
                'currency_id': currency_id,
                'project_id': project_id,
                'jobcost_id': active_id.id,
                'analytic_id': active_id.analytic_id.id,
                'reference': active_id.so_number,
                'description': active_id.notes_job,
            }
            estimate = job_estimate_obj.create(vals)
            rec._prepare_estimate_lines(estimate, active_id)
            estimate_lst = active_id.cost_estimate_ids.ids
            estimate_lst.append(estimate.id)
            active_id.write({
                'cost_estimate_ids': [(6, 0, estimate_lst)],
            })
