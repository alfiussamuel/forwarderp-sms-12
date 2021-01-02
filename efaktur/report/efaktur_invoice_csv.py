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


class efaktur_invoice_csv_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(efaktur_invoice_csv_parser, self).__init__(cr, uid, name, context=context)
        self.env = Environment(cr, uid, context)
        move_obj = self.env['account.invoice']
        self.context = context
        self.localcontext.update({
            'datetime': datetime,
            'get_name_npwp': self._get_name_npwp,
            'get_street_npwp': self._get_street_npwp,
            'amount_currency': self._amount_currency,
            'amount_currency_line': self._amount_currency_line,
        })
        
    def _get_name_npwp(self, partner_id, type):
        return partner_id.name.upper()
#         if partner_id:
#             part_ids = self.pool.get('res.partner').search(self.cr, self.uid, [('parent_id','=',partner_id.id), ('type','=',type)])        
#             if part_ids:
#                 partner = self.pool.get('res.partner').browse(self.cr, self.uid, part_ids[0])
#                 return partner.name.upper()
#             else:
#                 return partner_id.name.upper()
        
    def _get_street_npwp(self, partner_id, type):
        address = self.env['res.partner'].browse(partner_id.id)
        partner_address = ''
        if address.child_ids:
            addr_npwp = False
            for addr_npwp in address.child_ids:
                if addr_npwp.type == 'npwp':
                    address = addr_npwp
            if addr_npwp:
                partner_address += address.street and address.street +'. ' or ''
                partner_address += address.street2 and address.street2 +'. ' or ''
                partner_address += address.blok and 'Blok '+ address.blok or ''
                partner_address += address.nomor and 'No. '+ address.nomor or ''
                partner_address += address.rt and address.rw and 'RT/RW: %s/%s' % (address.rt,address.rw) or ''
                partner_address += address.kelurahan_id and ', Kel. ' + address.kelurahan_id.name or ''
                partner_address += address.kecamatan_id_new and ', Kec. ' + address.kecamatan_id.name or ''
                partner_address += address.kabupaten_id and ', Kota/Kab. ' + address.kabupaten_id.name + ', ' or ''
                partner_address += address.city and address.city +'. ' or ''
                partner_address += address.zip and address.zip +'. ' or ''
                partner_address += address.country_id.name and address.country_id.name or ''
        if not partner_address:
            partner_address += address.street and address.street +'. ' or ''
            partner_address += address.street2 and address.street2 +'. ' or ''
            partner_address += address.blok and 'Blok '+ address.blok or ''
            partner_address += address.nomor and 'No. '+ address.nomor or ''
            partner_address += address.rt and address.rw and 'RT/RW: %s/%s' % (address.rt,address.rw) or ''
            partner_address += address.kelurahan_id and ', Kel. ' + address.kelurahan_id.name or ''
            partner_address += address.kecamatan_id_new and ', Kec. ' + address.kecamatan_id_new.name or ''
            partner_address += address.kabupaten_id and ', Kota/Kab. ' + address.kabupaten_id.name + ', ' or ''
            partner_address += address.city and address.city +'. ' or ''
            partner_address += address.zip and address.zip +'. ' or ''
            partner_address += address.country_id.name and address.country_id.name or ''
        return partner_address.upper()

    def _amount_currency(self, amount, inv):
        cur_obj = self.env['res.currency']
        amount = cur_obj.with_context({'date': inv.date_invoice or time.strftime('%Y-%m-%d')}).compute(amount, inv.company_id.currency_id.id, round=False)
        return amount
    
    def _amount_currency_line(self, amount, inv):
        cur_obj = self.env['res.currency']
        amount = cur_obj.with_context({'date': inv.invoice_id.date_invoice or time.strftime('%Y-%m-%d')}).compute(amount, inv.invoice_id.company_id.currency_id.id, round=False)
        return amount

