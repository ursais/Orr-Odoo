# Copyright (C) 2019 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    analytic_segment_one_id = fields.Many2one(
        'analytic.segment.one',
        string='Job Type')

    @api.model
    def create(self, vals):
        # Get Sale Order Warehouse Account ,
        # if Invoice created from Sale Order
        if self._context.get('active_model', False) and \
                self._context['active_model'] == 'sale.order':
            so_id = self.env['sale.order'].browse(
                self._context.get('active_id', False)
            )
            if so_id:
                wh_acc = so_id.analytic_account_id and \
                         so_id.analytic_account_id.id or \
                         False
                vals.update(
                    {'account_analytic_id': wh_acc}
                )

        return super(AccountInvoiceLine, self).create(vals)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    analytic_segment_one_id = fields.Many2one(
        'analytic.segment.one',
        string='Job type')


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    analytic_segment_one_id = fields.Many2one(
        'analytic.segment.one',
        string='Job type',
        copy=False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_segment_one_id = fields.Many2one(
        'analytic.segment.one',
        string='Job type')
