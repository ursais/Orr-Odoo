# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )

    @api.multi
    def _compute_revised_estimate(self):
        for rec in self:
            so_rec = rec.sale_order_id
            if so_rec and so_rec.state == 'sale':
                total_purchase_price = 0.0
                for so_line in so_rec.order_line:
                    total_purchase_price += so_line.purchase_price
                rec.revised_estimate = total_purchase_price

    @api.multi
    def _compute_revised_contract(self):
        for rec in self:
            so_rec = rec.sale_order_id
            if so_rec and so_rec.state == 'sale':
                rec.revised_contract = so_rec.amount_untaxed

    @api.depends('job_cost_ids')
    def _compute_original_estimate(self):
        for rec in self:
            if rec.job_cost_ids:
                count_jobcost_total = 0.0
                for cost_sheet_rec in rec.job_cost_ids:
                    count_jobcost_total += cost_sheet_rec.jobcost_total
                rec.original_estimate = count_jobcost_total

    @api.depends('job_cost_ids')
    def _compute_original_contract(self):
        for rec in self:
            if rec.job_cost_ids:
                count_total_sale = 0.0
                for cost_sheet_rec in rec.job_cost_ids:
                    count_total_sale += cost_sheet_rec.total_sale
                rec.original_contract = count_total_sale

    @api.depends('costs', 'revised_estimate')
    def _compute_calculated_complete(self):
        for rec in self:
            if rec.costs and rec.revised_estimate:
                rec.calculated_complete = rec.costs / rec.revised_estimate

    @api.depends('revised_contract', 'calculated_complete')
    def _compute_revenue_earned(self):
        for rec in self:
            rec.revenue_earned = rec.revised_contract * rec.calculated_complete

    @api.depends('revenue_earned', 'invoiced_no_tax')
    def _compute_over_under_billed(self):
        for rec in self:
            rec.over_under_billed = rec.revenue_earned - rec.invoiced_no_tax

    @api.depends('revised_estimate', 'costs')
    def _compute_projected_cost_complete(self):
        for rec in self:
            rec.projected_cost_complete = rec.revised_estimate - rec.costs

    @api.depends('revised_contract', 'revised_estimate')
    def _compute_projected_profit_loss(self):
        for rec in self:
            rec.projected_profit_loss = \
                rec.revised_contract - rec.revised_estimate

    @api.depends('revised_contract', 'revised_estimate')
    def _compute_projected_profit(self):
        for rec in self:
            if rec.revised_contract:
                rec.projected_profit = (
                    rec.revised_contract - rec.revised_estimate
                ) / rec.revised_contract

    @api.multi
    def _compute_last_cost_date(self):
        for rec in self:
            move_line_obj = self.env['account.move.line']
            user_type_income = self.env.ref(
                'account.data_account_type_direct_costs',
                raise_if_not_found=False)
            for rec in self:
                move_line_rec = move_line_obj.search(
                    [('analytic_account_id', '=', rec.analytic_account_id.id),
                     ('account_id.user_type_id', '=',
                        user_type_income and user_type_income.id)],
                    order="id desc", limit=1)
                if move_line_rec:
                    rec.last_cost_date = move_line_rec.move_id.date

    @api.multi
    def _compute_costs(self):
        move_line_obj = self.env['account.move.line']
        user_type_income = self.env.ref(
            'account.data_account_type_direct_costs',
            raise_if_not_found=False)
        for rec in self:
            move_line_rec = move_line_obj.search(
                [('analytic_account_id', '=', rec.analytic_account_id.id),
                 ('account_id.user_type_id', '=',
                    user_type_income and user_type_income.id)])
            compute_total_costs = 0.0
            for line_rec in move_line_rec:
                compute_total_costs += line_rec.debit
            rec.costs = compute_total_costs

    @api.multi
    def _compute_invoiced_no_tax(self):
        invoice_obj = self.env['account.invoice']
        for rec in self:
            if rec.analytic_account_id:
                invoice_rec = invoice_obj.search(
                    [('project_id', '=', rec.analytic_account_id.id),
                     ('state', 'in', ('draft', 'paid'))])
                count_amount_untaxed = 0.0
                for invoice in invoice_rec:
                    count_amount_untaxed += invoice.amount_untaxed
                rec.invoiced_no_tax = count_amount_untaxed

    @api.multi
    def _compute_last_date_invoiced(self):
        invoice_obj = self.env['account.invoice']
        for rec in self:
            if rec.analytic_account_id:
                invoice_rec = invoice_obj.search(
                    [('project_id', '=', rec.analytic_account_id.id),
                     ('state', '=', 'open')],
                    order="id desc", limit=1)
                if invoice_rec:
                    rec.last_date_invoiced = invoice_rec.date_invoice

    @api.multi
    def _compute_payment_received(self):
        invoice_obj = self.env['account.invoice']
        for rec in self:
            invoice_rec = invoice_obj.search(
                [('project_id', '=', rec.analytic_account_id.id),
                 ('state', 'in', ('draft', 'paid'))])
            count_payment_received = 0.0
            for invoice in invoice_rec:
                for payment in invoice.payment_ids:
                    count_payment_received += payment.amount
            rec.payment_received = count_payment_received

    @api.multi
    def _compute_last_payment_received(self):
        invoice_obj = self.env['account.invoice']
        payment_obj = self.env['account.payment']
        for rec in self:
            invoice_rec = invoice_obj.search(
                [('project_id', '=', rec.analytic_account_id.id),
                 ('state', 'in', ('draft', 'paid'))])
            payment_rec = payment_obj.search(
                [('invoice_ids', 'in', invoice_rec.ids)],
                order="id desc", limit=1)
            rec.last_payment_received = payment_rec.payment_date

    projected_profit = fields.Float(
        string='Projected Profit',
        compute='_compute_projected_profit',
    )
    projected_profit_loss = fields.Float(
        string='Project Profit (Loss)',
        compute='_compute_projected_profit_loss',
    )
    projected_cost_complete = fields.Float(
        string='Projected Cost to Complete',
        compute='_compute_projected_cost_complete',
    )
    over_under_billed = fields.Float(
        string='Over/Under Billed',
        compute='_compute_over_under_billed',
    )
    revenue_earned = fields.Float(
        string='Revenue Earned',
        compute='_compute_revenue_earned',
    )
    calculated_complete = fields.Float(
        string='Calculated Complete',
        compute='_compute_calculated_complete',
    )
    revised_contract = fields.Float(
        string='Revised Contract',
        compute='_compute_revised_contract'
    )
    original_contract = fields.Float(
        string='Original Contract',
        compute='_compute_original_contract',
    )
    revised_estimate = fields.Float(
        string='Revised Estimate',
        compute='_compute_revised_estimate',
    )
    original_estimate = fields.Float(
        string='Original Estimate',
        compute='_compute_original_estimate',
    )
    last_cost_date = fields.Date(
        string='Last Cost Date',
        compute='_compute_last_cost_date',
    )
    costs = fields.Float(
        string='Costs',
        compute='_compute_costs',
    )
    last_date_invoiced = fields.Date(
        string='Last Date Invoiced',
        compute='_compute_last_date_invoiced',
    )
    invoiced_no_tax = fields.Float(
        string='Invoiced (no tax)',
        compute='_compute_invoiced_no_tax',
    )
    last_payment_received = fields.Date(
        string='Last Payment Received',
        compute='_compute_last_payment_received',
    )
    payment_received = fields.Float(
        string='Payment received',
        compute='_compute_payment_received',
    )
