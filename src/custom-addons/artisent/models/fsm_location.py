# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class FSMLocation(models.Model):
    _inherit = "fsm.location"


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super().name_search(name, args, operator, limit)
        if self._context.get('sale_order', False):
            args = args or []
            recs = self.browse()
            if name:
                recs = self.\
                    search(['|', '|',
                            ('ref', 'ilike', name),
                            ('notes', 'ilike', name),
                            ('description', 'ilike', name)] + args, limit=limit)
            if not recs:
                recs = self.search([('name', operator, name)] + args, limit=limit)
            return recs.name_get()
        else:
            return res

    
    loc_sale_order_ids = fields.Many2many(
        'sale.order',
        string='Sale Orders')

    loc_sale_order_count = fields.Integer(
        string='Sale Order Count',
        compute='compute_sale_order_count')

    # Sale Orders
    @api.multi
    def action_view_sales_orders(self):
        for location in self:
            orders = self.get_orders(location)
            action = self.env.ref('sale.action_orders').read()[0]
            action['context'] = self.env.context.copy()
            if len(orders) == 1:
                action['views'] = [(self.env.\
                    ref('sale.view_order_form').id, 'form')]
                action['res_id'] = orders.id
                action['context'].update({'active_id': orders.id})
            else:
                action['domain'] = [('id', 'in', orders.ids)]
                action['context'].update({'active_ids': orders.ids})
                action['context'].update({'active_id': ''})
            return action

    def get_orders(self, loc):
        for child in loc:
            child_locs = self.env['fsm.location'].\
                search([('fsm_parent_id', '=', child.id)])
            orders = self.env['sale.order'].\
                search([('fsm_location_id', '=', child.id)])
        if child_locs:
            for loc in child_locs:
                orders += loc.get_orders(loc)
        return orders

    def comp_orders(self, loc):
        for child in loc:
            child_locs = self.env['fsm.location'].\
                search([('fsm_parent_id', '=', child.id)])
            orders = self.env['sale.order'].\
                search_count([('fsm_location_id', '=', child.id)])
        if child_locs:
            for loc in child_locs:
                orders += loc.comp_orders(loc)
        return orders

    @api.multi
    def compute_sale_order_count(self):
        for loc in self:
            orders = self.comp_orders(loc)
            loc.loc_sale_order_count = orders

    quotation_template_ids = fields.Many2many(
        'sale.order.template',
        string='Sale Order Templates')

    quotation_template_count = fields.Integer(
        string='Sale Order Template Count',
        compute='compute_quotation_template_count')

    # Sale Order Templates
    @api.multi
    def action_view_quotation_templates(self):
        for location in self:
            templates = self.get_temps(location)
            action = self.env.ref('sale_management.sale_order_template_action').\
                read()[0]
            action['context'] = self.env.context.copy()
            if len(templates) == 1:
                action['views'] = [(self.env.\
                    ref('sale_management.sale_order_template_view_form').id,
                                    'form')]
                action['res_id'] = templates.id
                action['context'].update({'active_id': templates.id})
            else:
                action['domain'] = [('id', 'in', templates.ids)]
                action['context'].update({'active_ids': templates.ids})
                action['context'].update({'active_id': ''})
            return action

    def get_temps(self, loc):
        for child in loc:
            child_locs = self.env['fsm.location'].\
                search([('fsm_parent_id', '=', child.id)])
            temps = self.env['sale.order.template'].\
                search([('fsm_location_id', '=', child.id)])
        if child_locs:
            for loc in child_locs:
                temps += loc.get_temps(loc)
        return temps

    def comp_temps(self, loc):
        for child in loc:
            child_locs = self.env['fsm.location'].\
                search([('fsm_parent_id', '=', child.id)])
            temps = self.env['sale.order.template'].\
                search_count([('fsm_location_id', '=', child.id)])
        if child_locs:
            for loc in child_locs:
                temps += loc.comp_temps(loc)
        return temps

    @api.multi
    def compute_quotation_template_count(self):
        for loc in self:
            temps = self.comp_temps(loc)
            loc.quotation_template_count = temps

    
    @api.depends('partner_id.name', 'fsm_parent_id.complete_name', 'ref')
    def _compute_complete_name(self):
        for loc in self:
            if loc.fsm_parent_id:
                if loc.name:
                    loc.complete_name = '%s / %s' % (
                        loc.fsm_parent_id.complete_name,
                        loc.partner_id.name)
                else:
                    loc.complete_name = '%s / %s' % (
                        loc.fsm_parent_id.complete_name, loc.partner_id.ref)
            else:
                if loc.name:
                    loc.complete_name = loc.partner_id.name
                else:
                    loc.complete_name = '%s' % (loc.ref)
