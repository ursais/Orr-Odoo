# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Merge Customer Invoices/Vendor Bills',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Accounting',
    'description':
        """
        This Module add below functionality into odoo

        1.Merge draft Customer Invoices/Vendor Bills which from same Customer/Vendor and draft state.
        2.When you merge Invoices/Vendor Bills, a merged Invoice/Vendor Bill is created as new Invoice/Vendor Bill
        3.Instead of creating new merged Invoice/Bill you can also merge selected Invoices/Bills in existing Invoices/Bills
        4.Once Invoices/Bills are merged as new Invoice/Bill or in Existing Invoice/Bill, selected Invoices/Bills will be Cancelled
        6.Note : You can't merge Invoices/Bills which are not in draft state or not from similar Customer/Vendor
        
        Merge Invocie 
        Merge Customer Invocie 
        odoo merge customer invoice
        merge vendor bills
        odoo merge vendro bills
        merge customer invocie with same customer 
        merge customer invocie with same invoice state
        Odoo merge customer invocie with same customer 
        Odoo merge customer invocie with same invoice state
        merge vendor bills  with same vendor
        merge vendor bills  with same invoice state
        Invoice merging 
        Vendor bill merginig
        Odoo merging
        odoo customer invoice merge 
        odoo vendor bill merge
        odoo bill merge 
Merge invoice 
Odoo merge invoice 
Manage invoice 
Odoo manage invoice 
Merge customer invoice 
Oodo merge customer invoice 
Merge vendor bill
Odoo merge vendor bill 
Merge vendor invoice 
Oodo merge vendor invoice 
This module helps you to merge Invoices/Bills which are from similar Customer/Vendor
Odoo This module helps you to merge Invoices/Bills which are from similar Customer/Vendor
Merge draft Invoices/Bills which are from same Customer/Vendor 
Odoo Merge draft Invoices/Bills which are from same Customer/Vendor 
When you merge Invoices/Bills, a merged Invoice/Bill is created as new Invoice/Bill 
Odoo When you merge Invoices/Bills, a merged Invoice/Bill is created as new Invoice/Bill  
Instead of creating new merged Invoice/Bill you can also merge selected Invoices/Bills in existing Invoices/Bills
Odoo Instead of creating new merged Invoice/Bill you can also merge selected Invoices/Bills in existing Invoices/Bills
Manage merge invoice 
Odoo manage merge invoice 
Manage merge customer invoice 
Odoo manage merge customer invoice 
        
        
        
        
    """,
    'summary': 'Odoo app will help to Merge Invoices/Vendor Bills of similar Customer/Vendor',
    'depends': ['account', 'account_cancel'],
    'data': [
        'wizard/merge_invoices_view.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':25.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
