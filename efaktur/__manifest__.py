{
    "name"          : "E-Faktur",
    "version"       : '10.0.2.0.1',
    'license'       : 'AGPL-3',
    "depends"       : ["account", "mail_attach_existing_attachment"],
    'external_dependencies': {'python': ['xlwt']},
    'images'        : ['static/description/main_screenshot.jpg'],
    "author"        : "Alphasoft",
    "description"   : """This module aim to:
                    - Create Object Nomor Faktur Pajak
                    - Add Column Customer such as: 
                        * NPWP, RT, RW, Kelurahan, Kecamatan, Kabupaten, Province
                    - Just Import the file csv at directory data
                    - Export file csv for upload to efaktur""",
    "website"       : "https://www.alphasoft.co.id/",
    "category"      : "Accounting",
    "data"    : [
                "security/ir.model.access.csv",
                "data/res_country_data.xml",
                "views/base_view.xml",
                "views/res_partner_view.xml",
                "views/faktur_pajak_view.xml",
                "views/account_invoice_view.xml",
                "wizard/faktur_pajak_generate.xml",
                "wizard/faktur_pajak_upload.xml",
                "report/efaktur_invoice_csv_view.xml",
    ],
    'price'         : 149.00,
    'currency'      : 'IDR',
    "init_xml"      : [],
    "demo_xml"      : [],
    'test'          : [],    
    "active"        : False,
    "installable"   : True,
    'post_init_hook': '_post_init',
}