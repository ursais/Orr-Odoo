# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project by Phases',
    'version': '1.1.3',
    'price': 9.0,
    'currency': 'EUR',
    'depends': [
                'project',
                ],
    'license': 'Other proprietary',
    'category': 'Projects',
    'summary': 'Allow you to manage your project and task by phases',
    'description': """
Odoo Project Phases
Odoo Project Phases
project phase
task phase
scrum project
project scrum
project phases
task phases
phase management
phase
odoo phase
project task
project app
task app
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://youtu.be/HmvGPM8Ddkg',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project_phase_view.xml',
        'views/project_view.xml',
        'views/task_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
