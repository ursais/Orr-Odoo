# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_type = fields.Selection(
        [('owner', 'Owner'),
         ('management_company', 'Management Company'),
         ('contact', 'Contact'),
         ('new_construction', 'New Constructions')],
        'Partner Type')
    address_type = fields.Char('AddressType')
    associated_id = fields.Many2one('res.partner', 'Associated Entity')
    num_unit = fields.Integer(string="Number of Units")
    prop_mgmt_id = fields.Many2one('res.partner', 
                                   string="Property Management Company")
    prop_mgr_id = fields.Many2one('res.partner', string="Current Manager")
    property_count = fields.Integer("# Properties", compute='_compute_property_count')

    @api.multi
    def action_open_aln_feed(self):
        "This method will filter ALN Feed data based on current partner"
        action = self.env.ref('connector_alndata.aln_feed_action_tree_2').read()[0]
        action['context'] = {}
        action['domain'] = [('partner_id', 'in', self.ids)]
        return action

    @api.multi
    def _compute_property_count(self):
        for partner in self:
            part_ids = self.search([('prop_mgmt_id', '=', partner.id)])
            partner.property_count = len(part_ids)
