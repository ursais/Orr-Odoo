# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ALNNewConstruction(models.Model):
    _name = "aln.new.construction"
    _description = "ALN New Construction"

    construction_id_txt = fields.Char('Construction ID')
    new_apartment_id_txt = fields.Char('Apartment ID')
    company = fields.Char('Company')
    project_name = fields.Char('Project Name')
    project_address = fields.Char('Project Address')
    project_city = fields.Char('Project City')
    project_state = fields.Char('Project State')
    project_zip = fields.Char('Project Zip')
    new_num_of_units = fields.Char('Number Of Units')
    property_type = fields.Char('Property Type')
    construction_status = fields.Char('Construction Status')
    start_date = fields.Char('Start Date')
    lease_date = fields.Char('Lease Date')
    occupancy_date = fields.Char('Occupancy Date')
    completion_date = fields.Char('Completion Date')
    progress = fields.Text('Progress')
    new_last_changed_date = fields.Datetime(string="Last changed Date")
    new_published_date = fields.Datetime(string="Published Date")
    new_published_id = fields.Many2one(
        'res.partner',
        'Published by'
    )
    new_state = fields.Selection(
        [('published', 'Published'),
         ('unpublished', 'Unpublished')],
        string='State',
        default='unpublished'
    )
