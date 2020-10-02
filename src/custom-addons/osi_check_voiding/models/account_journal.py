# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    reverse_for_void = fields.Boolean(
        string="Enable Payment Voiding Entries",
        default=False,
    )
