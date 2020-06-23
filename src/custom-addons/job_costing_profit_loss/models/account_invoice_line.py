# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    customer_job_cost_id = fields.Many2one(
        'job.costing',
        string='Job Cost Center',
    )
    customer_job_cost_line_id = fields.Many2one(
        'job.cost.line',
        string='Job Cost Line',
    )
    

