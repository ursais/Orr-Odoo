# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "OSI Roll Tags",
    "version": "12.0.1.1.0",
    "license": "AGPL-3",
    "summary": "Print Roll Tags for Inventory on Incoming Delivery Orders",
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "https://wiki.opensourceintegrators.com/art",
    "depends": [
        "stock"
    ],
    "data": [
        'views/stock_picking.xml',
        'views/stock_production_lot.xml',
        'reports/stock_picking_roll_tags_report.xml',
        'reports/stock_production_lot_roll_tags_report.xml'
    ],
    "application": True,
    "sequence": 0,
}
