# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    analytic_segment_two_id = fields.Many2one(
        'analytic.segment.two',
        string='Warehouse Account')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    analytic_segment_two_id = fields.Many2one(
        'analytic.segment.two',
        string='Warehouse Account')


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    analytic_segment_two_id = fields.Many2one(
        'analytic.segment.two',
        string='Warehouse Account',
        copy=False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_segment_two_id = fields.Many2one(
        'analytic.segment.two',
        string='Warehouse Account')

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    po_ref = fields.Char("PO Reference")
