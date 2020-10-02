# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    @api.depends('debit', 'credit', 'amount_currency', 'currency_id', 'matched_debit_ids', 'matched_credit_ids', 'matched_debit_ids.amount', 'matched_credit_ids.amount', 'move_id.state')
    def _amount_residual(self):
    
        super(AccountMoveLine, self)._amount_residual()
        for line in self:
            if line.currency_id and line.amount_currency and line.amount_residual_currency and not line.amount_residual:
                amount1 = abs(line.currency_id.round(line.amount_residual_currency))
                amount2 = 0.01
                if amount1 == amount2:
                    line.amount_residual_currency = amount1 - amount2
                    line.amount_residual = 0.0

    def _create_writeoff(self, writeoff_vals):
        reconcile_line = super(AccountMoveLine, self)._create_writeoff(writeoff_vals)
        
        if self._context.get('comment', False):
            reconcile_line.name = _('Reclassify to Cost of Goods Sold')
            reconcile_line.move_id.ref = self._context.get('comment')
            
            for line in reconcile_line.move_id.line_ids:
                line.name = _('Reclassify to Cost of Goods Sold')
        
        return reconcile_line