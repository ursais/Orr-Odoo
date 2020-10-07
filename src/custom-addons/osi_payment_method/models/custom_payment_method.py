# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class CustomPaymentMethod(models.Model):
    _name = "custom.payment.method"
    _description = "User Payment Type"

    name = fields.Char(string="User Payment Type")
    code = fields.Char(string="Code")

