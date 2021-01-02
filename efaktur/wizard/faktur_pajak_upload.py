from odoo import fields, models, exceptions, api, _
import os, os.path
import base64
import csv
import cStringIO
import logging

_logger = logging.getLogger(__name__)

class UploadEFaktur(models.TransientModel):
    _name = 'upload.efaktur'
    _description = 'Upload E-Faktur'

    name = fields.Char('Path', help='Path of your directory with all attachment E-Faktur')

    @api.model
    def default_get(self, fields):
        rec = super(UploadEFaktur, self).default_get(fields)
        if 'name' in fields:
            location_storage = self.env['ir.attachment']._storage()
            rec['name'] = location_storage#'/Users/henipurwanti/Desktop/Attachment'
        return rec
    
    @api.one
    def action_import(self):
        """Load Inventory data from the CSV file.
            value = { 
                'mimetype': 'application/vnd.ms-excel', 
                'name': u'Balance Sheet Print.xls', 
                'res_model': u'account.invoice', 
                'datas_fname': u'Balance Sheet Print.xls', 
                'res_id': 1,
                'datas': binary,
            }
        """
        ctx = self._context
        attachment_obj = self.env['ir.attachment']
        invoice_obj = self.env['account.invoice']
        storage = attachment_obj._storage()
        filestore = attachment_obj._filestore()
        file_gc = attachment_obj._file_gc()
        indir = self.name#+'/E-Faktur'
        files_in_dir = os.listdir(indir)
        in_dir = []
        for x in files_in_dir:
            r = open(indir+"/"+x,'rb').read().encode('base64')
            _logger.info("_read_file reading %s", x)
            if len(x) == 67:
                #_logger.info("_read_file valid file efaktur %s", x)
                faktur_pajak = x.split("-")
                #SEARCH INVOICE YG SUDAH TERFALIDASI DAN ADA FAKTUR PAJAK
                invoice_ids = invoice_obj.search([('nomor_faktur_id','!=',None),('move_id','!=',None),('nomor_faktur_id.number','ilike',faktur_pajak[1][8:])])
                #CARI APAKAH SUDAH TERATTACHMENT DI SISTEM
                attachment_ids = attachment_obj.search([('datas','!=',r),('res_id','in',invoice_ids.ids),('res_model','=','account.invoice'),('name','=',faktur_pajak[1])])
                if not attachment_ids and invoice_ids:
                    for invoice in invoice_ids:
                        values = {
                            'res_model': 'account.invoice',
                            'company_id': 1,
                            'res_name': invoice.number,#NOMOR INVOICE
                            'datas_fname': x,#NAMA FILE
                            'type': 'binary',
                            'res_id': invoice.id,
                            'name': x,#faktur_pajak[1],
                            'mimetype': 'application/pdf',
                            'store_fname': 'E-Faktur/'+x,
                            'datas': r,
                        }
                        attachment_obj.create(values)
                        _logger.info("_uploaded_file %s", x)
