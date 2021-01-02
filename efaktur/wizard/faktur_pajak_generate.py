# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

class generate_faktur_pajak(models.TransientModel):
    _name = 'generate.faktur.pajak'    
    _description = 'Generate Faktur Pajak'
    
    nomor_faktur_awal = fields.Char('Nomor Faktur Awal', size=20, default='Nomor Faktur Awal:')
    nomor_faktur_akhir = fields.Char('Nomor Faktur Akhir', size=20, default='Nomor Faktur Akhir:')
    strip= fields.Char('Strip', size=3, default='-')
    dot = fields.Char('Dot', size=3, default='.')
    strip2 = fields.Char('Strip', size=3, default='-')
    dot2 = fields.Char('Dot', size=3, default='.')
    nomor_perusahaan = fields.Char('Nomor Perusahaan', size=3, required=True)
    nomor_awal = fields.Char('Nomor Faktur Awal', size=8, required=True)
    nomor_akhir = fields.Char('Nomor Faktur Akhir', size=8, required=True)
    tahun = fields.Char('Tahun Penerbit', size=2, required=True)
    type = fields.Selection([('in','Faktur Pajak Masukan'),('out','Faktur Pajak Keluaran')],'Type')
    
    @api.multi
    def generate_faktur(self):
        context = dict(self._context or {})
        for record in self:
            awal = int(record.nomor_awal)
            akhir = int(record.nomor_akhir)
            while (awal <= akhir):
                vals = {
                    'nomor_perusahaan': record.nomor_perusahaan,
                    'tahun_penerbit': record.tahun,
                    'nomor_urut': '%08d' % awal,
                    'status': '0',
                    'type': record.type,
                }
                self.env['nomor.faktur.pajak'].create(vals)
                awal += 1
        return {'type': 'ir.actions.act_window_close'}