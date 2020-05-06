# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class Unit(models.Model):
    _inherit = 'uom.uom'
    
    short_code = fields.Char(
        'Abbreviation',
        help='Abbreviation for the Unit to be used on reports')
