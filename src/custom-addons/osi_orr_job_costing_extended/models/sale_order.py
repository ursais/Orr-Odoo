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

    def _create_task_for_non_service_product(
            self, project, non_service_task_list):
        values = {
            'name': 'Materials',
            'partner_id': self.partner_id.id,
            'email_from': self.partner_id.email,
            'description': 'Materials',
            'project_id': project.id,
            'company_id': self.company_id.id,
            'material_plan_ids': non_service_task_list,
        }
        task = self.env['project.task'].sudo().create(values)
        self.write({'task_id': task.id})
        # post message on task
        task_msg = _("This task has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a> (%s)") % (
            self.id, self.name, 'Materials')
        task.message_post(body=task_msg)
        return task

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for so in self:
            non_service_task_list = []
            estimate_job = self.env['sale.estimate.job'].search([
                ('quotation_id', '=', self.id)], limit=1)
            project = self.env['project.project'].search([
                ('sale_order_id', '=', so.id)], limit=1)
            if so.analytic_account_id:
                so.analytic_account_id.total_progress_account = so.amount_total
            if not estimate_job and project and so.analytic_account_id:
                project.name = so.analytic_account_id.name
            if project and estimate_job:
                project.name = estimate_job.jobcost_id.name
                project.analytic_account_id.name = estimate_job.jobcost_id.name
                project.analytic_tag_ids = [(6, 0, so.analytic_tag_ids.ids)]
                estimate_job.project_id = project.id
                estimate_job.analytic_id = project.analytic_account_id.id
                estimate_job.jobcost_id.project_id = project.id
                estimate_job.jobcost_id.analytic_id = \
                    project.analytic_account_id.id
                for line in so.order_line:
                    if line.product_id.type != 'service':
                        non_service_task_list.append(
                            (0, 0, {
                                'product_id': line.product_id.id,
                                'description': line.name,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'requisition_type': 'purchase',
                                'custom_job_cost_id': estimate_job.jobcost_id.id
                            }))
                so._create_task_for_non_service_product(
                    project, non_service_task_list)
        return result

    @api.multi
    def action_view_project_ids(self):
        self.ensure_one()
        project_ids = self.env['project.project'].search([('sale_order_id', '=', self.id)])
        action = self.env.ref('project.open_view_project_all').\
            read()[0]
        if action.get('context', False):
            action['context'] = self.env.context.copy()
        if len(project_ids) == 0 or len(project_ids) > 1:
            action['domain'] = [('id', 'in', project_ids.ids)]
        elif project_ids:
            action['views'] = [(self.env.ref('project.edit_project').id, 'form')]
            action['res_id'] = project_ids.id
        return action

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super().action_invoice_create(grouped, final)
        inv = self.env['account.invoice'].browse(res[0])
        estimate_job = self.env['sale.estimate.job'].search([('quotation_id', '=', self.id)], limit=1)
        if estimate_job:
            inv.job_cost_id = estimate_job.jobcost_id
        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super()._create_invoice(order, so_line, amount)
        self.env['account.invoice'].browse(res[0])
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if len(sale_orders) == 1:
            estimate_job = self.env['sale.estimate.job'].search([('quotation_id', '=', sale_orders.id)], limit=1)
            res.job_cost_id = estimate_job.jobcost_id
        return res
