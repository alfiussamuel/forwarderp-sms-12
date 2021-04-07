{
    'name': "Backdate Operations Access Rights",

    'summary': """
Access group for backdate operations""",

    'summary_vi_VN': """
    	""",

    'description': """
This module is intended for other backdate-related modules to extend such as Stock Transfers Backdate, Inventory Backdate, Sales Confirmation Backdate, etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Module này là module cơ sở để các module liên quan đến backdate có thể kế thừa.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': "https://www.tvtmarine.com",
    'live_test_url': "https://v12demo-int.erponline.vn",
    'support': "support@ma.tvtmarine.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'wizard/abstract_inventory_backdate_wizard_views.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}