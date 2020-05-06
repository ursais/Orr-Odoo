.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
OSI Stock Receive Split
=======================

This module will have flexibility to split Detailed Operation lines into user defined lines.


Usage
=====

To use this module, you need to:
1- Create PO, make sure you use product that has Traceability NOT as 'By Unique Serial Number' with qty 150 and CONFIRM
2- Open Receipt [Smart Button] from PO form View
3- On 'Operation' tab, at the end of your product click on button icon and it will open form view 'Detailed Operation'
4- Core odoo will function as it is and will get reserved qty 150.
5- If you need customized No. of lines, Click on button 'Delete all Lines', Make No of Lines as 15 and click button 'Compute'
6- You should see it will create 15 lines with 10 reserved qty on each lines (total 150) and 'Compute' button
   should not be visible anymore and No of Lines field should be readonly now. And button 'Delete all Lines' should be visible.


Credits
=======

Images
------

Contributors
------------

* Mayank Gosai <mgosai@opensourceintegrators.com>

Funders
-------

The development of this module has been financially supported by:

* Open Source Integrators <http://www.opensourceintegrators.com>