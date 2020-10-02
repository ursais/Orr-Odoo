# -*- coding: utf-8 -*-
# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'OSI Batch Invoice Payments Processing',
    'version': '12.0.1.0.0',
    'author': 'Open Source Integrators',
    'summary': """
        OSI Batch Payments Processing for Customers Invoices and
        Supplier Invoices based on Invoice Payment terms
    """,
    'category': 'Extra',
    'maintainer': 'Open Source Integrators',
    'website': 'http://www.opensourceintegrators.com',
    'depends': [
        'osi_custom_payment_term',
        'osi_payment_batch_process'
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'external_dependencies': {
        'python': ['num2words'],
    },
    'installable': True,
}
