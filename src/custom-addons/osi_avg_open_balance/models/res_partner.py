# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    track_open_invoice_due = fields.Boolean("Track AVG Open Invoice Due", default=False)
    open_invoice_days = fields.Float(default=0.00)
    open_invoice_total = fields.Float(default=0.00)
    open_invoice_average = fields.Float(string="AVG Open Invoice Due")

    def _cron_compute_open_invoice_average(self):
        partners = self.search([('track_open_invoice', '=', True)])
        for partner_id in partners:
            partner_id.open_invoice_days = partner_id.open_invoice_days + 1.00
            if partner_id.total_due:
                    partner_id.open_invoice_total = partner_id.open_invoice_total + partner_id.total_due
            partner_id.open_invoice_average = partner_id.open_invoice_total / partner_id.open_invoice_days
