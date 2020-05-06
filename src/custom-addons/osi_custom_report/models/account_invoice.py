# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    style = fields.Many2one(
        'report.template.settings',
        'Invoice Style',
        help="Select Style to use when printing this invoice",
        default=lambda self: self.partner_id.style or\
            self.env.user.company_id.inv_style or\
            self.env.user.company_id.df_style)
    
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_style(self):
        self.style = self.partner_id.style or\
        self.env.user.company_id.inv_style or\
        self.env.user.company_id.df_style or\
        self.env.ref('professional_templates.df_style_for_all_reports')
