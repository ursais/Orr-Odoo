# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class JobCosting(models.Model):
    _inherit = 'job.costing'

    @api.depends(
        'job_cost_line_ids',
        'job_cost_line_ids.product_qty',
        'job_cost_line_ids.sale_price',
    )
    def _compute_total_material_sale(self):
        for rec in self:
            rec.total_material_sale = sum(
                [(p.product_qty * p.sale_price)
                 for p in rec.job_cost_line_ids])

    @api.depends(
        'job_overhead_line_ids',
        'job_overhead_line_ids.product_qty',
        'job_overhead_line_ids.sale_price'
    )
    def _compute_total_overhead_sale(self):
        for rec in self:
            rec.total_overhead_sale = sum(
                [(p.product_qty * p.sale_price)
                 for p in rec.job_overhead_line_ids])

    @api.depends(
        'job_labour_line_ids',
        'job_labour_line_ids.hours',
        'job_labour_line_ids.sale_price'
    )
    def _compute_total_labor_sale(self):
        for rec in self:
            rec.total_labor_sale = sum(
                [(p.hours * p.sale_price)
                 for p in rec.job_labour_line_ids])

    @api.depends(
        'total_material_sale',
        'total_labor_sale',
        'total_overhead_sale'
    )
    def _compute_total_sale(self):
        for rec in self:
            rec.total_sale = rec.total_material_sale + \
                rec.total_labor_sale + rec.total_overhead_sale

    @api.depends(
        'total_sale',
        'jobcost_total',
    )
    def _compute_total_margin(self):
        for rec in self:
            rec.total_margin = rec.total_sale - \
                rec.jobcost_total

    @api.multi
    def _timesheet_line_count(self):
        hr_timesheet_obj = self.env['account.analytic.line']
        for timesheet_line in self:
            timesheet_line.timesheet_line_count = hr_timesheet_obj.\
                search_count([('project_id', '=', self.project_id.id)])

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        copy=False
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=False
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=False,
        domain=[('customer', '=', True)],
        copy=False
    )
    job_cost_line_ids = fields.One2many(
        'job.cost.line',
        'direct_id',
        string='Direct Materials',
        copy=True,
        domain=[('job_type', '=', 'material')],
    )
    job_labour_line_ids = fields.One2many(
        'job.cost.line',
        'direct_id',
        string='Direct Materials',
        copy=True,
        domain=[('job_type', '=', 'labour')],
    )
    job_overhead_line_ids = fields.One2many(
        'job.cost.line',
        'direct_id',
        string='Direct Materials',
        copy=True,
        domain=[('job_type', '=', 'overhead')],
    )
    total_material_sale = fields.Float(
        string='Total Material Sale',
        compute='_compute_total_material_sale',
        store=True,
    )
    total_labor_sale = fields.Float(
        string='Total Labour Sale',
        compute='_compute_total_labor_sale',
        store=True,
    )
    total_overhead_sale = fields.Float(
        string='Total Overhead Sale',
        compute='_compute_total_overhead_sale',
        store=True,
    )
    total_sale = fields.Float(
        string='Total Sale',
        compute='_compute_total_sale',
        store=True,
    )
    total_margin = fields.Float(
        string='Margin',
        compute='_compute_total_margin',
        store=True,
    )
    sale_order_count = fields.Integer(
        string='Sale Order Ids',
        compute='_compute_sale_order_count',
        store=True,
    )

    @api.multi
    def _compute_sale_order_count(self):
        for order_id in self:
            sale_ids = []
            for estimate_id in order_id.cost_estimate_ids:
                sale_ids.append(estimate_id.quotation_id.id)
            order_id.sale_order_ids = len(sale_ids)

    @api.multi
    def action_view_sale_orders(self):
        cost_estimate_ids = self.env['sale.estimate.job'].search([('jobcost_id', '=', self.id)])
        sale_order_ids = [estimate_id.quotation_id.id for estimate_id in cost_estimate_ids if estimate_id.quotation_id]
        action = self.env.ref('sale.action_orders').read()[0]
        if len(sale_order_ids) == 1:
            action['views'] = [(
                self.env.ref('sale.view_order_form').id,
                'form')]
            action['res_id'] = sale_order_ids[0]
        else:
            action['domain'] = [('id', 'in', sale_order_ids)]
        return action

    @api.multi
    def action_view_hr_timesheet_line(self):
        action = super().action_view_hr_timesheet_line()
        action['domain'] = [('project_id', '=', self.project_id.id)]
        return action


class JobCostLine(models.Model):
    _inherit = 'job.cost.line'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=True,
        required=True,
    )
    description = fields.Char(
        string='Description',
        copy=True,
    )
    reference = fields.Char(
        string='Reference',
        copy=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        copy=True,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=True,
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=True,
    )
    sale_price = fields.Float(
        string='Sale Price / Unit',
        copy=True,
    )
