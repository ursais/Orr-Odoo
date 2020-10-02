# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta


class Partner(models.Model):
    _inherit = "res.partner"

    sales_hold = fields.Boolean(
        string='Sales Hold',
        default=False,
        help='If checked, new quotations cannot be confirmed'
    )
    credit_limit = fields.Monetary(string='Credit Limit')
    grace_period = fields.Integer(
        string='Grace Period',
        help='Grace period added on top of the customer payment term '
             '(in days)'
    )
    credit_hold = fields.Boolean(
        string='Credit Hold',
        help='Place the customer on credit hold to prevent from shipping goods'
    )

   
    @api.multi
    def write(self, vals):

        res = super(Partner,self).write(vals)
        if 'credit_limit' in vals:
            for partner in self:
                order_ids = self.env['sale.order'].search([
                            ('partner_id', '=', partner.id),
                            ('ship_hold', '=', True)])
                if partner.credit_limit > 0 and order_ids:
                    if not self.check_limit(order_ids[0]):
                        order_ids.write({'ship_hold':False})
        return res
    

    @api.multi
    def check_limit(self, sale_id):
        partner_id = sale_id.partner_id
        # Other orders for this partner
        order_ids = self.env['sale.order'].search([
                    ('partner_id', '=', partner_id.id),
                    ('state', '=', 'sale'),
                    ('invoice_status', '!=', 'invoiced')
        ])
        # Open invoices (unpaid or partially paid invoices --
        # It is already included in partner.credit
        invoice_ids = self.env['account.invoice'].search([
            ('partner_id', '=', partner_id.id),
            #('state', '=', 'open'),
            ('state', 'in', ['open', 'draft']),
            ('type', 'in', ['out_invoice', 'out_refund'])])
        # Initialize variables
        existing_order_balance = 0.0
        existing_invoice_balance = 0.0
        # Confirmed orders - invoiced - draft or open / not invoiced
        for order in order_ids:
            existing_order_balance = existing_order_balance + \
            order.amount_total
        # Invoices that are open (also shows up as part of partner.
        # Credit, so must be deducted
        for invoice in invoice_ids:
            if (fields.Datetime.to_string((invoice.date_due or invoice.date_invoice or invoice.create_date) + timedelta(
                days=partner_id.grace_period))) > fields.Datetime.to_string(
                datetime.now()):
                continue
            else:
                existing_invoice_balance = existing_invoice_balance + \
                invoice.residual
        # All open sale orders + partner credit (AR balance) -
        # Open invoices (already included in partner credit)
        if sale_id.partner_id.credit_limit and (existing_invoice_balance + \
                        existing_order_balance) > \
                        sale_id.partner_id.credit_limit:
            return True
        else:
            return False
    '''
    @api.onchange('credit_limit')
    def onchange_credit_limit(self):
        import pdb; pdb.set_trace()
        for partner in self:
            order_ids = self.env['sale.order'].search([
                        ('partner_id', '=', partner.id),
                        ('ship_hold', '=', True)])
            if partner.credit_limit > 0 and order_ids:
                if not self.check_limit(order_ids[0]):
                    order_ids.write({'ship_hold':False})
    '''
