# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    restrict_for_void = fields.Boolean(
        string="Entry Voided",
        default=False,
    )
    void_txn = fields.Many2one(
        "account.move",
        string="Void Txn",
        default=False,
    )

    @api.multi
    def button_cancel(self):
        for move in self:
            if move.journal_id.reverse_for_void:
                if move.restrict_for_void:
                    raise UserError(_("This transaction is already voided."))

                return {
                    "name": ("Add a reason for cancel"),
                    "view_type": "form",
                    "view_mode": "form",
                    "res_model": "cancel.void.payment",
                    "view_id": False,
                    "type": "ir.actions.act_window",
                    "target": "new",
                    "context": {"mode": "entry"},
                }
            else:
                return super(AccountMove, self).button_cancel()