class efaktur_account_invoice_csv(report_csv):
    column_sizes = [x[1] for x in _column_sizes]
    
    def generate_csv_report(self, _p, _xs, data, objects, wb):
        #print "==generate_csv_report==",objects.type
        if objects[0].type in ('out_invoice','out_refund'):
            report_name = _("Faktur Keluaran")
        else:
            report_name = _("Faktur Masukan")
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
                ('FK',  1, 0, 'text', 'FK'),
                ('KD_JENIS_TRANSAKSI',  1, 0, 'text', 'KD_JENIS_TRANSAKSI'),
                ('FG_PENGGANTI',  1, 0, 'text', 'FG_PENGGANTI'),
                ('NOMOR_FAKTUR',  1, 0, 'text', 'NOMOR_FAKTUR'),
                ('MASA_PAJAK',  1, 0, 'text', 'MASA_PAJAK'),
                ('TAHUN_PAJAK',  1, 0, 'text', 'TAHUN_PAJAK'),
                ('TANGGAL_FAKTUR',  1, 0, 'text', 'TANGGAL_FAKTUR'),
                ('NPWP',  1, 0, 'text', 'NPWP'),
                ('NAMA',  1, 0, 'text', 'NAMA'),
                ('ALAMAT_LENGKAP',  1, 0, 'text', 'ALAMAT_LENGKAP'),
                ('JUMLAH_DPP',  1, 0, 'text', 'JUMLAH_DPP'),
                ('JUMLAH_PPN',  1, 0, 'text', 'JUMLAH_PPN'),
                ('JUMLAH_PPNBM',  1, 0, 'text', 'JUMLAH_PPNBM'),
                ('ID_KETERANGAN_TAMBAHAN',  1, 0, 'text', 'ID_KETERANGAN_TAMBAHAN'),
                ('FG_UANG_MUKA',  1, 0, 'text', 'FG_UANG_MUKA'),
                ('UANG_MUKA_DPP',  1, 0, 'text', 'UANG_MUKA_DPP'),
                ('UANG_MUKA_PPN',  1, 0, 'text', 'UANG_MUKA_PPN'),
                ('UANG_MUKA_PPNBM',  1, 0, 'text', 'UANG_MUKA_PPNBM'),
                ('REFERENSI',  1, 0, 'text', 'REFERENSI'),
                ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)
        # Column headers 2
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
        # Column headers 3
        c_specs = [
                ('OF',  1, 0, 'text', 'OF'),
                ('KODE_OBJEK',  1, 0, 'text', 'KODE_OBJEK'),
                ('NAMA',  1, 0, 'text', 'NAMA'),
                ('HARGA_SATUAN',  1, 0, 'text', 'HARGA_SATUAN'),
                ('JUMLAH_BARANG',  1, 0, 'text', 'JUMLAH_BARANG'),
                ('HARGA_TOTAL',  1, 0, 'text', 'HARGA_TOTAL'),
                ('DISKON',  1, 0, 'text', 'DISKON'),
                ('DPP',  1, 0, 'text', 'DPP'),
                ('PPN',  1, 0, 'text', 'PPN'),
                ('TARIF_PPNBM',  1, 0, 'text', 'TARIF_PPNBM'),
                ('PPNBM',  1, 0, 'text', 'PPNBM'),
                ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)  
        for inv in objects:
            print ("CANCELLL ", inv.is_cancel)
            if not inv.is_cancel:
                print ("AAAAAAAAAAAAA ", inv.is_cancel)
                c_specs = [
                        ('FK',  1, 0, 'text', 'FK'),
                        ('kd_jenis_transaksi',  1, 0, 'text', '01'),#x['faktur_pajak_no'] and x['faktur_pajak_no'][:2] or '01'
                        ('jenis_fp',  1, 0, 'text', '0'),#0=faktur pajak, 1=faktur pajak pengganti
                        ('nomor_faktur',  1, 0, 'text', inv.nomor_faktur_id and inv.nomor_faktur_id.number or ''),#010.000-15.10897639
                        ('masa_pajak',  1, 0, 'number', int(time.strftime('%m', time.strptime(inv.date_invoice,'%Y-%m-%d')))),
                        ('tahun_pajak',  1, 0, 'number', time.strftime('%Y', time.strptime(inv.date_invoice,'%Y-%m-%d'))),
                        ('tanggal_faktur',  1, 0, 'text', time.strftime('%d/%m/%Y', time.strptime(inv.date_invoice,'%Y-%m-%d'))),
                        ('npwp',  1, 0, 'text', inv.npwp_efaktur or '000000000000000'),#02.505.335.6-016.000
                        ('nama',  1, 0, 'text', _p.get_name_npwp(inv.partner_id, 'npwp') or ''),
                        ('alamat_lengkap',  1, 0, 'text', _p.get_street_npwp(inv.partner_id, 'npwp') or ''),
                        ('jumlah_dpp',  1, 0, 'number', int(inv.amount_untaxed)),
                        ('jumlah_ppn',  1, 0, 'number', int(inv.amount_tax)),
                        ('jumlah_ppnbm',  1, 0, 'number', 0),
                        ('id_keterangan_tambahan',  1, 0, 'text', ''),
                        ('fg_uang_muka',  1, 0, 'number', 0),
                        ('uang_muka_dpp',  1, 0, 'number', 0),
                        ('uang_muka_ppn',  1, 0, 'number', 0),
                        ('uang_muka_ppnbm',  1, 0, 'number', 0),
                        ('referensi',  1, 0, 'text', inv.partner_id and inv.partner_id.ktp or inv.origin or ''),
                    ]
            elif inv.is_cancel:
                print ("BBBBBBBBBBBBB ", inv.is_cancel)
                c_specs = [
                        ('FK',  1, 0, 'text', 'FK'),
                        ('kd_jenis_transaksi',  1, 0, 'text', '01'),#x['faktur_pajak_no'] and x['faktur_pajak_no'][:2] or '01'
                        ('jenis_fp',  1, 0, 'text', '1'),#0=faktur pajak, 1=faktur pajak pengganti
                        ('nomor_faktur',  1, 0, 'text', inv.nomor_faktur_id and inv.nomor_faktur_id.number or ''),#010.000-15.10897639
                        ('masa_pajak',  1, 0, 'number', int(time.strftime('%m', time.strptime(inv.date_invoice,'%Y-%m-%d')))),
                        ('tahun_pajak',  1, 0, 'number', time.strftime('%Y', time.strptime(inv.date_invoice,'%Y-%m-%d'))),
                        ('tanggal_faktur',  1, 0, 'text', time.strftime('%d/%m/%Y', time.strptime(inv.date_invoice,'%Y-%m-%d'))),
                        ('npwp',  1, 0, 'text', inv.npwp_efaktur or '000000000000000'),#02.505.335.6-016.000
                        ('nama',  1, 0, 'text', _p.get_name_npwp(inv.partner_id, 'npwp') or ''),
                        ('alamat_lengkap',  1, 0, 'text', _p.get_street_npwp(inv.partner_id, 'npwp') or ''),
                        ('jumlah_dpp',  1, 0, 'number', int(inv.amount_untaxed)),
                        ('jumlah_ppn',  1, 0, 'number', int(inv.amount_tax)),
                        ('jumlah_ppnbm',  1, 0, 'number', 0),
                        ('id_keterangan_tambahan',  1, 0, 'text', ''),
                        ('fg_uang_muka',  1, 0, 'number', 0),
                        ('uang_muka_dpp',  1, 0, 'number', 0),
                        ('uang_muka_ppn',  1, 0, 'number', 0),
                        ('uang_muka_ppnbm',  1, 0, 'number', 0),
                        ('referensi',  1, 0, 'text', inv.partner_id and inv.partner_id.ktp or inv.origin or ''),
                    ]

            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)
            #Faktur Company
            #===================================================================
            # c_specs = [
            #     ('FAPR',  1, 0, 'text', 'FAPR'),
            #     ('company_name',  1, 0, 'text', inv.partner_id.name),
            #     ('company_address',  1, 0, 'text', _p.get_street_npwp(inv.partner_id.id, 'npwp')),
            #     ]
            # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            # row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)
            #===================================================================
            #print "===line.invoice_line_tax_ids==",sum(line.amount for line in self.tax_line_ids)
            for line in inv.invoice_line_ids:
                tax_amt_type = sum(tax.amount_type == 'percent' and tax.amount/100.0 or tax.amount for tax in line.invoice_line_tax_ids)
                c_specs = [
                    ('OF',  1, 0, 'text', 'OF'),
                    ('code_product',  1, 0, 'text', line.product_id.default_code or ''),
                    ('name_product',  1, 0, 'text', line.product_id.name or ''),
                    ('price_unit',  1, 0, 'number', int(_p.amount_currency_line(line.price_subtotal/line.quantity, line))),
                    ('quantity',  1, 0, 'number', line.quantity or 1),
                    ('price_unit_quantity',  1, 0, 'number', int(_p.amount_currency_line(line.price_subtotal, line))),
                    ('discount',  1, 0, 'number', line.discount or 0),
                    ('dpp_product',  1, 0, 'number', int(_p.amount_currency_line(line.price_subtotal, line))),
                    ('ppn_product',  1, 0, 'number', line.invoice_line_tax_ids and int(_p.amount_currency_line(round(tax_amt_type*line.price_subtotal,2),line))),
                    ('tarif_ppnbm',  1, 0, 'number', 0),
                    ('ppnbm',  1, 0, 'number', 0),
                ]
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_row_cell_style)
                
efaktur_account_invoice_csv('report.efaktur.account.invoice.csv',
              'account.invoice',
              parser=efaktur_invoice_csv_parser)
