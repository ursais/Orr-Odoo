# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.partner'
    
    style = fields.Many2one(
        'report.template.settings',
        'Reports Style',
        help="Select a style to use when printing reports for this customer",
        default=False)
