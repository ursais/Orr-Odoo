# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    

    dn_style = fields.Many2one(
        'report.template.settings',
        'Delivery Note Style',
        help="Select style to use when printing the Delivery Note",
        default=lambda self: self.partner_id.style or\
            self.env.user.company_id.dn_style or\
            self.env.user.company_id.df_style)
    pk_style = fields.Many2one(
        'report.template.settings',
        'Picking Style',
        help="Select Style to use when printing the picking slip",
        default=lambda self: self.partner_id.style or\
            self.env.user.company_id.pick_style or\
            self.env.user.company_id.df_style)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_style(self):
        """method to assign a style to a report based on the selected
        partner."""
        self.pk_style = self.partner_id.style or\
            self.env.user.company_id.pick_style or\
            self.env.user.company_id.df_style or\
            self.env.ref('professional_templates.df_style_for_all_reports').id
        self.dn_style = self.partner_id.style or\
            self.env.user.company_id.dn_style or\
            self.env.user.company_id.df_style or\
            self.env.ref('professional_templates.df_style_for_all_reports').id
