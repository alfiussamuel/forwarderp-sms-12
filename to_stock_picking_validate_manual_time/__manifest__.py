# -*- coding: utf-8 -*-
{
    'name': "Stock Transfers Backdate",

    'summary': """
    Manual validation date for stock transfers.
        """,

    'description': """
The problem
===========
In Odoo, when you validate a stock transfer, Odoo applies the current time for the transfer date automatically which is sometimes not what you want. For example, you input data for the past.

The solution
============
This module gives the user a chance to input the transfer date manually. During validation of stock transfers,
when the user click on Validate button, a new window will be popped out with a datetime field for your input.
The default value for the field is the current datetime.

The date you input here will also be used for accounting entry's date if the product is configured with automated stock valuation.

Backdate Operations Control
---------------------------

By default, only users in the "Inventory / Manager" group can carry out backdate operations in Inventory application.
Other users must be granted to the access group **Backdate Operations** before she or he can do it.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'author': 'T.V.T Marine Automation (aka TVTMA)',
    'website': 'https://www.tvtmarine.com',
    'live_test_url': 'https://v12demo-int.erponline.vn',
    'support': 'support@ma.tvtmarine.com',

    'category': 'Warehouse',
    'version': '0.3',

    'depends': ['stock', 'to_backdate'],

    'data': [
        'security/module_security.xml',
        'wizard/stock_picking_validate_manual_time_views.xml'
    ],
    'application': False,
    'installable': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
