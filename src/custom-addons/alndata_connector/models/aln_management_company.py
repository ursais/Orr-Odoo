# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ALNManagementCompany(models.Model):
    _name = "aln.management.company"
    _description = "ALN Management Company"

    company_id_txt = fields.Char('Management Company ID')
    company_market = fields.Char('Market')
    company_name = fields.Char('Name')
    company_website = fields.Char('Website')
    company_parent_id_txt = fields.Char('Parent')
    company_rowversion = fields.Integer('RowVersion')
    cmp_last_changed_date = fields.Datetime(string="Last changed Date")
    cmp_published_date = fields.Datetime(string="Published Date")
    cmp_published_id = fields.Many2one(
        'res.partner',
        'Published by'
    )
    cmp_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='State',
        default='unpublished'
    )
