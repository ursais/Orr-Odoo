# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'OSI Stock Receive Product',
    'summary': 'Flexibility to split Picking/Operations/Detailed Operation lines as requested by user',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators',
    'category': 'Stock',
    'website': 'https:www.opensourceintegrators.com',
    'depends': [
        'stock',
        'purchase'
    ],
    'data': [
        'views/stock.xml',
    ],
    'installable': True,
    'application': True,
}
