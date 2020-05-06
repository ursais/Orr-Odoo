"""Scrap Stock Quantity."""
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class StockScrap(models.Model):
    """Stock Scrap."""

    _inherit = 'stock.scrap'

    def _scrap_batch_order(self):

        active_ids = self._context.get('active_ids') or []
        for rec in self.browse(active_ids):
            rec.do_scrap()
