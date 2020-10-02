# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _anglo_saxon_sale_move_lines(self, name, product, uom, qty, price_unit,
                                     currency=False, amount_currency=False,
                                     fiscal_position=False,
                                     account_analytic=False,
                                     analytic_tags=False):

        # consumables kits may also be tracked for value
        if product.type == 'consu' and \
           product.product_tmpl_id.bom_count and \
           product.product_tmpl_id.bom_ids[0].type == 'phantom':
            accounts = product.product_tmpl_id.get_product_accounts(
                fiscal_pos=fiscal_position)
            # debit account dacc will be the output account
            dacc = accounts['stock_output'].id
            # credit account cacc will be the expense account
            cacc = accounts['expense'].id
            if dacc and cacc:
                return [
                    {
                        'type': 'src',
                        'name': name[:64],
                        'price_unit': price_unit,
                        'quantity': qty,
                        'price': price_unit * qty,
                        'currency_id': currency and currency.id,
                        'amount_currency': amount_currency,
                        'account_id': dacc,
                        'product_id': product.id,
                        'uom_id': uom.id,
                        'account_analytic_id': account_analytic and
                        account_analytic.id,
                        'analytic_tag_ids': analytic_tags and
                        analytic_tags.ids and
                        [(6, 0, analytic_tags.ids)] or False,
                    },

                    {
                        'type': 'src',
                        'name': name[:64],
                        'price_unit': price_unit,
                        'quantity': qty,
                        'price': -1 * price_unit * qty,
                        'currency_id': currency and currency.id,
                        'amount_currency': -1 * amount_currency,
                        'account_id': cacc,
                        'product_id': product.id,
                        'uom_id': uom.id,
                        'account_analytic_id': account_analytic and
                        account_analytic.id,
                        'analytic_tag_ids': analytic_tags and
                        analytic_tags.ids and
                        [(6, 0, analytic_tags.ids)] or False,
                    },
                ]
            else:
                return []

        elif product.type == 'product':
            return super(ProductProduct, self)._anglo_saxon_sale_move_lines(
                name, product, uom, qty, price_unit, currency=currency,
                amount_currency=amount_currency,
                fiscal_position=fiscal_position,
                account_analytic=account_analytic, analytic_tags=analytic_tags)
        return []
