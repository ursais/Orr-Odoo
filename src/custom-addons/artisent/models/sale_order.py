# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import RedirectWarning, Warning
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    service_requirement = fields.Char(string="Service Requirements")

    # Artisent Workflow
    @api.onchange('sale_order_template_id')
    def onchange_template_id(self):
        res = super().onchange_sale_order_template_id()
        if self.sale_order_template_id:
            if self.sale_order_template_id.fsm_location_id:
                self.fsm_location_id = self.sale_order_template_id.\
                    fsm_location_id
            temp_lines = self.sale_order_template_id.\
                sale_order_template_line_ids
            index = 0
            for line_id in self.order_line:
                line_id.instructions = temp_lines[index].instructions
                index += 1
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id and self.sale_order_template_id:
            if self.partner_id != self.sale_order_template_id.partner_id:
                self.sale_order_template_id = False
        self.warehouse_id = self.partner_id.warehouse_id
        return res

    sale_order_template_id = fields.\
        Many2one('sale.order.template',
                 'Quotation Template',
                 readonly=True,
                 states={'draft': [('readonly', False)],
                         'sent': [('readonly', False)]},
                 track_visibility='onchange')

    confirmation_date = fields.\
        Datetime(string='Confirmation Date',
                 readonly=True,
                 index=True,
                 help="Date on which the sales \
                 order is confirmed.",
                 oldname="date_confirm",
                 copy=False,
                 track_visibility='always')

    def _default_validity_date(self):
        return super()._default_validity_date()

    validity_date = fields.\
        Datetime(string='Validity',
                 readonly=True,
                 copy=False,
                 states={'draft': [('readonly', False)],
                         'sent': [('readonly', False)]},
                 help="Validity date of the quotation, after this date, \
                 the customer won't be able to validate the quotation \
                 online.",
                 default=_default_validity_date,
                 track_visibility='always')

    # Helper method for action_confirm
    # Check if SO Lines are a subset of previous order
    def check_order_lines(self, orders):
        self_lines = []
        for line_id in self.order_line:
            self_lines.append(line_id.product_id.id)
        for order in orders:
            order_lines = []
            for line_id in order.order_line:
                order_lines.append(line_id.product_id.id)
            if set(self_lines).issubset(set(order_lines)):
                return True
        return False

    so_warning_override = fields.Boolean('Override SO Warning', default=False)
    request_early = fields.Datetime(
        string='Earliest Installation Date',
        required=True,
        default=lambda self: fields.Datetime.now())
    request_late = fields.Datetime(
        string='Latest Installation Date')
    po_ref = fields.Char("PO Reference")

    # Check for similar orders placed within the last year
    # Raise warning until they check the override box
    def action_confirm(self):
        check_orders = self.env['sale.order'].\
            search([('fsm_location_id', '=', self.fsm_location_id.id),
                    ('sale_order_template_id', '=',
                     self.sale_order_template_id.id),
                    ('partner_id', '=', self.partner_id.id),
                    ('id', '!=', self.id),
                    ('state', 'in', ['sale', 'done']),
                    ('confirmation_date', '>', (datetime.today() - timedelta(days=365)))], order='confirmation_date desc')
        if check_orders:
            if self.check_order_lines(check_orders):
                if not self.so_warning_override:
                    action = self.env.ref('sale.action_orders')
                    msg = _('You placed a similar order on %s in Sale Order: %s \n To Continue, \
                            check the box that says Override SO Warning') % (check_orders[0].confirmation_date, check_orders[0].name)
                    raise RedirectWarning(
                        msg, action.id, _('View Sale Orders'))
        return super().action_confirm()

    # Copy SO Lines onto FSM Order
    def _field_create_fsm_order_prepare_values(self):
        res = super()._field_create_fsm_order_prepare_values()
        res.update({
            'sale_order_line_ids': [(6, 0, self.order_line.ids)],
            'request_early': self.request_early,
            'service_requirement': self.service_requirement
        })
        return res

    def _field_create_fsm_order(self):
        res = super()._field_create_fsm_order()
        key = list(res.keys())[0]
        # for line in res[key].sale_order_line_ids:
        #     line.state = 'draft'
        return res

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        res = super()._compute_picking_ids()
        if self.picking_ids and self.fsm_order_ids:
            for picking_id in self.picking_ids:
                picking_id.write({'fsm_order_id': self.fsm_order_ids[0].id})
        return res


    hide_invoice_btn = fields.Boolean(default=False, compute='_compute_hide_invoice_btn')

    # Artisent only wants invoice generated from FSO's if FSO available
    # Else use default SO Invoice Method
    def _compute_hide_invoice_btn(self):
        if self.fsm_order_ids:
            self.hide_invoice_btn = True
        else:
            self.hide_invoice_btn = False

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    instructions = fields.Char("Instructions")
    qty_to_invoice_fsm = fields.Float(
        string='To Invoice Quantity',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    @api.depends('qty_delivered_method', 'qty_delivered_manual', 'analytic_line_ids.so_line', 'analytic_line_ids.unit_amount', 'analytic_line_ids.product_uom_id')
    def _compute_qty_delivered(self):
        res = super()._compute_qty_delivered()
        for order in self:
            if order.qty_delivered:
                order.qty_to_invoice_fsm = order.qty_delivered
        return res


class SaleOrderTemplateLine(models.Model):
    _inherit = "sale.order.template.line"

    instructions = fields.Char("Instructions")


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    partner_id = fields.Many2one('res.partner', "Customer")
    fsm_location_id = fields.Many2one('fsm.location', "Service Location")
