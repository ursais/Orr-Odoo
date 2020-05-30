# -*- coding: utf-8 -*-

from odoo import fields, models, api

class CustomJobOrderCategory(models.Model):
    _name = 'custom.job.order.category'

    name = fields.Char(
    	string="Name",
    	required=True,
	)
