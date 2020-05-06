# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _prepare_payment_line_vals(self, payment_order):
        vals = super(AccountMoveLine, self)._prepare_payment_line_vals(
            payment_order)
        invoice = self.invoice_id
        discount_amt = 0
        amount_currency = vals.get('amount_currency')
        if invoice \
                and invoice.payment_term_id \
                and invoice.payment_term_id.is_discount \
                and invoice.payment_term_id.line_ids:
            discount_information = invoice.payment_term_id._check_payment_term_discount(
                invoice, self._context.get('payment_date') or invoice.date_invoice)
            discount_amt = discount_information[0]
        vals.update({'discount_amount': discount_amt,
                     'amount_currency': amount_currency - discount_amt})
        return vals
