# -*- coding: utf-8 -*-

{
    'name': "Debranding Kit",
    'version': '12.0.0',
    'author': 'Planet-Odoo',
    "support": "http://www.planet-odoo.com/",
    'category': 'Tools',
    'depends': [
        'web',
        'mail',
        'web_settings_dashboard',
        'portal',

    ],
    'data': [
        'views/data.xml',
        'views/views.xml',
        'views/js.xml',
        'views/webclient_templates.xml',
        'security/ir.model.access.csv',

        ],
    'qweb': [
        'static/src/xml/web.xml',
        'static/src/xml/dashbord.xml',

    ],
    'images': ['static/description/main.png'],
    'license': "LGPL-3",
    'auto_install': False,
    'installable': True
}
