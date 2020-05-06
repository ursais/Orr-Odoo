# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    so_style = fields.Many2one(
        'report.template.settings',
        'Default Order/Quote Style',
        help="The default template style for Sale Order and Quotation reports")
    inv_style = fields.Many2one(
        'report.template.settings',
        'Default Invoice Style',
        help="The default template style for Account Invoice reports")
    pick_style = fields.Many2one(
        'report.template.settings',
        'Default Picking Slip Style',
        help="The default template style for Picking Operations reports")
    dn_style = fields.Many2one(
        'report.template.settings',
        'Default Delivery Note Style',
        help="The default template style for Delivery Slip reports")
    po_style = fields.Many2one(
        'report.template.settings',
        'Default Purchase Order Style',
        help="The default template style for Purchase Order reports")
    rfq_style = fields.Many2one(
        'report.template.settings',
        'Default RFQ Style',
        help="The default template style for Request for Quotation (RFQ) reports")
    fsm_style = fields.Many2one(
        'report.template.settings',
        'Default FSM Style',
        help="The default template style for Field Service Work Order reports")
