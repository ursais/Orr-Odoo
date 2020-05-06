# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "OSI Partner Average Open Invoice",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summary": "See the average open invoice value for partner records",
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": ["account"],
    "data": [
        "views/res_partner.xml",
        "data/ir_cron.xml",
    ],
    "development_status": "beta",
    "installable": True,
}
