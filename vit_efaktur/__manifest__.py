{
	"name": "E-Faktur Management for Indonesia Tax",
	"version": "1.11",
	"depends": [
		"account",
		"stock",
		"vit_kelurahan",
	],
	'images': ['static/description/images/main_screenshot.png'],
	"author": "vitraining.com",
	"website": "www.vitraining.com", 
    'category': 'Accounting',
    'price':'30',
    'currency': 'USD',
	"category": "Accounting",
	"summary": "Manage, Export and Import, Tag Invoice with E-Faktur, the online tax management system for Indonesian companies",
	"description": """\


Version 1.11
* bug fixed Export Product CSV
* bug fixed Export Partner CSV
* bug fixed Export FP. Masukan CSV

Version 1.10
* bug fixed date_invoice
* bug fixed on download CSV


Version 1.9
* menu position
* bug fixes invoice view

Version 1.8
* inv.date_invoice.month

Version 1.7
* Bugs fix on combined efaktur total DPP, referene invoice
* Save file to binary field, not file on static folder

Version 1.6
* Bugs fix on combined efaktur total DPP

Version 1.5
* Bugs fix on combined efaktur

Version 1.4
* Multi invoice single efaktur

Version 1.3
* Encode utf8

Version 1.2
* Kawasan berikat

Version 1.0
* Pengelolaan eFaktur Pajak Indonesia
* created menu:
* created object
* created views
* logic:

""",
	"data": [
		"security/ir.model.access.csv",
		"wizard/generate.xml",
		"wizard/product.xml",
		"wizard/partner.xml",
		"wizard/pk.xml",
		"wizard/auto.xml",
		"wizard/pm.xml",
		"wizard/assign.xml",

		"view/product.xml",
		"view/efaktur.xml",
		"view/partner.xml",
		"view/invoice.xml",
		"view/invoice_supplier.xml",
		"report/invoice.xml",


	],
	"application": True,
	"installable": True,
	"auto_install": False,
}