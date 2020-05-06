# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ALNContact(models.Model):
    _name = "aln.contact"
    _description = "ALN Contact"

    contact_id_txt = fields.Char('Contact')
    contact_name = fields.Char('Name')
    contact_title = fields.Char('Title')
    contact_email = fields.Char('Email')
    contact_company_property = fields.Char('Company/Property')
    associated_id_txt = fields.Char('Associated Entity')
    corporate_id_txt = fields.Char('Corporate Entity')
    contact_rowversion = fields.Integer('RowVersion')
    cont_last_changed_date = fields.Datetime(string="Last changed Date")
    cont_published_date = fields.Datetime(string="Published Date")
    cont_published_id = fields.Many2one(
        'res.partner',
        'Published by'
    )
    cont_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='State',
        default='unpublished'
    )
