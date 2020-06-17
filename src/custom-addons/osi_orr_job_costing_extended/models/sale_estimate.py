# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleEstimateJob(models.Model):
    _inherit = "sale.estimate.job"

    accounting_person_id = fields.Many2one(
        'res.users',
        string='Accountic Person',
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )

    @api.multi
    def _prepare_quotation_line(self, quotation):
        """Overrite this method for populate analytic tag"""
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            for line in rec.estimate_ids:
                vals1 = {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'name': line.product_description,
                    'price_total': self.total,
                    'discount': line.discount,
                    'order_id': quotation.id,
                    'analytic_tag_ids':
                    [(6, 0, rec.analytic_tag_ids.ids)],
                }
                quo_line = quo_line_obj.create(vals1)
            for line in rec.labour_estimate_line_ids:
                vals1 = {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'name': line.product_description,
                    'price_total': self.total,
                    'discount': line.discount,
                    'order_id': quotation.id,
                    'analytic_tag_ids':
                    [(6, 0, rec.analytic_tag_ids.ids)],
                }
                quo_line = quo_line_obj.create(vals1)

            for line in rec.overhead_estimate_line_ids:
                vals1 = {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'name': line.product_description,
                    'price_total': self.total,
                    'discount': line.discount,
                    'order_id': quotation.id,
                    'analytic_tag_ids':
                    [(6, 0, rec.analytic_tag_ids.ids)],
                }
                quo_line = quo_line_obj.create(vals1)

    @api.multi
    def estimate_to_quotation(self):
        """Overrite this method for populate analytic account,
        reference, note"""
        quo_obj = self.env['sale.order']
        for rec in self:
            vals = {
                'partner_id': rec.partner_id.id,
                'origin': rec.number,
                # 'project_id': rec.analytic_id.id,
                # 'analytic_account_id': rec.analytic_id.id,
                'note': rec.description,
                'client_order_ref': rec.reference,
                'analytic_tag_ids':
                    [(6, 0, rec.analytic_tag_ids.ids)],
            }
            quotation = quo_obj.create(vals)
            rec._prepare_quotation_line(quotation)
            rec.quotation_id = quotation.id
        rec.state = 'quotesend'

    @api.multi
    def estimate_confirm(self):
        res = super().estimate_confirm()
        for rec in self:
            if rec.accounting_person_id:
                template = self.env.ref(
                    'osi_orr_job_costing_extended.job_estimate_approval',
                    raise_if_not_found=False)
                template.send_mail(self.id, force_send=True)
        return res


class SaleEstimatelineJob(models.Model):
    _inherit = "sale.estimate.line.job"

    cost_price = fields.Float(
        string='Cost / Unit',
    )
