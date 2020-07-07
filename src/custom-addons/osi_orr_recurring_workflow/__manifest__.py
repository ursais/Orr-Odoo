# -*- coding: utf-8 -*-

{
    'name': 'OSI ORR Recurring Workflow',
    'version': '12.0.1.0.0',
    'author': 'Open Source Integrators',
    'category': 'Sales',
    'maintainer': 'Open Source Integrators',
    'summary': 'ORR Recurring Workflow',
    'website': 'http://www.opensourceintegrators.com',
    'depends': [
        'fieldservice_sale_recurring',
        'agreement_legal_sale_fieldservice',
        'osi_orr_fieldservice_extend'
    ],
    'data': [
        'views/sale.xml',
        'views/account.xml',
        'views/fsm_order.xml',
        'views/fsm_recurring.xml'
    ],
    'installable': True,
}
