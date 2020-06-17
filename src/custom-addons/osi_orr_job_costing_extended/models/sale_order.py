# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )

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

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for so in self:
            estimate_job = self.env['sale.estimate.job'].search([
                ('quotation_id', '=', self.id)], limit=1)
            project = self.env['project.project'].search([
                ('sale_order_id', '=', so.id)], limit=1)
            if project:
                project.name = estimate_job.jobcost_id.name
                project.analytic_account_id.name = estimate_job.jobcost_id.name
                project.analytic_tag_ids = [(6, 0, so.analytic_tag_ids.ids)]
                estimate_job.project_id = project.id
                estimate_job.analytic_id = project.analytic_account_id.id
                estimate_job.jobcost_id.project_id = project.id
                estimate_job.jobcost_id.analytic_id = project.analytic_account_id.id
        return result
