# Copyright 2018 Open Source Integrators (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

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

    @api.onchange('amount', 'payment_difference', 'payment_date')
    def onchange_payment_amount(self):
        if self.invoice_id \
                and self.invoice_id.payment_term_id \
                and self.invoice_id.payment_term_id.is_discount \
                and self.invoice_id.payment_term_id.line_ids:

            self.payment_difference_handling = 'open'
            self.writeoff_account_id = False
            self.writeoff_label = False

            for line in self.invoice_id.payment_term_id.line_ids:
                # Check payment date discount validation
                invoice_date = fields.Date.from_string(
                    self.invoice_id.date_invoice)
                till_discount_date = invoice_date + relativedelta(
                    days=line.discount_days)
                payment_date = fields.Date.from_string(self.payment_date)
                discount_amt = round(
                    (self.invoice_id.amount_untaxed_invoice_signed * line.discount) / 100.0,
                     2)
                payment_difference = self.payment_difference
                self.payment_difference = 0.0

                if payment_date <= till_discount_date:
                    #changing payment date
                    if not payment_difference and discount_amt:
                        self.payment_difference = discount_amt
                        self.payment_difference_handling = 'reconcile'
                        self.writeoff_account_id = \
                            line.discount_expense_account_id.id
                        self.writeoff_label = 'Payment Discount'
                    #customer is paying more
                    elif abs(payment_difference) < discount_amt:
                        self.payment_difference = abs(payment_difference)
                        self.payment_difference_handling = 'reconcile'
                        self.writeoff_account_id = \
                            line.discount_expense_account_id.id
                        self.writeoff_label = 'Payment Discount'
                    #ocustomer paying more than discount_amt
                    elif abs(payment_difference) > discount_amt:
                        self.payment_difference = abs(payment_difference)
                        self.payment_difference_handling = 'open'
                        self.writeoff_label = False
                    #customer paying more than discount_amt
                    elif abs(payment_difference) == discount_amt and \
                            discount_amt > 0:
                        self.payment_difference = abs(payment_difference)
                        self.payment_difference_handling = 'reconcile'
                        self.writeoff_account_id = \
                            line.discount_expense_account_id.id
                        self.writeoff_label = 'Payment Discount'
                else:
                    self.payment_difference = payment_difference

                self.amount = self.invoice_id.residual_signed - abs(self.payment_difference)

    def action_validate_invoice_payment(self):
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a "
                              "single invoice's payment."))
        res = super(AccountPayment, self).action_validate_invoice_payment()
        for payment in self:
            if payment.payment_difference_handling == 'reconcile':
                payment.invoice_id.write({'discount_taken': abs(payment.payment_difference),
                                          'discount_amt': 0})

        return res
