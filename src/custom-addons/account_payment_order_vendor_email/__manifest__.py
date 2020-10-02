# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Order Email",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators",
    "maintainers": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": ["account_payment_order", "account_payment_mode"],
    "data": [
        "data/ach_payment_email_template.xml",
        "views/account_payment_mode_view.xml",
        "views/account_payment_order_view.xml",
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
