# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class PrintPreNumberedChecks(models.TransientModel):
    _inherit = 'print.prenumbered.checks'

    @api.multi
    def print_checks(self):
        check_number = self.next_check_number
        payment_obj = self.env['account.payment']
        payments = payment_obj.browse(
            self.env.context['payment_ids'])
        for payment in payments:
            payment_id = payment_obj.search(
                [('journal_id', '=', payment.journal_id.id),
                 ('check_number', '=', check_number)])
            if payment_id:
                raise ValidationError(_("Cannot duplicate a check!."))
        return super(PrintPreNumberedChecks, self).print_checks()
