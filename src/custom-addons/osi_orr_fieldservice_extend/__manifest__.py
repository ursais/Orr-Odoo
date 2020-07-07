# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'OSI ORR Field Service Ehancements',
    'summary': 'This module will improve FSM Order form view and stages',
    'license': 'AGPL-3',
    'version': '12.0.1.0.0',
    'category': 'Field Service',
    'author': 'Open Source Integrators',
    'depends': [
        'fieldservice_sale',
        'account_accountant',
        'fieldservice_sale_recurring',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fsm_order.xml',
        'views/fsm_location.xml'
        'views/fsm_equipment.xml',
        'views/fsm_person.xml',
        'views/fsm_recurring.xml',
    ],
    'maintainers': [
        'smangukiya',
    ],
    "installable": True,
}
