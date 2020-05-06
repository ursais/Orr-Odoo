# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "OSI Custom Reports",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["professional_templates", "fieldservice"],
    "website": "www.opensourceintegrators.com",
    "data": [
        "reports/fsm_report_templates.xml",
        "reports/sale_report_templates.xml",
        "reports/account_report_templates.xml",
        "reports/picking_report_templates.xml",
        "reports/purchase_report_templates.xml",
        "reports/fsm_report_data.xml",
        "reports/account_report_data.xml",
        
        "views/fsm_order_views.xml",
        "views/report_style_views.xml",
        "views/res_company_views.xml",
        "views/uom_views.xml",
    ],
    "installable": True,
}
