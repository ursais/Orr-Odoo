# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    style = fields.Many2one(
        'report.template.settings',
        'Quote/Order Style',
        help="Select Style to use when printing the Sales Order or Quote",
        default=lambda self: self.partner_id.style or\
            self.env.user.company_id.so_style or\
            self.env.user.company_id.df_style)

    @api.onchange('partner_id')
    def onchange_partner_style(self):
        """assign style to a document based on chosen partner"""
        self.style = self.partner_id.style or\
            self.env.user.company_id.so_style or\
            self.env.user.company_id.df_style or\
            self.env.ref('professional_templates.df_style_for_all_reports').id
