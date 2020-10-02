# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "OSI Stock Interim Variance",
    "version": "12.0.1.2.0",
    "license": "AGPL-3",
	"description": """
    Write off price variance automatically when price changed between invoice and delivery.
    Address cost rollup on nested bom kits.
    Address exclusion of display lines (sections) in anglo-saxon processing of kits.
    """,
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "images": [],
    "depends": [
        'account',        
        'stock_account',
        'sale_mrp',
        'purchase_stock',
    ],
    "data": [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
