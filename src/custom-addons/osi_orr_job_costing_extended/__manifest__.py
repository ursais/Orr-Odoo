# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Job Costing and Job Cost Sheet Extended',
    'summary': 'This module extend the functionality of Project Job '
    'Costing and Job Cost Sheet.',
    'license': 'AGPL-3',
    'version': '12.0.1.0.0',
    'category': 'Projects',
    'author': 'Open Source Integrators',
    'website': 'https://github.com/ursais/osi-addons',
    'depends': [
        'odoo_job_costing_management',
        'odoo_customer_progress_billing',
    ],
    'data': [
        'data/sale_estimate_mail_data.xml',
        'views/job_costing_view.xml',
        'views/sale_estimate_job_view.xml',
        'views/sale_order_view.xml',
        'views/project_view.xml',
        'views/account_invoice_view.xml',
        'report/project_financials_view.xml',
    ],
}
