# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    po_style = fields.Many2one(
        'report.template.settings',
        'PO Style',
        help="Select Style to use when printing the Purchase Order",
        default=lambda self: self.partner_id.style or\
            self.env.user.company_id.po_style or\
            self.env.user.company_id.df_style)
    rfq_style = fields.Many2one(
        'report.template.settings',
        'RFQ Style',
        help="Select style to use when printing the RFQ",
        default=lambda self: self.partner_id.style or\
            self.env.user.company_id.rfq_style or\
            self.env.user.company_id.df_style)
    
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_style(self):
        self.po_style = self.partner_id.style or\
            self.env.user.company_id.po_style or\
            self.env.user.company_id.df_style or\
            self.env.ref('professional_templates.df_style_for_all_reports').id
        self.rfq_style = self.partner_id.style or\
            self.env.user.company_id.rfq_style or\
            self.env.user.company_id.df_style or\
            self.env.ref('professional_templates.df_style_for_all_reports').id
