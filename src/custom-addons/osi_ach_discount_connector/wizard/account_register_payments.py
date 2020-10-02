# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.multi
    def make_payments(self):
        payment_method = self.payment_method_id
        if self.is_customer:
            invoice_payment_method = self.invoice_customer_payments[
                0
            ].invoice_id.payment_mode_id.payment_method_id
        else:
            invoice_payment_method = self.invoice_payments[
                0
            ].invoice_id.payment_mode_id.payment_method_id
        if (
            payment_method.code in ("ACH-In", "ACH-Out") and not invoice_payment_method
        ) or (
            payment_method.code not in ("ACH-In", "ACH-Out") and invoice_payment_method
        ):
            raise UserError(_("Payment Method does not match Invoice payment mode."))
        if payment_method:
            if payment_method.code in ("ACH-In", "ACH-Out"):
                action = False
                payment_mode_id = self.env["account.payment.mode"].search(
                    [
                        ("payment_type", "=", self.payment_type),
                        ("payment_method_id", "=", payment_method.id),
                        ("payment_order_ok", "=", True),
                    ],
                    limit=1,
                )
                payment_line_pool = self.env["account.payment.line"]
                # Update invoice with Payment mode
                if payment_mode_id:
                    for payment_line in self.invoice_payments:
                        invoice_id = payment_line.invoice_id
                        invoice_id.write({"payment_mode_id": payment_mode_id.id})
                        invoice_id.move_id.line_ids.write(
                            {"payment_mode_id": payment_mode_id.id}
                        )
                        action = invoice_id.with_context(
                            payment_date=self.payment_date
                        ).create_account_payment_line()
                        # Find related ACH transaction line
                        domain = [
                            ("invoice_id", "=", invoice_id.id),
                            ("state", "=", "draft"),
                        ]
                        ach_transaction_line = payment_line_pool.search(domain)
                        if ach_transaction_line:
                            ach_transaction_line.write(
                                {
                                    "payment_difference_handling": payment_line.payment_difference_handling,
                                    "writeoff_account_id": payment_line.writeoff_account_id.id,
                                    "reason_code": payment_line.reason_code.id,
                                    "note": payment_line.note,
                                    "amount_currency": payment_line.paying_amt,
                                    "payment_difference": payment_line.payment_difference,
                                }
                            )
                return action
        res = super(AccountRegisterPayments, self).make_payments()
        return res
