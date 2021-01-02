
{
    "name": "GSLab Backend Theme",
    "summary": "YABT based on responsive web client and inspired by Openworx",
    "version": "12.0.1.1.0",
    "category": "Themes/Backend",
    "website": "https://www.gslab.it",
    "author": "Giovanni - GSLab",
    "live_test_url": "http://odoo.gslab.it:8069",
    "price": "49",
    "currency": "EUR",
    "license": "LGPL-3",
    "support": "giovanni@gslab.it",
    "installable": True,
    "depends": [
        'web_responsive',
        'web_widget_color'
    ],
    "data": [
        'views/assets.xml',
        'views/res_config_settings_views.xml'
    ],
    "images": [
        'static/description/banner.png',
        'static/description/theme_screenshot.png'
    ],
    "qweb": [
        'static/src/xml/apps.xml',
    ]
}
