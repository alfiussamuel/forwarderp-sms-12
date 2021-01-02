from odoo import api, fields, models, _
import time
import csv
from odoo.modules import get_modules, get_module_path
from odoo.exceptions import UserError
import copy
import logging
from io import StringIO
import base64

_logger = logging.getLogger(__name__)

class efaktur_pk_wizard(models.TransientModel):
    _name = 'vit.efaktur_pk'

    export_file = fields.Binary(string="Export File",  )
    export_filename = fields.Char(string="Export File",  )

    @api.multi
    def confirm_button(self):
        """
        export pk yang is_efaktur_exported = False
        update setelah export
        :return: 
        """
        cr = self.env.cr

        headers = [
            'FK',
            'KD_JENIS_TRANSAKSI',
            'FG_PENGGANTI',
            'NOMOR_FAKTUR',
            'MASA_PAJAK',
            'TAHUN_PAJAK',
            'TANGGAL_FAKTUR',
            'NPWP',
            'NAMA',
            'ALAMAT_LENGKAP',
            'JUMLAH_DPP',
            'JUMLAH_PPN',
            'JUMLAH_PPNBM',
            'ID_KETERANGAN_TAMBAHAN',
            'FG_UANG_MUKA',
            'UANG_MUKA_DPP',
            'UANG_MUKA_PPN',
            'UANG_MUKA_PPNBM',
            'REFERENSI'
        ]


        mpath = get_module_path('vit_efaktur')

        # csvfile = open(mpath + '/static/fpk.csv', 'wb')
        csvfile = StringIO()
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow([h.upper() for h in headers])

        inv_obj = self.env['account.invoice']
        invoices = inv_obj.search([('is_efaktur_exported','=',False),
                                   ('state','=','open'),
                                   ('efaktur_id','!=', False),
                                   ('type','=','out_invoice')])

        company = self.env.user.company_id.partner_id

        i=0
        self.baris2(headers, csvwriter)
        self.baris3(headers, csvwriter)

        combined_invoices = self.gabung_by_efaktur(invoices)

        for invoice in combined_invoices:
            self.baris4(headers, csvwriter, invoice)
            self.baris5(headers, csvwriter, company )

            for line in invoice['invoice_line_ids']:
                self.baris6(headers, csvwriter, line)

            i+=1

        for id in invoices.mapped('id'):
            invoice = inv_obj.browse(id)
            invoice.is_efaktur_exported=True
            invoice.date_efaktur_exported=time.strftime("%Y-%m-%d %H:%M:%S")

        cr.commit()
        # csvfile.close()
        # _logger.info(csvfile.getvalue().encode() )
        self.export_file = base64.b64encode(csvfile.getvalue().encode())
        self.export_filename = 'Export-%s.csv' % time.strftime("%Y%m%d_%H%M%S")
        return {
            'name': "Export E-Faktur Complete, total %s records" % i,
            'type': 'ir.actions.act_window',
            'res_model': 'vit.efaktur_pk',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        # raise UserError("Export %s record(s) Done!" % i)

    def gabung_by_efaktur(self, invoices):
        old_efaktur = None
        inv_obj = self.env['account.invoice']
        i=0
        combines=[]
        # list of tuples of invoices to be combined by efaktur
        # [(inv1,inv2,inv5),(inv3,inv4)]


        final_invoices = []
        # list of final combined invoices, totallized
        # [inv125, inv34]

        for inv in sorted(invoices, key=lambda inv: inv.efaktur_id):
            if old_efaktur == inv.efaktur_id:
                combines[i-1].append(inv_obj.search_read([('id','=',inv.id)])[0])
            else:
                combines.append([inv_obj.search_read([('id','=',inv.id)])[0]])
                i += 1
            old_efaktur = inv.efaktur_id

        # comb = invoices per efaktur yg sama
        for comb in combines:
            i=0
            for inv in comb:
                if i == 0:
                    i+=1
                    continue

                line_ids = inv['invoice_line_ids']
                for id in line_ids:
                    comb[0]['invoice_line_ids'].append(id)

                comb[0]['amount_untaxed'] += inv['amount_untaxed']
                comb[0]['amount_tax'] += inv['amount_tax']
                comb[0]['amount_total'] += inv['amount_total']
                comb[0]['number'] += "," + inv['number']
                i+=1

            comb[0]['invoice_line_ids'] = self.merge_lines(comb[0]['invoice_line_ids'])

            final_invoices.append(comb[0])

        return final_invoices

    def merge_lines(self, lines):
        old_line = None
        final_lines = []

        i=0
        for line in self.env['account.invoice.line'].search_read([('id','in',lines)]):
            if old_line and (old_line['product_id'] == line['product_id'] and old_line['price_unit'] == line['price_unit']):
                old_line['price_unit'] += line['price_unit']
                old_line['quantity'] += line['quantity']
                final_lines.append(old_line)
            else:
                final_lines.append(line)

            old_line = line
            i+=1


        return final_lines



    def baris2(self, headers, csvwriter):
        data = {
            'FK': 'LT',
            'KD_JENIS_TRANSAKSI': 'NPWP',
            'FG_PENGGANTI': 'NAMA',
            'NOMOR_FAKTUR': 'JALAN',
            'MASA_PAJAK': 'BLOK',
            'TAHUN_PAJAK': 'NOMOR',
            'TANGGAL_FAKTUR': 'RT',
            'NPWP': 'RW',
            'NAMA': 'KECAMATAN',
            'ALAMAT_LENGKAP': 'KELURAHAN',
            'JUMLAH_DPP': 'KABUPATEN',
            'JUMLAH_PPN': 'PROPINSI',
            'JUMLAH_PPNBM': 'KODE_POS',
            'ID_KETERANGAN_TAMBAHAN': 'NOMOR_TELEPON',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])

    def baris3(self, headers, csvwriter):
        data = {
            'FK': 'OF',
            'KD_JENIS_TRANSAKSI': 'KODE_OBJEK',
            'FG_PENGGANTI': 'NAMA',
            'NOMOR_FAKTUR': 'HARGA_SATUAN',
            'MASA_PAJAK': 'JUMLAH_BARANG',
            'TAHUN_PAJAK': 'HARGA_TOTAL',
            'TANGGAL_FAKTUR': 'DISKON',
            'NPWP': 'DPP',
            'NAMA': 'PPN',
            'ALAMAT_LENGKAP': 'TARIF_PPNBM',
            'JUMLAH_DPP': 'PPNBM',
            'JUMLAH_PPN': '',
            'JUMLAH_PPNBM': '',
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])


    def baris4(self, headers, csvwriter, inv):
        partner_id = self.env['res.partner'].browse(inv['partner_id'][0])
        if not partner_id.npwp:
            raise UserError("Harap masukkan NPWP Customer %s" % inv['partner_id'][1])

        if not inv['efaktur_id'][0]:
            raise UserError("Harap masukkan Nomor Seri Faktur Pajak Keluaran Invoice Nomor %s" % inv['number'])

        # yyyy-mm-dd to dd/mm/yyyy

        # d  = inv['date_invoice'].split("-")
        # date_invoice = "%s/%s/%s" %(d[2],d[1],d[0])
        date_invoice = inv['date_invoice'].strftime("%d/%m/%Y")
        npwp = partner_id.npwp.replace(".","").replace("-","")
        faktur = inv['efaktur_id'][1].replace(".","").replace("-","")

        print ("Tax ", inv['amount_tax'])
        print ("DPP ", inv['amount_untaxed'])
        print ("Tax Round ", round(inv['amount_tax']))
        print ("DPP Round ", round(inv['amount_untaxed']))

        if inv['is_cancel']:
            data = {
                'FK': 'FK',
                'KD_JENIS_TRANSAKSI': '01',
                'FG_PENGGANTI': '1',
                'NOMOR_FAKTUR': faktur,
                'MASA_PAJAK': inv['masa_pajak'] or '',
                'TAHUN_PAJAK': inv['tahun_pajak'] or '',
                'TANGGAL_FAKTUR': date_invoice,
                'NPWP': npwp,
                'NAMA': partner_id.name.encode('utf8') or '',
                'ALAMAT_LENGKAP': partner_id.alamat_lengkap.encode('utf8') or '',
                'JUMLAH_DPP': round(inv['amount_untaxed']) or 0,
                'JUMLAH_PPN': round(inv['amount_tax']) or 0,
                'JUMLAH_PPNBM': 0,
                'ID_KETERANGAN_TAMBAHAN': '',
                'FG_UANG_MUKA': 0,
                'UANG_MUKA_DPP': 0,
                'UANG_MUKA_PPN': 0,
                'UANG_MUKA_PPNBM': 0,
                'REFERENSI': inv['number'] or ''
            }

        elif not inv['is_cancel']:
            data = {
                'FK': 'FK',
                'KD_JENIS_TRANSAKSI': '01',
                'FG_PENGGANTI': '0',
                'NOMOR_FAKTUR': faktur,
                'MASA_PAJAK': inv['masa_pajak'] or '',
                'TAHUN_PAJAK': inv['tahun_pajak'] or '',
                'TANGGAL_FAKTUR': date_invoice,
                'NPWP': npwp,
                'NAMA': partner_id.name.encode('utf8') or '',
                'ALAMAT_LENGKAP': partner_id.alamat_lengkap.encode('utf8') or '',
                'JUMLAH_DPP': round(inv['amount_untaxed']) or 0,
                'JUMLAH_PPN': round(inv['amount_tax']) or 0,
                'JUMLAH_PPNBM': 0,
                'ID_KETERANGAN_TAMBAHAN': '',
                'FG_UANG_MUKA': 0,
                'UANG_MUKA_DPP': 0,
                'UANG_MUKA_PPN': 0,
                'UANG_MUKA_PPNBM': 0,
                'REFERENSI': inv['number'] or ''
            }

        _logger.info(data)
        csvwriter.writerow([data[v] for v in headers])

    def baris5(self, headers, csvwriter, company):
        data = {
            'FK': 'FAPR',
            'KD_JENIS_TRANSAKSI': company.name,
            'FG_PENGGANTI': company.alamat_lengkap,
            'NOMOR_FAKTUR': '',
            'MASA_PAJAK': '',
            'TAHUN_PAJAK': '',
            'TANGGAL_FAKTUR': '',
            'NPWP': '',
            'NAMA': '',
            'ALAMAT_LENGKAP': '',
            'JUMLAH_DPP': '',
            'JUMLAH_PPN': '',
            'JUMLAH_PPNBM': '',
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])

    def baris6(self, headers, csvwriter, line):
        # harga_total = line['price_unit'] * line['quantity']
        harga_total = round(line['price_subtotal'])
        dpp = harga_total
        ppn = round(dpp * 0.1) #TODO ambil dari Tax many2many
        product_id = self.env['product.product'].browse(line['product_id'][0])

        data = {
            'FK': 'OF',
            'KD_JENIS_TRANSAKSI': product_id.default_code or '',
            'FG_PENGGANTI': product_id.name or '',
            'NOMOR_FAKTUR': line['price_unit'],
            'MASA_PAJAK': line['quantity'] ,
            'TAHUN_PAJAK': harga_total,
            'TANGGAL_FAKTUR': line['discount'] or 0,
            'NPWP': dpp,
            'NAMA': ppn,
            'ALAMAT_LENGKAP': '0',
            'JUMLAH_DPP': '0',
            'JUMLAH_PPN': '',
            'JUMLAH_PPNBM': '',
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': ''
        }
        csvwriter.writerow([data[v] for v in headers])

