{
    'name': "Inventory Backdate",

    'summary': """
Total solution for backdate stock & inventory operations""",

    'summary_vi_VN': """
Nhập ngày trong quá khứ cho các hoạt động kho vận
    	""",

    'description': """
The problem
===========
In Odoo, when you carry out stock & inventory operations such as validating a stock transfer, doing inventory adjustment, creating scrap,
Odoo applies the current date and time for the move automatically which is sometimes not what you want. For example,
when you were inputting data for the past operations or when you start a new Odoo implementation that requires data from the past.

The solution
============
This module gives you a chance to input your desired date in the past. The following operations are currently supported with backdate

1. Stock Transfer

   During validation of stock transfers, when you click on Validate button, a new window will be popped out with a datetime field for your input.
   The default value for the field is the current datetime.

2. Inventory Adjustment

   During validating a scrap from either a stock transfer or a standalone scrap order, a new window will be popped out with a datetime field for your input.
   The default value for the field is the current datetime.

3. Stock Scrapping

   During validating a scrap from either a stock transfer or a standalone scrap order, a new window will be popped out with a datetime field for your input.
   The default value for the field is the current datetime.

The backdate you input will also be used for accounting entry's date if the product is configured with automated stock valuation.
It supports all available costing methods in Odoo (i.e. Standard Costing, Average Costing, FIFO Costing)

Backdate Operations Control
---------------------------

By default, only users in the "Inventory / Manager" group can carry out backdate operations in Inventory application.
Other users must be granted to the access group **Backdate Operations** before she or he can do it.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': "https://www.tvtmarine.com",
    'live_test_url': "https://v12demo-int.erponline.vn",
    'support': "support@ma.tvtmarine.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_stock_picking_validate_manual_time'],

    # always loaded
    'data': [
        'wizard/stock_inventory_backdate_wizard_views.xml',
        'wizard/stock_scrap_backdate_wizard_views.xml',
        'wizard/stock_warn_insufficient_qty_scrap_views.xml',
    ],

    'images' : [
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 81.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
