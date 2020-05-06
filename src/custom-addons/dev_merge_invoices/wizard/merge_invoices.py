# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date


class MergeInvoices(models.TransientModel):
    _name = "merge.invoices"
    _description = "Merge Invoices/Bills"

    @api.multi
    def get_selected_invoices(self):
        active_ids = self._context.get('active_ids')
        return active_ids


    @api.multi
    @api.onchange('option')
    def onchange_option(self):
        invoice_bill_id = self.invoice_ids[0]
        self.invoice_bill_type = invoice_bill_id.type


    @api.multi
    def merge_invoices(self):
        active_ids = self._context.get('active_ids')
        if len(active_ids) < 2 and not self.option == 'existing_merge_cancel':
            raise ValidationError("Please Select at least two Invoices, in "
                                  "order to merge them")
        invoice_pool = self.env['account.invoice']
        invoice_ids = invoice_pool.browse(active_ids)
        if invoice_ids:
            for invoice in invoice_ids:
                if invoice.type not in ['out_invoice', 'in_invoice']:
                    raise ValidationError("Please select only Customer Invoices"
                                          " or Vendor Bills")
            partners = []
            invoices = []
            for invoice in invoice_ids:
                partners.append(invoice.partner_id.id)
                invoices.append(invoice.id)
            similar = len(set(partners)) == 1
            if not similar:
                raise ValidationError("Please select Invoices/Bills, which have"
                                      " similar Customer/Vendor, in order to"
                                      " merge them")
            if invoice_ids.filtered(lambda inv: inv.state != 'draft'):
                raise ValidationError("Please select Invoices/Bills, which are "
                                      "in draft state, in order to merge them")
            all_origins = []
            for invoice in invoice_ids:
                if invoice.origin:
                    if invoice.origin not in all_origins:
                        all_origins.append(str(invoice.origin))
            if self.option == 'merge_and_cancel':
                origin_string = ', '.join(map(str, all_origins))
                sample_inv_id = invoice_pool.browse(int(invoices[0]))
                invoice_id = invoice_pool.create(
                    {'partner_id': sample_inv_id.partner_id.id,
                     'user_id': sample_inv_id.user_id.id,
                     'fiscal_position_id':
                         sample_inv_id.fiscal_position_id and
                         sample_inv_id.fiscal_position_id.id or False,
                     'date_invoice': date.today(),
                     'account_id': sample_inv_id.account_id.id,
                     'company_id': sample_inv_id.company_id.id,
                     'currency_id': sample_inv_id.currency_id.id,
                     'journal_id': sample_inv_id.journal_id.id,
                     'payment_term_id': sample_inv_id.payment_term_id
                                        and sample_inv_id.payment_term_id.id
                                        or False,
                     'name': sample_inv_id.name or '',
                     'origin': str(origin_string),
                     'type': sample_inv_id.type,
                     'partner_shipping_id':
                         sample_inv_id.partner_shipping_id and
                         sample_inv_id.partner_shipping_id.id or False,
                     'team_id': sample_inv_id.team_id and
                                sample_inv_id.team_id.id or False
                     })
                if invoice_id:
                    invoice_id._onchange_payment_term_date_invoice()
                    for invoice in invoice_ids:
                        for line in invoice.invoice_line_ids:
                            line_copy = line.copy()
                            line_copy.invoice_id = invoice_id.id
                    invoice_id.compute_taxes()
                    invoice_ids.action_invoice_cancel()
            if self.option == 'existing_merge_cancel':
                inv_type = invoice_pool.browse(int(invoices[0])).type
                if self.invoice_id.type != inv_type:
                    if inv_type == 'out_invoice':
                        raise ValidationError("You can not merge Customer "
                                              "Invoices into Vendor Bill")
                    if inv_type == 'in_invoice':
                        raise ValidationError("You can not merge Vendor "
                                              "Bills into Customer Invoice")
                if self.invoice_id.id in invoices:
                    raise ValidationError("Please select another Invoice/Bill "
                                          "in Existing Invoice\nbecause you "
                                          "have already selected it for "
                                          "merging")
                for invoice in invoice_ids:
                    for line in invoice.invoice_line_ids:
                        line_copy = line.copy()
                        line_copy.invoice_id = self.invoice_id.id
                if self.invoice_id.origin and self.invoice_id.origin \
                        not in all_origins:
                    all_origins.append(str(self.invoice_id.origin))
                origin_string = ', '.join(map(str, all_origins))
                self.invoice_id.origin = str(origin_string)
                self.invoice_id.compute_taxes()
                invoice_ids.action_invoice_cancel()

    option = fields.Selection([
        ('merge_and_cancel', 'Merge Invoice/Bill into New Invoice and Cancel '
                             'Selected Invoices/Bills'),
        ('existing_merge_cancel', 'Merge Invoice/Bill into Existing Invoice '
                                  'and Cancel Selected Invoices/Bills')],
        string="Option of Merge", default="merge_and_cancel", required=1)

    invoice_ids = fields.Many2many("account.invoice",
                                   string="Selected Invoices/Bills to Merge",
                                   default=get_selected_invoices)
    invoice_id = fields.Many2one("account.invoice",
                                 string="Existing Invoice/Bill")
    invoice_bill_type = fields.Char(string="Invoice/Bill Type")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: