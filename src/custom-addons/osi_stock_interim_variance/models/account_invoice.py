# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _get_anglo_saxon_price_unit(self):

        price_unit = super(
            AccountInvoiceLine, self)._get_anglo_saxon_price_unit()
        product = self.product_id
        bom = product.product_tmpl_id.bom_ids and\
            product.product_tmpl_id.bom_ids[0]

        if self.product_id.invoice_policy == "delivery" and \
                bom.type == 'phantom':
            # Put moves in fixed order by date executed
            moves = self.invoice_id._get_last_step_stock_moves()
            components = self.invoice_id._explode_bom(bom)
            price_unit = 0.0
            for product_id in components:
                prod_moves = [
                    m for m in moves if m.product_id.id == product_id]
                for move in prod_moves:
                    if move.state == 'done':
                        price_unit += move.product_qty * abs(move.price_unit)
                price_unit = price_unit and round(price_unit/self.quantity,2) or 0.0
        return price_unit

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _get_products_set(self):
        """ Returns a recordset of the products contained
            in this invoice's lines
        """
        invoice_lines = self.mapped('invoice_line_ids').filtered(
            lambda x: x.product_id and x.display_type == False)
        return invoice_lines.mapped('product_id')

    def _explode_bom(self, bom):

        prod_ids = []
        for line in bom.bom_line_ids:
            if line.product_id.product_tmpl_id.bom_count and \
                    line.product_id.product_tmpl_id.bom_ids[0].type == 'phantom':
                prod_ids += self._explode_bom(
                    line.product_id.product_tmpl_id.bom_ids[0])
            else:
                prod_ids.append(line.product_id.id)
        return prod_ids

    def _anglo_saxon_reconcile_valuation(self, product=False):
        """ Reconciles the entries made in the interim accounts in
            anglosaxon accounting,
            reconciling stock valuation move lines with the invoice's.
        """
        if self._context.get('active_model',False) == 'purchase.order':
            return super(AccountInvoice,self)._anglo_saxon_reconcile_valuation(product=product)
        
        for invoice in self:
            if invoice.company_id.anglo_saxon_accounting:
                stock_moves = invoice._get_last_step_stock_moves()
                product_set = product or invoice._get_products_set()
                for prod in product_set:
                    # product is a bom
                    prod_ids = []
                    if prod.product_tmpl_id.bom_count and \
                            prod.product_tmpl_id.bom_ids[0].type == 'phantom':
                        prod_ids = self._explode_bom(
                            prod.product_tmpl_id.bom_ids[0])
                    else:
                        prod_ids.append(prod.id)
                    if prod.valuation == 'real_time' and stock_moves:
                        # We first get the invoices move lines (taking the
                        # invoice and the previous ones into account)...
                        product_interim_account =\
                            invoice._get_anglosaxon_interim_account(prod)
                        to_reconcile = self.env['account.move.line'].search([
                            ('move_id', '=', invoice.move_id.id),
                            ('product_id', '=', prod.id),
                            ('account_id', '=', product_interim_account.id),
                            ('reconciled', '=', False)
                        ])

                        # And then the stock valuation ones.
                        product_stock_moves = stock_moves.filtered(
                            lambda s: s.product_id.id in prod_ids)
                        for valuation_line in product_stock_moves.mapped(
                                'account_move_ids.line_ids'):
                            if valuation_line.account_id == product_interim_account and \
                                    not valuation_line.reconciled:
                                to_reconcile += valuation_line

                        accounts = prod.product_tmpl_id.get_product_accounts()
                        cogs_account = accounts['expense']
                        if to_reconcile:
                            journal_id = self.env['account.journal'].search([
                                ('type','=','general'), ('name','ilike','Misc'),
                                ('company_id','=', invoice.company_id.id)]) or \
                                        invoice.journal_id
                            to_reconcile.with_context(comment=invoice.number).reconcile(
                                cogs_account, journal_id)

    @api.model
    def _anglo_saxon_purchase_move_lines(self, i_line, res):
        """Fix for rounding errors on price_unit.
           Only final amount should be rounded, not interim data
        """
        inv = i_line.invoice_id
        company_currency = inv.company_id.currency_id
        if i_line.product_id and i_line.product_id.valuation == 'real_time' and i_line.product_id.type == 'product':
            # get the fiscal position
            fpos = i_line.invoice_id.fiscal_position_id
            # get the price difference account at the product
            acc = i_line.product_id.property_account_creditor_price_difference
            if not acc:
                # if not found on the product get the price difference account at the category
                acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ
            acc = fpos.map_account(acc).id
            # reference_account_id is the stock input account
            reference_account_id = i_line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)['stock_input'].id
            diff_res = []
            # calculate and write down the possible price difference between invoice price and product price
            for line in res:
                if line.get('invl_id', 0) == i_line.id and reference_account_id == line['account_id']:
                    # valuation_price unit is always expressed in invoice currency, so that it can always be computed with the good rate
                    valuation_price_unit = company_currency._convert(
                        i_line.product_id.uom_id._compute_price(i_line.product_id.standard_price, i_line.uom_id),
                        inv.currency_id,
                        company=inv.company_id, date=fields.Date.today(), round=False,
                    )
                    line_quantity = line['quantity']

                    if i_line.product_id.cost_method != 'standard' and i_line.purchase_line_id:
                        po_currency = i_line.purchase_id.currency_id
                        po_company = i_line.purchase_id.company_id
                        #for average/fifo/lifo costing method, fetch real cost price from incomming moves
                        valuation_price_unit = po_currency._convert(
                            i_line.purchase_line_id.product_uom._compute_price(i_line.purchase_line_id.price_unit, i_line.uom_id),
                            inv.currency_id,
                            company=po_company, date=inv.date or inv.date_invoice, round=False,
                        )
                        stock_move_obj = self.env['stock.move']
                        valuation_stock_move = stock_move_obj.search([
                            ('purchase_line_id', '=', i_line.purchase_line_id.id),
                            ('state', '=', 'done'), ('product_qty', '!=', 0.0)
                        ])
                        if self.type == 'in_refund':
                            valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_out())
                        elif self.type == 'in_invoice':
                            valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_in())

                        if valuation_stock_move:
                            valuation_price_unit_total = 0
                            valuation_total_qty = 0
                            for val_stock_move in valuation_stock_move:
                                # In case val_stock_move is a return move, its valuation entries have been made with the
                                # currency rate corresponding to the original stock move
                                valuation_date = val_stock_move.origin_returned_move_id.date or val_stock_move.date_expected
                                valuation_price_unit_total += company_currency._convert(
                                    abs(val_stock_move.price_unit) * val_stock_move.product_qty,
                                    inv.currency_id,
                                    company=inv.company_id, date=valuation_date, round=False,
                                )
                                valuation_total_qty += val_stock_move.product_qty
                            valuation_price_unit = valuation_price_unit_total / valuation_total_qty
                            valuation_price_unit = i_line.product_id.uom_id._compute_price(valuation_price_unit, i_line.uom_id)
                            line_quantity = valuation_total_qty

                        elif i_line.product_id.cost_method == 'fifo':
                            # In this condition, we have a real price-valuated product which has not yet been received
                            valuation_price_unit = po_currency._convert(
                                i_line.purchase_line_id.price_unit, inv.currency_id,
                                company=po_company, date=inv.date or inv.date_invoice, round=False,
                            )

                    interim_account_price = valuation_price_unit * line_quantity
                    invoice_cur_prec = inv.currency_id.decimal_places

                    if float_compare(valuation_price_unit, i_line.price_unit, precision_digits=invoice_cur_prec) != 0 and float_compare(line['price_unit'], i_line.price_unit, precision_digits=invoice_cur_prec) == 0:

                        # price with discount and without tax included
                        price_unit = i_line.price_unit * (1 - (i_line.discount or 0.0) / 100.0)
                        tax_ids = []
                        if line['tax_ids']:
                            #line['tax_ids'] is like [(4, tax_id, None), (4, tax_id2, None)...]
                            taxes = self.env['account.tax'].browse([x[1] for x in line['tax_ids']])
                            price_unit = taxes.compute_all(price_unit, currency=inv.currency_id, quantity=1.0)['total_excluded']
                            for tax in taxes:
                                tax_ids.append((4, tax.id, None))
                                for child in tax.children_tax_ids:
                                    if child.type_tax_use != 'none':
                                        tax_ids.append((4, child.id, None))

                        price_before = line.get('price', 0.0)
                        price_unit_val_dif = price_unit - valuation_price_unit

                        price_val_dif = price_before - interim_account_price
                        if inv.currency_id.compare_amounts(i_line.price_unit, valuation_price_unit) != 0 and acc:
                            # If the unit prices have not changed and we have a
                            # valuation difference, it means this difference is due to exchange rates,
                            # so we don't create anything, the exchange rate entries will
                            # be processed automatically by the rest of the code.
                            diff_line = {
                                'type': 'src',
                                'name': i_line.name[:64],
                                'price_unit': price_unit_val_dif, #OSI - 04/16/2019 - cannot round the price unit as it will result in big errors in amount
                                'quantity': (i_line.quantity  - line_quantity) or line_quantity, #OSI - 05/10/2019, Odoo ignores purchase quantity variance
                                'price': inv.currency_id.round(price_val_dif),
                                'account_id': acc,
                                'product_id': line['product_id'],
                                'uom_id': line['uom_id'],
                                'account_analytic_id': line['account_analytic_id'],
                                'tax_ids': tax_ids,
                            }
                            # We update the original line accordingly
                            #OSI - 04/16/2019 - cannot round the price unit as it will result in big errors in amount
                            line['price_unit'] = line['price_unit'] - diff_line['price_unit']
                            #OSI - 05/10/2019, Odoo ignores purchase quantity variance
                            line['quantity'] = line_quantity
                            line['price'] = inv.currency_id.round(line['quantity'] * line['price_unit'])
                            diff_res.append(diff_line)
            return diff_res
        return []
