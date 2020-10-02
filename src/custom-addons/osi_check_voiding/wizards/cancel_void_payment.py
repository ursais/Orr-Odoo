# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CancelVoidPayment(models.TransientModel):
    _name = "cancel.void.payment"
    _description = "Void Payment"

    reason = fields.Text(
        string="Reason for the cancel",
    )

    @api.multi
    def cancel_payment_entry(self):
        if self._context.get("mode", False) == "payment":
            move_id = self.env["account.move"].browse(
                self._context.get("res_id"))
        else:
            move_id = self.env["account.move"].browse(
                self._context.get("active_id"))
        if move_id.restrict_for_void:
            raise UserError(_("This transaction is already voided."))
        for move_line in move_id.line_ids:
            move_line.remove_move_reconcile()
        move_id.write(
            {
                "narration": self.reason,
                "restrict_for_void": True,
            }
        )
        new_move_date = date.today()
        reverse_move = move_id.reverse_moves(
            date=new_move_date, journal_id=move_id.journal_id, auto=False
        )

        if reverse_move:
            reverse_move_id = self.env["account.move"].browse(reverse_move)
            reverse_move_id.write(
                {
                    "restrict_for_void": True,
                    "void_txn": move_id.id,
                }
            )
            move_id.write({"void_txn": reverse_move_id.id})

            if self._context.get("mode", False) == "payment":
                rec = self.env["account.payment"].browse(
                    self._context.get("active_id"))
                rec.write(
                    {
                        "state": "cancelled",
                        "restrict_for_void": True,
                        "reason": self.reason,
                    }
                )
