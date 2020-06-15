# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_view_job_cost_sheet(self):
        self.ensure_one()
        action = self.env.ref(
            'odoo_job_costing_management.action_job_costing').read()[0]
        estimate_job = self.env['sale.estimate.job'].search([
            ('quotation_id', '=', self.id)])
        action['domain'] = [('id', 'in',
                             estimate_job and estimate_job.jobcost_id.ids)]
        return action

    @api.multi
    def action_view_job_estimate(self):
        self.ensure_one()
        estimate_job = self.env['sale.estimate.job'].search([
            ('quotation_id', '=', self.id)])
        return {
            'name': _('Job Estimates'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.estimate.job',
            'target': 'current',
            'res_id': estimate_job and estimate_job.id
        }
