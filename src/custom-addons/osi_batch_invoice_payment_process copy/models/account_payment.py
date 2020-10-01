# -*- coding: utf-8 -*-
# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    valid_discount_date = fields.Date(string='Valid Discount Date')

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for rec in self:
            if rec.payment_term_id and rec.date_invoice:
                # Check payment date discount validation
                invoice_date = fields.Date.from_string(
                    rec.date_invoice)
                # Get discount validity days from payment terms
                for line in rec.payment_term_id.line_ids:
                    rec.valid_discount_date = invoice_date + relativedelta(
                        days=line.discount_days)
        return res

class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    @api.multi
    def write(self, vals):
        res = super(AccountPaymentTermLine, self).write(vals)
        if vals.get('discount_days'):
            for item in self:
                # get all invoice related to this payment term and update
                # validity discount date
                invoice_ids = self.env['account.invoice'].search([('state','=','open'),
                                                                  ('payment_term_id','=',item.payment_id.id)])
                for inv in invoice_ids:
                    # Check payment date discount validation
                    invoice_date = fields.Date.from_string(
                        inv.date_invoice)
                    # Update discount validity days
                    for line in inv.payment_term_id.line_ids:
                        inv.valid_discount_date = invoice_date + relativedelta(
                            days=line.discount_days)
        return res
