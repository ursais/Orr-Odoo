# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    restrict_for_void = fields.Boolean(
        string="Payment Voided",
        default=False,
    )
    reason = fields.Text(
        string="Void Reason",
    )

    @api.multi
    def cancel(self):
        for payment in self:
            if payment.journal_id.reverse_for_void:
                for move in payment.move_line_ids.mapped("move_id"):
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
                        "context": {"mode": "payment", "res_id": move.id},
                    }
            return super(AccountPayment, self).button_cancel()
