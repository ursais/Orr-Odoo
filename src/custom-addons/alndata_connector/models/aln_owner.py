# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ALNOwner(models.Model):
    _name = "aln.owner"
    _description = "ALN Owner"

    owner_id_txt = fields.Char('Owner ID')
    owner_name = fields.Char('Name')
    owner_address = fields.Char('Address')
    owner_phone = fields.Char('Phone')
    own_published_date = fields.Datetime(string="Published Date")
    own_published_id = fields.Many2one(
        'res.partner',
        'Published by'
    )
    own_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='State',
        default='unpublished'
    )
