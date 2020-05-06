# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FsmLocation(models.Model):
    _inherit = "fsm.location"

    industry_id = fields.Many2one('res.partner.industry', 'Market')
    year_built = fields.Char('Build Year')
    year_remodeled = fields.Char('YearRemodeled')
    owner_id = fields.Many2one('res.partner', string='Related Owner',
                               required=False, ondelete='restrict',
                               auto_join=True)
    prop_mgmt_id = fields.Many2one('res.partner', 
                                   string="Property Management Company")
    prop_mgmt_id_txt = fields.Char('Property Management Company Key')

