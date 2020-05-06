# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_type = fields.Selection(
        [('apartment', 'Apartment'),
         ('owner', 'Owner'),
         ('management_company', 'Management Company'),
         ('contact', 'Contact'),
         ('new_construction', 'New Constructions')],
        'Partner Type')
    address_type = fields.Char('AddressType')
    parent_id_txt = fields.Char('Parent Entity Key')
    associated_id = fields.Many2one('res.partner', 'Associated Entity')
    associated_id_txt = fields.Char('Associated Entity Key')
    num_unit = fields.Integer(string="Number of Units")
    prop_mgmt_id = fields.Many2one('res.partner',
                                   string="Property Management Company")
    prop_mgmt_id_txt = fields.Char('Property Management Company Key')
    prop_mgr_id_txt = fields.Char('Property Manager Key')
    mgmt_comp_id_txt = fields.Char('Management company Key')
    prop_mgr_id = fields.Many2one('res.partner', string="Current Manager")
    property_count = fields.Integer("# Properties", compute='_compute_property_count')

    @api.multi
    def _compute_property_count(self):
        for partner in self:
            # Filter based on Management cmp and curr manager
            part_ids = self.search(['|',
                                    ('prop_mgmt_id', '=', partner.id),
                                    ('prop_mgr_id', '=', partner.id)
                                    ])
            partner.property_count = len(part_ids)
