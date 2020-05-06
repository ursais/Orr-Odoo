# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Artisent Floors",
    "version": "12.0.1.2.0",
    "license": "AGPL-3",
    "summary": "Artisent Floors Configuration and Data",
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "https://wiki.opensourceintegrators.com/art",
    "depends": [
        # Odoo Addons
        "crm",
        "purchase",
        "portal",
        "sale_stock",
        "sale_margin",
        "delivery",
        # Enterprise Addons
        "documents",
        "account_accountant",
        # OCA Addons
        "account_invoice_transmit_method",
        "fieldservice_account",
        "fieldservice_purchase",
        "fieldservice_sale",
        "fieldservice_skill",
        "fieldservice_vehicle_stock",
        "account_banking_ach_base",
        "account_banking_ach_credit_transfer",
        "account_banking_ach_direct_debit",
        "account_banking_mandate",
        "account_banking_mandate_sale",
        "l10n_us_account_profile",
        # OSI Addons
        "osi_custom_payment_term",
        "osi_ach_discount_connector",
        "osi_batch_invoice_payment_process",
        "osi_custom_payment_term",
        "osi_payment_batch_process",
        "osi_warehouse_ext",
        "avatax_connector",
        "osi_payment_method",
        # Private Addons
    ],
    "data": [
        'data/fsm_stage.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/fsm_location.xml',
        'views/fsm_order.xml',
        'views/account_invoice_view.xml',
        'views/stock_request.xml',
        'security/ir.model.access.csv'
    ],
    "application": True,
    "sequence": 0,
}
