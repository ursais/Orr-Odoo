# -*- coding: utf-8 -*-
# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta
from datetime import datetime

try:
    from num2words import num2words
except ImportError:
    logging.getLogger(__name__).warning("The num2words python library is not\
     installed.")
    num2words = None

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

# Since invoice amounts are unsigned,
# this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class InvoiceCustomerPaymentLine(models.TransientModel):
    _inherit = "invoice.customer.payment.line"

    @api.onchange('payment_difference_handling')
    def onchange_payment_diff_handling(self):
        """
            Special case: When payment diff amount is 0, payment difference
            handling should be in 'open' action
         """
        if self.payment_difference_handling and\
            self.payment_difference_handling == 'reconcile' and\
            self.payment_difference == 0.0:
            # Change handling difference
            self.payment_difference_handling = 'open'

    @api.onchange('payment_difference')
    def onchange_payment_difference(self):
        """
            Special case: When payment diff amount is 0, payment difference
            handling should be in 'open' action
         """
        if self.payment_difference_handling and \
                self.payment_difference_handling == 'reconcile' and \
                self.payment_difference == 0.0:
            # Change handling difference
            self.payment_difference_handling = 'open'

    @api.onchange('receiving_amt')
    def onchange_receiving_amt(self):
        rec = self

        # is discount applicable
        payment_date = fields.Date.from_string(rec.wizard_id.payment_date)
        discount_information = rec.invoice_id.payment_term_id._check_payment_term_discount(
                rec.invoice_id, payment_date)
        discount_amount = discount_information[0]
        discount_account_id = discount_information[1]

        # compute difference
        due_or_balance = rec.balance_amt - rec.receiving_amt

        # apply discount
        if due_or_balance <= discount_amount:
            overpayment = discount_amount - due_or_balance
            rec.payment_difference = discount_amount - overpayment
            rec.payment_difference_handling = 'reconcile'
            if due_or_balance:
                rec.writeoff_account_id = discount_account_id
                rec.writeoff_label = 'Payment Discount'
                rec.note = 'Early Pay Discount'
            
        # cannot apply discount
        else:
            rec.payment_differnce = due_or_balance
            rec.payment_difference_handling = 'open'
            rec.writeoff_account_id = False
            rec.writeoff_label = False
            rec.note = False

class InvoicePaymentLine(models.TransientModel):
    _inherit = "invoice.payment.line"

    @api.onchange('paying_amt')
    def onchange_paying_amt(self):
        rec = self

        # is discount applicable
        payment_date = fields.Date.from_string(rec.wizard_id.payment_date)
        discount_information = rec.invoice_id.payment_term_id._check_payment_term_discount(
                rec.invoice_id, payment_date)
        discount_amount = discount_information[0]
        discount_account_id = discount_information[1]

        # compute difference
        due_or_balance = rec.balance_amt - rec.paying_amt

        # apply discount
        if due_or_balance <= discount_amount:
            overpayment = discount_amount - due_or_balance
            rec.payment_difference = discount_amount - overpayment
            rec.payment_difference_handling = 'reconcile'

            if due_or_balance:
                rec.writeoff_account_id = discount_account_id
                rec.writeoff_label = 'Payment Discount'
                rec.note = 'Early Pay Discount'
            
        # cannot apply discount
        else:
            rec.payment_differnce = due_or_balance
            rec.payment_difference_handling = 'open'
            rec.writeoff_account_id = False
            rec.writeoff_label = False
            rec.note = False

