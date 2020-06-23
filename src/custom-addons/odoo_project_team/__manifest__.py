# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Team for Constrcution and Contracting',
        'price': 19.0,

    'version': '1.1',
    'depends': [
            'odoo_job_costing_management',
    ],
    'category' : 'Projects',

    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """This app allow you to set project team on Project, Job order and Job Cost Sheet.""",
    'description': """
Project Teams
Project Team on Project
Project Team on Job Order
Project Team on Cost Sheet
Project Team on Job Order Report
Project Team on Job Cost Sheet Report
Cost Sheet Tags on Job Cost Sheet
Tags on Job Cost Sheet
Project Team on Job Order PDF Report
project team
team management
team manager
projects team
project team
team member
team user
odoo team
job team
construction team
contracting team
job contracting team
team
teams
team odoo
job cost sheet
Odoo Job Costing And Job Cost Sheet (Contracting)
Odoo job cost sheet
job cost sheet odoo
contracting odoo
odoo construction
job costing (Contracting)
odoo job costing (Contracting)
odoo job costing Contracting
job order odoo
work order odoo
job Contracting
job costing
job cost Contracting
odoo Contracting
Contracting odoo job
Jobs
Jobs/Configuration
Jobs/Configuration/Job Types
Jobs/Configuration/Stages
Jobs/Job Costs
Jobs/Job Costs/Job Cost Sheets
Jobs/Job Orders
Jobs/Job Orders/Job Notes
Jobs/Job Orders/Job Orders
Jobs/Job Orders/Project Issues
BOQ
Job Costing
Notes
Project Report
Task Report
Jobs/Materials / BOQ 
Jobs/Materials / BOQ /Material Requisitions/ BOQ
Jobs/Materials / BOQ /Materials
Jobs/Projects
Jobs/Projects/Project Budgets
Jobs/Projects/Project Notes
Jobs/Projects/Projects
Jobs/Sub Contractors 
Jobs/Sub Contractors /Sub Contractors
material requision odoo
Contracting
job Contracting
job sheet
job cost Contracting
job cost plan
costing
cost Contracting
subcontracting
Email: contact@probuse.com for more details.
This module provide Construction Management Related Activity.
Construction
Construction Projects
Budgets
Notes
Materials
Material Request For Job Orders
Add Materials
Job Orders
Create Job Orders
Job Order Related Notes
Issues Related Project
Vendors
Vendors / Contractors

Construction Management
Construction Activity
Construction Jobs
Job Order Construction
Job Orders Issues
Job Order Notes
Construction Notes
Job Order Reports
Construction Reports
Job Order Note
Construction app
Construction 

job costing
job cost sheet
cost sheet
project cost sheet
project planning
project sheet cost
job costing plan
Construction cost sheet
Construction job cost sheet
Construction jobs
Construction job sheet
Construction material
Construction labour
Construction overheads
Construction sheet plan
costing
workshop
job workshop
workshop
jobs
cost centers
Construction purchase order
Construction activities
Basic Job Costing
Job Costing Example
job order costing
job order
job orders
Tracking Labor
Tracking Material
Tracking Overhead
overhead
material plan
job overhead
job labor
Job Cost Sheet

Construction Management


    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
    'live_test_url': 'https://youtu.be/IGQ5NLQL5F8',

    'data':[
        'security/ir.model.access.csv',
        'views/project_team_view.xml',
        'views/costsheet_tag_view.xml',
        'views/project_view.xml',
        'views/job_costsheet_view.xml',
        'views/job_costing_report.xml',
        'views/task_report.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
