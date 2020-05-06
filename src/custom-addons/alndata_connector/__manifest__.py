# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'ALN Data Connector',
    'summary': '''This module allows you to synchronize your Odoo database
                with ALN Data once a month''',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators, Odoo Community Association (OCA),',
    'website': 'http://www.opensourceintegrators.com',
    'category': 'Tools',
    'maintainers': [],
    'depends': [
        'crm',
        'fieldservice',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'data/sync_aln_data_view.xml',
        'views/aln_apartment_view.xml',
        'views/aln_apartment_extended_view.xml',
        'views/aln_construction_view.xml',
        'views/aln_contact_view.xml',
        'views/aln_management_company_view.xml',
        'views/aln_owner_view.xml',
        'views/res_partner_industry_view.xml',
        'views/res_partner_view.xml',
        'views/fsm_location.xml',
    ],
    'installable': True,
}
