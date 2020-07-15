# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRecurringOrder(models.Model):
    _inherit = 'fsm.recurring'

    group_id = fields.Many2one(
        'fsm.recurring.group',
        string='Recurring Group ID')

    def _prepare_order_values(self, date=None):
        values = super(FSMRecurringOrder,
                       self)._prepare_order_values(date)
        if values.get('fsm_recurring_id') and \
                values.get('scheduled_date_start'):
            recurring_rec = self.env['fsm.recurring'].browse(
                [values.get('fsm_recurring_id')])
            if recurring_rec.group_id:
                scheduled_date_start = \
                    (values.get('scheduled_date_start').strftime(
                        '%Y-%m-%d')).replace("-", "")
                group_name = \
                    (recurring_rec.group_id.name + '-' + scheduled_date_start)
                fsm_group_rec = self.env['fsm.order.group'].search(
                    [('name', '=', group_name)], limit=1)
                if not fsm_group_rec:
                    fsm_group_rec = self.env['fsm.order.group'].create(
                        {'name': group_name})
                if fsm_group_rec:
                    values.update({'group_id': fsm_group_rec.id})
        return values

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if vals.get('group_id'):
                recurring_group_name = rec.group_id.name
                for order_rec in rec.fsm_order_ids:
                    if order_rec.group_id:
                        group_last_index = \
                            order_rec.group_id.name.split('-')[-1]
                        order_rec.group_id.name = \
                            recurring_group_name + '-' + group_last_index
        return res

    branch_id = fields.Many2one(
        'fsm.branch', 'Branch', related='location_id.branch_id', store=True)
    territory_id = fields.Many2one(
        'fsm.territory', 'Territory', related='location_id.territory_id', store=True)
