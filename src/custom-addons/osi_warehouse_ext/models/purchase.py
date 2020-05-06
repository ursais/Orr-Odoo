# Copyright (C) 2019 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    analytic_segment_one_id = fields.Many2one(
        'analytic.segment.one',
        string='Job Type',
        copy=False)
