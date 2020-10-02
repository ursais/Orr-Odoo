# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PaymentModeCustom(models.Model):
    _inherit = 'account.payment.mode'

    send_email_to_partner = fields.Boolean(
        string='Send Email to Partner', default=False
    )
    email_temp_id = fields.Many2one(
        'mail.template',
        string='Email Template',
    )


class PaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def send_vendor_email(self):
        for rec in self:
            if rec.payment_mode_id.send_email_to_partner:
                date_generated = rec.date_generated
                for bank_line in rec.bank_line_ids:
                    partner_name = bank_line.partner_id.name
                    total_amount = bank_line.total_amount
                    payment_ref = bank_line.name
                    line_data = []
                    for payment_line in bank_line.payment_line_ids:
                        line_dict = {
                            'inv_no':
                            payment_line.move_line_id.invoice_id.
                            supplier_invoice_number or '',
                            'payment_amount': payment_line.total_amount,
                            'discount': payment_line.discount_amount, }
                        line_data.append(line_dict)
                    template = rec.payment_mode_id.email_temp_id
                    if not template:
                        template = self.env.ref(
                            "account_payment_order_vendor_email."
                            "fulton_ach_payment_email_template")
                    partner_email_id = bank_line.partner_id.email
                    if partner_email_id:
                        template.write({'email_to': partner_email_id})
                        template.with_context(
                            {
                                'date': date_generated,
                                'partner_name': partner_name,
                                'total_amount': total_amount,
                                'payment_ref': payment_ref,
                                'line_data': line_data
                            }
                        ).send_mail(rec.id, force_send=True)
                        rec.message_post(body=(
                            "An email is sent successfully to %s \
                            Vendor." % partner_name))
                    else:
                        rec.message_post(body=(
                            "An email is not able to send to %s \
                            Vendor." % partner_name))

    @api.multi
    def generated2uploaded(self):
        res = super(PaymentOrder, self).generated2uploaded()
        if self.payment_mode_id.send_email_to_partner:
            self.send_vendor_email()
        return res
