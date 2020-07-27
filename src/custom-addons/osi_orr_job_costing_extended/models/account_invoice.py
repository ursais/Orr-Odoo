# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _compute_revised_budget(self):
        project_obj = self.env['project.project']
        for rec in self:
            project_rec = project_obj.search(
                [('analytic_account_id', '=', rec.project_id.id)], limit=1)
            if project_rec:
                rec.revised_budget = project_rec.revised_contract

    @api.multi
    def _compute_invoiced(self):
        project_obj = self.env['project.project']
        for rec in self:
            project_rec = project_obj.search(
                [('analytic_account_id', '=', rec.project_id.id)], limit=1)
            if project_rec:
                rec.invoiced = project_rec.invoiced_no_tax

    @api.depends('revised_budget', 'invoiced')
    def _compute_remaining_budget(self):
        for rec in self:
            rec.remaining_budget = rec.revised_budget - rec.invoiced

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )
    revised_budget = fields.Float(
        string='Revised Budget',
        compute='_compute_revised_budget'
    )
    invoiced = fields.Float(
        string='Validated Invoices',
        compute='_compute_invoiced'
    )
    remaining_budget = fields.Float(
        string='Remaining Budget',
        compute='_compute_remaining_budget'
    )
