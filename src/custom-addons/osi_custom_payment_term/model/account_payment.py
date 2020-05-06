# Copyright 2018 Open Source Integrators (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
    )
    discount_amt = fields.Monetary(store=True)

    @api.model
    def default_get(self, fields):
        res = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids',
                                                       res.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            res['invoice_id'] = invoice and invoice['id']
            res['discount_amt'] = invoice['discount_amt']
        return res

    @api.onchange('currency_id')
    def _onchange_currency(self):
        super(AccountPayment, self)._onchange_currency()
        if self.currency_id == self.invoice_id.currency_id:
            self.amount = self.discount_amt

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(AccountPayment, self)._onchange_journal()
        if self.journal_id == self.invoice_id.journal_id:
            self.amount = self.discount_amt
        return res

    @api.onchange('amount', 'payment_difference', 'payment_date')
    def onchange_payment_amount(self):
        if self.invoice_id \
                and self.invoice_id.payment_term_id \
                and self.invoice_id.payment_term_id.is_discount \
                and self.invoice_id.payment_term_id.line_ids \
                and self.payment_difference:

            self.payment_difference_handling = 'open'
            self.writeoff_account_id = False
            self.writeoff_label = False


            discount_information = self.invoice_id.payment_term_id._check_payment_term_discount(
                self.invoice_id, self.invoice_id.date_invoice)
            discount_amt = discount_information[0]
            discount_account_id = discount_information[1]
            self.amount = discount_information[2] - discount_amt
            if discount_amt > 0.0:
                # compute payment difference
                # payment_difference = self.payment_difference
                if self.invoice_id.type in ('in_invoice','out_refund'):
                    self.payment_difference = discount_amt * -1
                elif self.invoice_id.type in ('out_invoice','in_refund'):
                    self.payment_difference = discount_amt
                # self.amount = discount_information[2] - discount_amt
                # is payment difference applicable for a discount
                if self.payment_difference <= discount_amt:
                    self.payment_difference_handling = 'reconcile'
                    self.writeoff_account_id = discount_account_id
                    self.writeoff_label = 'Payment Discount'
