# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_discount_move_line(self, vals):
        valid = False
        for invoice in self:
            if invoice.payment_term_id and \
                    invoice.payment_term_id.is_discount and \
                    invoice.payment_term_id.line_ids:
                discount_information = invoice.payment_term_id._check_payment_term_discount(
                    invoice, invoice.date_invoice)
                discount_amt = discount_information[0]
                discount_account_id = discount_information[1]
                if discount_amt > 0.0:
                    vals.update({'account_id': discount_account_id,
                                 'invoice_id': invoice.id,
                                 'bank_payment_line_id': False,
                                 'name': 'Early Pay Discount'})
                    if invoice.type == 'out_invoice':
                        vals.update({'credit': 0.0, 'debit': discount_amt})
                        valid = True
                    elif invoice.type == 'in_invoice':
                        vals.update({'credit': discount_amt, 'debit': 0.0})
                        valid = True
            if valid:
                return vals
            else:
                return {}

    def _prepare_writeoff_move_line(self, payment_line, vals):
        for invoice in self:
            note = ''
            if payment_line.reason_code:
                note = payment_line.reason_code.display_name + ': '
            if payment_line.note:
                note += payment_line.note
            vals.update({'account_id': payment_line.writeoff_account_id.id,
                         'bank_payment_line_id': False,
                         'name': note,
                         'invoice_id': invoice.id,})
            if invoice.type == 'out_invoice':
                vals.update({'credit': 0.0,
                             'debit': payment_line.payment_difference})
            elif invoice.type == 'in_invoice':
                vals.update({'credit': payment_line.payment_difference,
                             'debit': 0.0})
        return vals
