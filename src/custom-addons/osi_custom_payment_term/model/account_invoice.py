# -*- coding: utf-8 -*-
# Copyright 2018 Open Source Integrators (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    discount_amt = fields.Monetary('Discounted Remainder',
                                   help='Total remainder due after discount',
                                   compute='_compute_discount_amt',
                                   stored=True)
    shipping_lines_total = fields.Monetary(
        'Shippling Lines Total',
        help='Exclude shipping lines total from discount if applicable '
             'in terms',
        compute='_compute_shipping_lines_total')

    @api.onchange('residual', 'payment_term_id', 'date_invoice')
    def _compute_discount_amt(self):
        for invoice in self:
            if invoice.payment_term_id:
                discount_information = invoice.payment_term_id._check_payment_term_discount(
                    self.invoice_id, self.invoice_id.date_invoice)
                if discount_information[0] > 0.0:
                    invoice.discount_amt = abs(
                        (invoice.residual_signed - discount_information[0]), 2)
            else:
                invoice.discount_amt = 0.0

    @api.depends('invoice_line_ids')
    def _compute_shipping_lines_total(self):
        for invoice in self:
            shipping_lines_total = 0.0
            for line in invoice.invoice_line_ids.filtered(
                    lambda l: l.product_id.is_exclude_shipping_amount):
                shipping_lines_total += line.price_subtotal
            invoice.shipping_lines_total = shipping_lines_total
