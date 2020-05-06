# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company)], limit=1)
        return warehouse_ids and warehouse_ids.id

    quotation_template_ids = fields.Many2many(
        'sale.order.template',
        string='Sale Order Templates')
    quotation_template_count = fields.Integer(
        string='Sale Order Template Count',
        compute='compute_quotation_template_count')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string="Priority", default="0")
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        default=_default_warehouse_id)

    @api.multi
    def action_view_quotation_templates(self):
        for partner in self:
            templates = self.env['sale.order.template'].\
                search([('partner_id', '=', partner.id)])
            action = self.env.ref('sale_management.sale_order_template_action').\
                read()[0]
            action['context'] = self.env.context.copy()
            if len(templates) == 1:
                action['views'] = [(self.env.
                                    ref('sale_management.sale_order_template_view_form').id,
                                    'form')]
                action['res_id'] = templates.id
                action['context'].update({'active_id': templates.id})
            else:
                action['domain'] = [('id', 'in', templates.ids)]
                action['context'].update({'active_ids': templates.ids})
                action['context'].update({'active_id': ''})
            return action

    @api.multi
    def compute_quotation_template_count(self):
        for partner in self:
            templates = self.env['sale.order.template'].\
                search([('partner_id', '=', partner.id)])
            partner.quotation_template_count = len(templates)
