# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools.safe_eval import safe_eval


class JobcostInvoice(models.TransientModel):
    _inherit = 'jobcost.invoice'

    @api.multi
    def create_jobcost_invoice(self):
        res = super().create_jobcost_invoice()
        inv_domain = safe_eval(res.get('domain'))
        if inv_domain:
            invoice_obj = self.env['account.invoice']
            active_id = self._context.get('active_id')
            job_costing = self.env['job.costing'].browse(active_id)
            invoice_rec = invoice_obj.browse(
                inv_domain[0][2])
            for invoice in invoice_rec:
                invoice.analytic_tag_ids = [(6, 0, job_costing.analytic_tag_ids.ids)]
                invoice.project_id = job_costing.analytic_id.id
                for inv_line in invoice_rec.invoice_line_ids:
                    inv_line.account_analytic_id = job_costing.analytic_id.id
                    inv_line.analytic_tag_ids = [(6, 0, job_costing.analytic_tag_ids.ids)]
        return res
