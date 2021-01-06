{
    'name' : 'BSC - Sumber Mas Sentosa',
    'version' : '10',    
    'category': 'Custom',    
    'author' :'Alfius Samuel Sutopo',        
    'depends' : ['product','stock', 'sale', 'account', 'base'],
    'data': [                    
        'views/sms_view.xml',
        'views/sms_menu.xml',    
        'views/invoices.xml',
        'views/mrp_production_templates.xml',
        'wizard/trigger_onchange_view.xml',        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
