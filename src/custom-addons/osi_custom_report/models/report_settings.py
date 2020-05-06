# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TemplateSettings(models.Model):
    _inherit = 'report.template.settings'

    @api.model
    def _default_fsm_template(self):
        def_tpl = self.env['ir.ui.view'].search(
            [
                ('key',
                 'like',
                 '%FSM\_%\_document'),
                ('type',
                 '=',
                 'qweb')],
            order='key asc',
            limit=1)
        return def_tpl or self.env.ref(
            'fieldservice.report_fsm_order_document')
    
    template_inv = fields.Many2one(
        'ir.ui.view',
        'Invoice Template',
        domain="[('type', '=', 'qweb'), ('key', 'like', '%INVOICE\_%\_document' )]",
        required=False)
    template_so = fields.Many2one(
        'ir.ui.view',
        'Order/Quote Template',
        domain="[('type', '=', 'qweb'), ('key', 'like', '%SO\_%\_document' )]",
        required=False)
    template_po = fields.Many2one(
        'ir.ui.view',
        'Purchase Order Template',
        domain="[('type', '=', 'qweb'), ('key', 'like', '%PO\_%\_document' )]",
        required=False)
    template_rfq = fields.Many2one(
        'ir.ui.view',
        'RFQ Template',
        domain="[('type', '=', 'qweb'), ('key', 'like', '%RFQ\_%\_document' )]",
        required=False)
    template_dn = fields.Many2one(
        'ir.ui.view',
        'Delivery Note Template',
        domain="[('type', '=', 'qweb'), ('key', 'like', '%DN\_%\_document' )]",
        required=False)
    template_pk = fields.Many2one(
        'ir.ui.view',
        'Picking Slip Template',
        domain="[('type', '=', 'qweb'), ('key', 'like', '%PICK\_%\_document' )]",
        required=False)
    template_fsm = fields.Many2one(
        'ir.ui.view',
        'FSM Order Template',
        default=_default_fsm_template,
        domain="[('type', '=', 'qweb'), ('key', 'like', '%FSM\_%\_document' )]",
        required=False)
