from odoo import api, fields, models

class POBackorderWizard(models.TransientModel):

    _name = "pobackorder.report.wizard"
    _description = "PO Backorder Report Wizard"
        
    def action_print_report(self, data):
        data = self.env['purchase.order.line'].search(['&', '&', ('state', '=', 'purchase'), ('product_type','=', 'product'),'|',('bo_value','!=',0),('uigr_value','!=',0)])
        return self.env.ref('osi_po_backorder_report.action_po_backorder_report').report_action(data)
