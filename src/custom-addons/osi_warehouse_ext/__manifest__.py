# Copyright (C) 2019 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'OSI Warehouse Extended',
    'version': '12.0.1.0.0',
    'author': 'Open Source Integrators',
    'category': 'Inventory',
    'maintainer': 'Open Source Integrators',
    'summary': "Adds Warehouse's Analytic Account to "
               "Customer Invoice created from SO",
    'website': 'http://www.opensourceintegrators.com',
    'depends': [
        'sale_stock',
        'account_asset',
        'account_voucher',
        'purchase_requisition',
        'osi_analytic_segments_sales',
        'osi_analytic_segments_defaults',
        'osi_analytic_segments_expenses',
        'osi_analytic_segments_purchase',
    ],
    'data': [
        'views/account.xml',
        'views/hr_expense_views.xml',
        'views/sale_order_view.xml',
        'report/account_report.xml'
    ],
    'installable': True,
}
