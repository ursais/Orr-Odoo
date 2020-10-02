# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Void Payment",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators",
    "maintainers": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": ["account_payment", "account_cancel"],
    "data": [
        "views/account_journal_view.xml",
        "views/account_move_view.xml",
        "views/account_payment_view.xml",
        "wizards/cancel_void_payment.xml",
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
