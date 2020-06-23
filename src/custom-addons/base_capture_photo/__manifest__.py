# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Base Scan and Upload Images on My Account Portal',
    'version': '1.1.1',
    'category' : 'Project',
    'license': 'Other proprietary',
    'price': 29.0,
    'currency': 'EUR',
    'summary': """Base Framework Module For Scan and Upload Images on My Account Portal""",
    'description': """
scan
scan image
scan photo
photo scan
image scan
photo
image
upload photo
upload image
photo upload
photo download
Scan and Upload Images for records
Uploaded Images Stored As Attachments and Also Chatter
Preview of Submitted Images

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': [
        'static/description/images.jpg'
    ],
    'depends': [
        'portal',
        'website'
    ],
    'data':[
        'views/snap_image_template_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
