# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import xlwt
import time
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from odoo.api import Environment

from odoo.report import report_sxw
from report_csv import report_csv
from utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
import logging
_logger = logging.getLogger(__name__)

_column_sizes = [
    ('A', 18),
    ('B', 18),
    ('C', 18), 
    ('D', 18), 
    ('E', 18), 
    ('F', 18), 
    ('G', 18),  
    ('H', 18),        
    ('I', 18),        
    ('J', 18),        
    ('K', 18),        
    ('L', 18),        
    ('M', 18),          
]

class efaktur_product_csv_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(efaktur_product_csv_parser, self).__init__(cr, uid, name, context=context)
        self.env = Environment(cr, uid, context)
        product_obj = self.env['product.template']
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
            'get_product': self._get_product,
        })
        
    def _get_product(self, product):
        return product.upper()

class efaktur_product_product_csv(report_csv):
    column_sizes = [x[1] for x in _column_sizes]
    
    def generate_csv_report(self, _p, _xs, data, objects, wb):
        report_name = _("Barang dan Jasa")
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        
        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        c_row_cell_style = xlwt.easyxf(num_format_str='###0')
        # Column headers 1
        c_specs = [
                ('OB',  1, 0, 'text', 'OB'),
                ('KODE_OBJEK',  1, 0, 'text', 'KODE_OBJEK'),
                ('NAMA',  1, 0, 'text', 'NAMA'),
                ('HARGA_SATUAN',  1, 0, 'text', 'HARGA_SATUAN'),
                ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)  
        for prod in objects:
            c_specs = [
                    ('OB',  1, 0, 'text', 'OB'),
                    ('kd_objek',  1, 0, 'text', prod.default_code and prod.default_code.upper() or ''),
                    ('nama',  1, 0, 'text', prod.name and prod.name.upper() or ''),
                    ('harga_satuan',  1, 0, 'number', prod.list_price or 0),
                ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)
                
efaktur_product_product_csv('report.efaktur.product.product.csv',
              'product.template',
              parser=efaktur_product_csv_parser)
