# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    sale_order_line_ids = fields.Many2many('sale.order.line',
                                           string='Sale Order Lines')

    service_requirement = fields.Char(string="Service Requirements")

    # Move to Assign
    # Make sure Worker and Vehicle are set
    def action_assign(self):
        if not self.vehicle_id or not self.person_id:
            raise ValidationError(_("You must set the Worker and \
                                    Vehicle before moving to Assigned Stage"))
        else:
            return self.write({'stage_id': self.env.ref(
            'artisent.fsm_stage_assigned').id})
    
    # Move to In Progress
    # Make sure Vehicle Loading is Done
    def action_in_progress(self):
        vehicle_picking = False
        for picking_id in self.picking_ids:
            if picking_id.picking_type_id.name == self.\
                    env.ref('fieldservice_vehicle_stock.' +
                            'picking_type_output_to_vehicle').name:
                vehicle_picking = picking_id
        if vehicle_picking:
            if vehicle_picking.state == 'done':
                return self.write({'stage_id': self.env.ref(
                    'artisent.fsm_stage_in_progress').id})
            else:
                raise ValidationError(_("The Stock Picking for Vehicle \
                                        Loading has not been Completed"))
        else:
            return self.write({'stage_id': self.env.ref(
                    'artisent.fsm_stage_in_progress').id})

    # Move to Review State
    def action_review(self):
        return self.write({'stage_id': self.env.ref(
            'artisent.fsm_stage_review').id})

    # Move to Complete State
    # Must have Invoice and Bill made
    def action_complete(self):
        if self.bill_btn or self.invoice_btn:
            raise ValidationError(_("Cannot move to Completed without \
                                        an Invoice and a Vendor Bill"))
        return super().action_complete()
    
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
            'date_invoice': str(datetime.today())
        }
        invoice = self.env['account.invoice'].sudo().create(vals)
        price_list = invoice.partner_id.property_product_pricelist
        line_ids = []
        for line in self.sale_order_line_ids:
            invoice_line = self.env['account.invoice.line'].create(line.invoice_line_create_vals(invoice.id, line.qty_to_invoice_fsm))
        
    # Method to build Vendor Bill
    # Only pull Services
    def build_bill(self):
        po_id = self.env['purchase.order'].create(self.get_po_vals())
        # Post Message in Chatter With FSO Name in It
        message = _("This Purchase Order has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br") % (self.id, self.name)
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
            'user_id': po_id.user_id.id or False
        }
        bill = self.env['account.invoice'].sudo().create(vals)
        index = 0
        inv_line_obj = self.env['account.invoice.line']
        for line in self.sale_order_line_ids:
            if line.product_id.type == 'service':
                invoice_line = inv_line_obj.create(line.invoice_line_create_vals(bill.id, line.qty_to_invoice_fsm))
                invoice_line.write({'price_unit': po_id.order_line[index].price_unit})
                index += 1
        bill.compute_taxes()

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
                if line_id.product_id.type =='service':
                    vals.append((0, 0, {
                        'name': line_id.name,
                        'product_id': line_id.product_id.id,
                        'product_qty': line_id.qty_to_invoice_fsm,
                        'product_uom': line_id.product_uom.id,
                        'price_unit': line_id.price_unit,
                        'date_planned': datetime.today()
                    }))
        return vals

    # Overwrite FSM Stock Method
    # Current Method only checks 'outgoing'
    # Change to get everything but returns
    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(
                [picking for picking in order.picking_ids if
                 picking.picking_type_id.code != 'incoming'])
            order.return_count = len(
                [picking for picking in order.picking_ids if
                 picking.picking_type_id.code == 'incoming'])
    
    # Overwrite FSM Stock Method
    # Current Method only checks 'outgoing'
    # Change to get everything but returns
    @api.multi
    def action_view_delivery(self):
        """
        This function returns an action that display existing delivery orders
        of given fsm order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        """
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.mapped('picking_ids')
        delivery_ids = [picking.id for picking in pickings if
                        picking.picking_type_id.code != 'incoming']
        if len(delivery_ids) > 1:
            action['domain'] = [('id', 'in', delivery_ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id,
                                'form')]
            action['res_id'] = delivery_ids[0]
        return action

    # Everything below here will be moved to OCA


    # Default Vehicle should be pulled from Worker
    @api.onchange('person_id')
    def onchange_person_id(self):
        if self.person_id:
            self.vehicle_id = self.person_id.vehicle_id

    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_account_invoice_count', readonly=True)

    # Currently Invoices and Bills are in the same Smart Button
    # We are going to split between Invoice and Bills
    @api.depends('invoice_ids')
    def _compute_account_invoice_count(self):
        for order in self:
            invoices = [inv_id for inv_id in order.invoice_ids if inv_id.type == 'out_invoice']
            order.invoice_count = len(invoices)

    @api.multi
    def action_view_invoices(self):
        action = self.env.ref(
            'account.action_invoice_tree').read()[0]
        invoices = [inv_id.id for inv_id in self.invoice_ids if inv_id.type == 'out_invoice']
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
            invoices = [inv_id for inv_id in order.invoice_ids if inv_id.type == 'in_invoice']
            order.bill_count = len(invoices)

    @api.multi
    def action_view_vendor_bills(self):
        action = self.env.ref(
            'account.action_invoice_tree').read()[0]
        invoices = [inv_id.id for inv_id in self.invoice_ids if inv_id.type == 'in_invoice']
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

    @api.onchange('request_early')
    def onchange_request_early(self):
        if self.request_early:
            self.scheduled_date_start = self.request_early
