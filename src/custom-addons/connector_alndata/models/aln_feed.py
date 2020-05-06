# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ALNFeed(models.Model):
    _name = "aln.feed"
    _description = "ALN Feed DATA"

    partner_id = fields.Many2one(
        'res.partner',
        'Partner'
    )
    status = fields.Selection(
        [('create', 'Created'),
         ('update', 'Updated')],
        'Status'
    )
    raw_aln_feed = fields.Text(
        'Raw ALN'
    )
    note = fields.Char(
        'Note'
    )
