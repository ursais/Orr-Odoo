# Copyright (C) 2018 - TODAY, Open Source Integrators
# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    fsm_equipment_id = fields.Many2one('fsm.equipment', string='FSM Equipment')
