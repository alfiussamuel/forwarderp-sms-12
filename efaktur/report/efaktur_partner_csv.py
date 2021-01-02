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

class efaktur_partner_csv_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(efaktur_partner_csv_parser, self).__init__(cr, uid, name, context=context)
        self.env = Environment(cr, uid, context)
        partner_obj = self.env['res.partner']
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
            'get_street_npwp': self._get_street_npwp,
        })
        
    def _get_street_npwp(self, partner_id, type):
        address = self.env['res.partner'].browse(partner_id.id)
        partner_address = ''       
        if not address.is_npwp and address.child_ids:
            add_npwp = False
            for add_npwp in address.child_ids:
                if add_npwp.type == 'npwp':
                    address = add_npwp
            if add_npwp:
                if type == 'nama':
                    partner_address = address.name or ''
                elif type == 'npwp' and address.npwp:
                    partner_address = address.npwp
                    partner_address = partner_address.replace('.','')
                    partner_address = partner_address.replace('-','')
                elif type == 'jalan':
                    partner_address = address.street and address.street2 and address.street + ' ' + address.street2 or address.street or ''
                elif type == 'blok':
                    partner_address = address.blok or ''
                elif type == 'nomor':
                    partner_address = address.nomor or ''
                elif type == 'rt':
                    partner_address = address.rt or ''
                elif type == 'rw':
                    partner_address = address.rw or ''
                elif type == 'kel':
                    partner_address = address.kelurahan_id and address.kelurahan_id.name or ''
                elif type == 'kec':
                    partner_address = address.kecamatan_id and address.kecamatan_id.name or ''
                elif type == 'kab':
                    partner_address = address.kabupaten_id and address.kabupaten_id.name or ''
                elif type == 'prop':
                    partner_address = address.state_id and address.state_id.name or ''
                elif type == 'kode_pos':
                    partner_address = address.zip or ''
                elif type == 'no_telp':
                    partner_address = address.phone or ''
        if not partner_address and address.is_npwp:
            if type == 'nama':
                partner_address = address.name or ''
            elif type == 'npwp':
                partner_address = address.npwp
                partner_address = partner_address.replace('.','')
                partner_address = partner_address.replace('-','')
            elif type == 'jalan':
                partner_address = address.street and address.street2 and address.street + ' ' + address.street2 or address.street or ''
            elif type == 'blok':
                partner_address = address.blok or ''
            elif type == 'nomor':
                partner_address = address.nomor or ''
            elif type == 'rt':
                partner_address = address.rt or ''
            elif type == 'rw':
                partner_address = address.rw or ''
            elif type == 'kel':
                partner_address = address.kelurahan_id and address.kelurahan_id.name or ''
            elif type == 'kec':
                partner_address = address.kecamatan_id and address.kecamatan_id.name or ''
            elif type == 'kab':
                partner_address = address.kabupaten_id and address.kabupaten_id.name or ''
            elif type == 'prop':
                partner_address = address.state_id and address.state_id.name or ''
            elif type == 'kode_pos':
                partner_address = address.zip or ''
            elif type == 'no_telp':
                partner_address = address.phone or ''
        return partner_address.upper()
    
class efaktur_res_partner_csv(report_csv):
    column_sizes = [x[1] for x in _column_sizes]
    
    def generate_csv_report(self, _p, _xs, data, objects, wb):
        #print "==generate_csv_report==",objects.type
        report_name = _("Lawan Transaksi")
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
                ('LT',  1, 0, 'text', 'LT'),
                ('NPWP',  1, 0, 'text', 'NPWP'),
                ('NAMA',  1, 0, 'text', 'NAMA'),
                ('JALAN',  1, 0, 'text', 'JALAN'),
                ('BLOK',  1, 0, 'text', 'BLOK'),
                ('NOMOR',  1, 0, 'text', 'NOMOR'),
                ('RT',  1, 0, 'text', 'RT'),
                ('RW',  1, 0, 'text', 'RW'),
                ('KECAMATAN',  1, 0, 'text', 'KECAMATAN'),
                ('KELURAHAN',  1, 0, 'text', 'KELURAHAN'),
                ('KABUPATEN',  1, 0, 'text', 'KABUPATEN'),
                ('PROPINSI',  1, 0, 'text', 'PROPINSI'),
                ('KODE_POS',  1, 0, 'text', 'KODE_POS'),
                ('NOMOR_TELEPON',  1, 0, 'text', 'NOMOR_TELEPON'),
                ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)        
        for part in objects:
            c_specs = [
                    ('LT',  1, 0, 'text', 'LT'),
                    ('npwp',  1, 0, 'text', _p.get_street_npwp(part, 'npwp') or '000000000000000'),#02.505.335.6-016.000
                    ('nama',  1, 0, 'text', _p.get_street_npwp(part, 'nama') or ''),
                    ('jalan',  1, 0, 'text', _p.get_street_npwp(part, 'jalan') or ''),
                    ('blok',  1, 0, 'text', _p.get_street_npwp(part, 'blok') or ''),
                    ('nomor',  1, 0, 'text', _p.get_street_npwp(part, 'nomor') or ''),
                    ('rt',  1, 0, 'text', _p.get_street_npwp(part, 'rt') or ''),
                    ('rw',  1, 0, 'text', _p.get_street_npwp(part, 'rw') or ''),
                    ('kec',  1, 0, 'text', _p.get_street_npwp(part, 'kec') or ''),
                    ('kel',  1, 0, 'text', _p.get_street_npwp(part, 'kel') or ''),
                    ('kab',  1, 0, 'text', _p.get_street_npwp(part, 'kab') or ''),
                    ('prop',  1, 0, 'text', _p.get_street_npwp(part, 'prop') or ''),
                    ('kode_pos',  1, 0, 'text', _p.get_street_npwp(part, 'kode_pos') or ''),
                    ('no_telp',  1, 0, 'text', _p.get_street_npwp(part, 'no_telp') or ''),
                    
                ]
            if _p.get_street_npwp(part, 'npwp'):
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)
            
efaktur_res_partner_csv('report.efaktur.res.partner.csv',
              'res.partner',
              parser=efaktur_partner_csv_parser)
