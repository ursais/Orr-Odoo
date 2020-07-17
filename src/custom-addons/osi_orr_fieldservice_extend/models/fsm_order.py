# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    sale_order_line_ids = fields.Many2many('sale.order.line',
                                           string='Sale Order Lines')

    # Method to Build Invoices
    # Invoice the Qty To Invoice FSM Vals
    # Qty to invoice is not computed but manually set
    def build_invoice(self):
        jrnl = self.env['account.journal'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('type', '=', 'sale'),
            ('active', '=', True)],
            limit=1)
        fpos = self.sale_id.partner_id.property_account_position_id
        vals = {
            'partner_id': self.sale_id.partner_invoice_id.id,
            'type': 'out_invoice',
            'journal_id': jrnl.id or False,
            'fiscal_position_id': fpos.id or False,
            'fsm_order_ids': [(4, self.id)],
            'sale_order_id': self.sale_id.id,
            'team_id': self.sale_id.team_id.id,
            'user_id': self.sale_id.user_id.id,
            'date_invoice': str(datetime.today()),
            'date_start': self.scheduled_date_start,
        }
        invoice = self.env['account.invoice'].sudo().create(vals)
        line_ids = []
        for line in self.sale_order_line_ids:
            invoice_line = self.env['account.invoice.line'].create(
                line.invoice_line_create_vals(invoice.id, line.qty_to_invoice_fsm))
            invoice_line.write({'fsm_equipment_id': line.fsm_equipment_id.id})
        # Raise warning if no Invoice Lines
        if invoice and not invoice.invoice_line_ids:
            raise ValidationError(_("You must Set Done Quantity \
                                                from Sale Order Lines before Generating Invoice"))
        self.sale_id.write({'invoice_status': 'invoiced'})
        invoice.compute_taxes()

    def get_po_vals(self):
        return {
            'partner_id': self.person_id.partner_id.id,
            'date_order': datetime.today(),
            'picking_type_id': self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1).id,
            'order_line': self.get_order_line_vals(),
            'user_id': self.sale_id.user_id.id or False
        }

    def get_order_line_vals(self):
        vals = []
        for line_id in self.sale_order_line_ids:
            if line_id.product_id:
                vals.append((0, 0, {
                    'name': line_id.name,
                    'product_id': line_id.product_id.id,
                    'product_qty': line_id.qty_to_invoice_fsm,
                    'product_uom': line_id.product_uom.id,
                    'price_unit': line_id.price_unit,
                    'date_planned': datetime.today()
                }))
        return vals

    # Method to build Vendor Bill
    # Only pull Services
    def build_bill(self):
        po_id = self.env['purchase.order'].create(self.get_po_vals())
        # Post Message in Chatter With FSO Name in It
        message = _(
            "This Purchase Order has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br") % (self.id, self.name)
        po_id.message_post(body=message)
        for line_id in po_id.order_line:
            qty = line_id.product_qty
            line_id.onchange_product_id()
            line_id.write({'product_qty': qty, 'qty_received': qty})
        po_id.button_confirm()
        jrnl = self.env['account.journal'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('type', '=', 'purchase'),
            ('active', '=', True)],
            limit=1)
        fpos = self.person_id.partner_id.property_account_position_id
        vals = {
            'partner_id': self.person_id.partner_id.id,
            'type': 'in_invoice',
            'journal_id': jrnl.id or False,
            'fiscal_position_id': fpos.id or False,
            'fsm_order_ids': [(4, self.id)],
            'purchase_id': po_id.id,
            'po_ref': po_id.name,
            'company_id': self.env.user.company_id.id,
            'user_id': po_id.user_id.id or False,
            'date_start': self.scheduled_date_start
        }
        bill = self.env['account.invoice'].sudo().create(vals)
        index = 0
        inv_line_obj = self.env['account.invoice.line']
        for line in self.sale_order_line_ids:
            invoice_line = inv_line_obj.create(
                line.invoice_line_create_vals(bill.id, line.qty_to_invoice_fsm))
            invoice_line.write(
                {'price_unit': po_id.order_line[index].price_unit, 'account_id': invoice_line.product_id.property_account_expense_id.id})
            index += 1
        # Raise warning if no invoice lines
        if bill and not bill.invoice_line_ids:
            raise ValidationError(_("You must set Done Quantity \
                                                from Sale Order Lines before Generating Vendor Bill"))
        bill.compute_taxes()

    # Currently Invoices and Bills are in the same Smart Button
    # We are going to split between Invoice and Bills

    @api.depends('invoice_ids')
    def _compute_account_invoice_count(self):
        for order in self:
            invoices = [
                inv_id for inv_id in order.invoice_ids if inv_id.type == 'out_invoice']
            order.invoice_count = len(invoices)

    @api.multi
    def action_view_invoices(self):
        action = self.env.ref(
            'account.action_invoice_tree').read()[0]
        invoices = [
            inv_id.id for inv_id in self.invoice_ids if inv_id.type == 'out_invoice']
        if self.invoice_count > 1:
            action['domain'] = [('id', 'in', invoices)]
        elif invoices:
            action['views'] = \
                [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices[0]
        return action

    bill_count = fields.Integer(
        string='Vendor Bill Count',
        compute='_compute_vendor_bill_count', readonly=True)

    @api.depends('invoice_ids')
    def _compute_vendor_bill_count(self):
        for order in self:
            invoices = [
                inv_id for inv_id in order.invoice_ids if inv_id.type == 'in_invoice']
            order.bill_count = len(invoices)

    @api.multi
    def action_view_vendor_bills(self):
        action = self.env.ref(
            'account.action_invoice_tree').read()[0]
        invoices = [
            inv_id.id for inv_id in self.invoice_ids if inv_id.type == 'in_invoice']
        if self.invoice_count > 1:
            action['domain'] = [('id', 'in', invoices)]
        elif invoices:
            action['views'] = \
                [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices[0]
        return action

    invoice_btn = fields.Boolean(compute='_compute_invoice_buttons')
    bill_btn = fields.Boolean(compute='_compute_invoice_buttons')

    def _compute_invoice_buttons(self):
        if self.bill_count == 0:
            self.bill_btn = True
        else:
            self.bill_btn = True
            for inv in self.invoice_ids:
                if inv.type == 'in_invoice' and inv.state in ['draft', 'open', 'in_payment', 'paid']:
                    self.bill_btn = False
        if self.invoice_count == 0:
            self.invoice_btn = True
        else:
            self.invoice_btn = True
            for inv in self.invoice_ids:
                if inv.type == 'out_invoice' and inv.state in ['draft', 'open', 'in_payment', 'paid']:
                    self.invoice_btn = False

    group_id = fields.Many2one('fsm.order.group', string='Group ID')

    branch_id = fields.Many2one(
        'fsm.branch', 'Branch', related='location_id.branch_id', store=True)
    territory_id = fields.Many2one(
        'fsm.territory', 'Territory', related='location_id.territory_id', store=True)

    @api.multi
    def write(self, vals):
        duration = 0.0
        if vals.get('scheduled_date_start'):
            end = fields.Datetime.from_string(vals.get('scheduled_date_start'))
            start = fields.Datetime.from_string(self.scheduled_date_start)
            delta = end - start
            duration = delta.total_seconds() / 3600
        res = super().write(vals)
        for rec in self:
            if duration and rec.group_id:
                fsm_order_rec = self.search(
                    [('group_id', '=', rec.group_id.id),
                     ('id', '!=', rec.id)])
                for fsm_rec in fsm_order_rec:
                    new_date = fsm_rec.scheduled_date_start + \
                        relativedelta(hours=duration)
                    fsm_end_date = new_date + relativedelta(
                        hours=fsm_rec.scheduled_duration)
                    self._cr.execute("""UPDATE fsm_order
                        SET scheduled_date_start=%s,scheduled_date_end=%s
                        WHERE id = %s""", (new_date, fsm_end_date, fsm_rec.id,))
        return res