class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.onchange('payment_date')
    def onchange_payment_date(self):
        if self.payment_date:
            # Check for Customer Invoice
            for rec in self.invoice_customer_payments:
                rec.onchange_receiving_amt()

            # Check for Vendor Invoice
            for rec in self.invoice_payments:
                rec.onchange_paying_amt()

    @api.multi
    @api.onchange('invoice_customer_payments')
    def _get_cust_amount(self):
        tot = 0.0
        for rec in self.invoice_customer_payments:
            tot += rec.receiving_amt
        if self.invoice_customer_payments:
            self.cheque_amount = tot

    @api.multi
    @api.onchange('invoice_payments')
    def _get_supp_amount(self):
        tot = 0.0
        for rec in self.invoice_payments:
            tot += rec.paying_amt
        if self.invoice_payments:
            self.cheque_amount = tot

    @api.multi
    def get_batch_payment_amount(self, invoice_id=None, payment_date=None):
        val = {
            'amt': False,
            'payment_difference': False,
            'payment_difference_handling': False,
            'writeoff_account_id': False,
            'writeoff_label': False
        }
        discount_information = invoice_id.payment_term_id._check_payment_term_discount(
            invoice_id, payment_date)
        discount_amt = discount_information[0]
        discount_account_id = discount_information[1]
        # compute payment difference
        payment_difference = self.payment_difference
        if payment_difference <= discount_amt:
            # Prepare vals
            val.update({
                    'amt' : invoice_id.discount_amt,
                    'payment_difference': abs(invoice_id.residual - \
                                           invoice_id.discount_amt),
                    'payment_difference_handling' : 'reconcile',
                    'writeoff_account_id' : discount_account_id,
                    'note' : (payment_difference != 0.0) and 'Early Pay Discount' or False
                })
        return val

    @api.model
    def default_get(self, fields):
        if self.env.context and not self.env.context.get('batch', False):
            return super(AccountRegisterPayments, self).default_get(fields)

        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Program error: wizard action executed without\
             active_model or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(_("Program error: the expected model for this\
             action is 'account.invoice'. The provided one is '%d'.") \
                            % active_model)
        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for \
            open invoices"))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != \
               MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] \
               for inv in invoices):
            raise UserError(_("You cannot mix customer invoices and vendor\
             bills in a single payment."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once,\
             they must use the same currency."))
        # Set payment date as current date
        payment_date = datetime.today()

        rec = {}
        if 'batch' in context and context.get('batch'):
            payment_lines = []
            if MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] == 'customer':
                for inv in invoices:
                    # Get prepared dict
                    vals = self.get_batch_payment_amount(inv, payment_date)
                    discount_information = inv.payment_term_id._check_payment_term_discount(
                        inv, payment_date)
                    discount_amt = discount_information[0]
                    payment_amount = discount_information[2] - discount_amt
                    payment_difference = discount_amt
                    if payment_amount <= 0.0:
                        payment_amount = vals.get('amt') or 0.0
                    if discount_amt <= 0.0:
                        payment_difference = vals.get('payment_difference') or 0.0
                    payment_lines.append(
                        (0, 0, {'partner_id': inv.partner_id.id,
                                'invoice_id': inv.id,
                                'balance_amt': inv.residual or 0.0,
                                'receiving_amt': payment_amount,
                                'payment_difference_handling': vals.get('payment_difference_handling', False),
                                'payment_difference': payment_difference,
                                'writeoff_account_id': vals.get('writeoff_account_id', False),
                                'note': vals.get('note', False),
                                }))
                rec.update({'invoice_customer_payments': payment_lines,
                            'is_customer': True})
            else:
                for inv in invoices:
                    # Get prepared dict
                    vals = self.get_batch_payment_amount(inv, payment_date)
                    discount_information = inv.payment_term_id._check_payment_term_discount(
                        inv, payment_date)
                    discount_amt = discount_information[0]
                    payment_amount = discount_information[2] - discount_amt
                    payment_difference = discount_amt
                    if payment_amount <= 0.0:
                        payment_amount = vals.get('amt')
                    if discount_amt <= 0.0:
                        payment_difference = vals.get('payment_difference') or 0.0
                    payment_lines.append(
                        (0, 0, {'partner_id': inv.partner_id.id,
                                'invoice_id': inv.id,
                                'balance_amt': inv.residual or 0.0,
                                'payment_difference':payment_difference,
                                'paying_amt': payment_amount,
                                'note': vals.get('note', False),
                                'writeoff_account_id': vals.get('writeoff_account_id', False),
                                'payment_difference_handling': vals.get('payment_difference_handling', False),
                                }))
                rec.update({'invoice_payments': payment_lines,
                            'is_customer': False})
        else:
            # Checks on received invoice records
            if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != \
                   MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] \
                   for inv in invoices):
                raise UserError(_("You cannot mix customer invoices and\
                 vendor bills in a single payment."))

        total_amount = sum(inv.residual * \
                           MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
        rec.update({
            'amount': abs(total_amount),
            'currency_id': invoices[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'payment_date': payment_date,
        })
        return rec

    @api.multi
    def auto_fill_payments(self):
        ctx = self._context.copy()
        # Check if payment date set
        if not self.payment_date:
            raise ValidationError(_('Warning! \
                                         Please enter Payment Date!'))

        for wiz in self:
            if wiz.is_customer:
                if wiz.invoice_customer_payments:
                    cust_tot = 0.0
                    for payline in wiz.invoice_customer_payments:
                        vals = self.get_batch_payment_amount(payline.invoice_id, self.payment_date)
                        payline.write(
                            {'receiving_amt': vals.get('amt', False) or payline.balance_amt,
                             'payment_difference': vals.get('payment_difference', False) or 0.0,
                             'writeoff_account_id': vals.get('writeoff_account_id', False),
                             'payment_difference_handling': vals.get('payment_difference_handling', False),
                             'note': vals.get('note', False),
                             })
                        # Special Case: If full amount payment, then make diff handling as 'reconcile'
                        if payline.payment_difference_handling == 'reconcile' and \
                                payline.payment_difference == 0.0:
                            # Change handling difference
                            payline.payment_difference_handling = 'open'
                        cust_tot += payline.receiving_amt
                    wiz.cheque_amount = cust_tot
                ctx.update({
                    'reference': wiz.communication or '',
                    'journal_id': wiz.journal_id.id
                })
            else:
                if wiz.invoice_payments:
                    supp_tot = 0.0
                    for payline in wiz.invoice_payments:
                        vals = self.get_batch_payment_amount(payline.invoice_id, self.payment_date)
                        payline.write(
                            {'paying_amt': vals.get('amt', False) or payline.balance_amt,
                             'payment_difference': vals.get('payment_difference', False) or 0.0,
                             'writeoff_account_id': vals.get('writeoff_account_id', False),
                             'payment_difference_handling': vals.get('payment_difference_handling', False),
                             'note': vals.get('note', False),
                             })
                        # Special Case: If full amount payment, then make diff handling as 'reconcile'
                        if payline.payment_difference_handling == 'reconcile' and \
                            payline.payment_difference == 0.0:
                            # Change handling difference
                            payline.payment_difference_handling = 'open'
                        supp_tot += payline.paying_amt
                    wiz.cheque_amount = supp_tot
                ctx.update({
                    'reference': wiz.communication or '',
                    'journal_id': wiz.journal_id.id
                })
        return {
            'name': _("Batch Payments"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_id': self.id,
            'res_model': 'account.register.payments',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': ctx
        }
