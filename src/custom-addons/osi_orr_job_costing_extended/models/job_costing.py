# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class JobCosting(models.Model):
    _inherit = 'job.costing'

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
