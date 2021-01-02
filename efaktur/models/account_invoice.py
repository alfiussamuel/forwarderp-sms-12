# -*- coding: utf-8 -*-
##############################################################################
#
#    Alphasoft Solusi Integrasi, PT
#    Copyright (C) 2014 Alphasoft (<http://www.alphasoft.co.id>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit    = "account.invoice"
    
    @api.one
    @api.depends('partner_id.code_transaction', 'nomor_faktur_id', 'nomor_faktur_id.name')
    def _nomor_faktur_partner(self):
        for invoice in self:
            invoice.nomor_faktur_partner = "%s.%s" % (invoice.partner_id.code_transaction,invoice.nomor_faktur_id and invoice.nomor_faktur_id.name)
            invoice.code_transaction = invoice.partner_id.code_transaction
            invoice.npwp_no = invoice.partner_id.npwp
            if invoice.npwp_no:
                npwp = invoice.npwp_no
                npwp = npwp.replace('.','')
                npwp = npwp.replace('-','')
                invoice.npwp_efaktur = npwp

    nomor_faktur_id = fields.Many2one('nomor.faktur.pajak', string='Nomor Faktur Pajak', change_default=True,
        required=False, copy=False,readonly=True, states={'draft': [('readonly', False)]})
    code_transaction = fields.Selection([
            ('01','010.'),('02','020.'),('03','030.'),('08','080.')
        ], string='Kode Faktur', compute='_nomor_faktur_partner', store=True, readonly=True,copy=False)
    nomor_faktur_partner = fields.Char(string='Nomor Faktur', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_nomor_faktur_partner')
    npwp_no = fields.Char(string='NPWP', compute='_nomor_faktur_partner', store=True, readonly=True)
    npwp_efaktur = fields.Char(string='NPWP for eFaktur', compute='_nomor_faktur_partner', store=False, readonly=True)
    vat_supplier = fields.Char(string='Faktur Pajak No', size=63, readonly=True, states={'draft': [('readonly', False)]}, index=True,
        help="Nomor Bukti Potong", copy=False)
    
    @api.multi
    def onchange_partner_npwp(self, npwp=False):
        return {'value': {}}





    
    # @api.one
    # def faktur_pajak_create(self):
    #     # == coba ah testing ==
    #     obj_no_faktur = self.env['nomor.faktur.pajak'].browse(self.nomor_faktur_id.id)
    #     if self.nomor_faktur_id and self.type in ('out_invoice','out_direct'):
    #         self.nomor_faktur_id.write({
    #             'invoice_id': self.id,
    #             'state': '1'         
    #             })  
    #         print '======================'
    #         print 'AAAAAAA',self.nomor_faktur_id.name
    #         print '======================'
    #         self.write({'no_faktur_customer' : str(self.nomor_faktur_id.name)})
    #     elif self.nomor_faktur_id and self.type in ('in_invoice','in_direct'):                
    #         if self.nomor_faktur_id[3] == "." and self.nomor_faktur_id[6] == '.':
    #             if len(str(self.nomor_faktur_id).split('.')[2]) > 8:
    #                 raise osv.except_osv(_('Wrong Faktur Number'), _('Nomor Urut max 8 Digit'))                
    #             vals = {
    #                 'nomor_perusahaan'  : str(self.vat_supplier).split('.')[0],
    #                 'tahun_penerbit'    : str(self.vat_supplier).split('.')[1], 
    #                 'nomor_urut'        : str(self.vat_supplier).split('.')[2],
    #                 'invoice_id'        : self.id,
    #                 'type'              : 'in',
    #                 'state'             : '1'
    #             }
    #         else:
    #             raise osv.except_osv(_('Faktur Number Wrong'), _('Please input Faktur Number use SEPARATOR "."(DOT).'))
    #         obj_no_faktur.create(vals)
    #         self.no_faktur_vendor = obj_no_faktur.name
        
    #     return True