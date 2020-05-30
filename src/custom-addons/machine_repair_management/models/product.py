# -*- coding: utf-8 -*

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    brand = fields.Char(
        string = "Brand"
    )
    color = fields.Char(
        string = "Color"
    )
    model = fields.Char(
        string="Model"
    )
    year = fields.Integer(
        string="Year"
    )
    is_machine = fields.Boolean(
        string="Is Machine"
    )
    machine_repair_ids = fields.One2many(
        'machine.repair.support',
        'product_id',
        string='Machine Repair Request',
        copy=False,
        readonly=True,
    )
    
    
    @api.multi
    def action_machine_repair_request(self):
        self.ensure_one()
        res = self.env.ref('machine_repair_management.action_machine_repair_support')
        res = res.read()[0]
        res['domain'] = str([('product_id', '=', self.id)])
        return res
