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
        'agreement_legal_sale_fieldservice'
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
