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


import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class nomor_faktur_pajak(models.Model):
    _name = "nomor.faktur.pajak"
    _description = 'Nomor faktur Pajak'
    
    @api.one
    @api.depends('nomor_perusahaan', 'tahun_penerbit', 'nomor_urut')
    def _get_nomor_faktur(self):
        for faktur in self:    
            faktur.name = "%s.%s.%s" % (faktur.nomor_perusahaan, faktur.tahun_penerbit, faktur.nomor_urut)
            faktur.number = "%s%s%s" % (faktur.nomor_perusahaan, faktur.tahun_penerbit, faktur.nomor_urut)
            # faktur.state = '0'
            # if faktur.invoice_id and faktur.invoice_id.state not in ('draft','cancel'):
            #     faktur.state = '1'
    
    nomor_perusahaan = fields.Char('Nomor Perusahaan', size=3)
    tahun_penerbit = fields.Char('Tahun Penerbit', size=2)
    nomor_urut = fields.Char('Nomor Urut', size=8)
    name = fields.Char(string='Nomor Faktur', compute='_get_nomor_faktur', store=True)
    number = fields.Char(string='Nomor eFaktur', compute='_get_nomor_faktur', store=True)
    invoice_id = fields.Many2one('account.invoice', 'Invoice No')
    # uang_muka_id = fields.Many2one('adhimix.invoice.uang.muka', 'No Invoice Uang Muka')
    partner_id = fields.Many2one('res.partner', string='Partner', related='invoice_id.partner_id', store=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', related='invoice_id.amount_untaxed', store=True)
    amount_tax = fields.Monetary(string='Tax Amount', related='invoice_id.amount_tax', store=True)
    date_invoice = fields.Date(string='Date Used', related='invoice_id.date_invoice', store=True)
    company_id = fields.Many2one('res.company', string='Company', related='invoice_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='invoice_id.currency_id', store=True)
    type = fields.Selection([('in','Faktur Pajak Masukan'),('out','Faktur Pajak Keluaran')], string='Type')
    status = fields.Selection([('1','Used'),('0','Not Used')],string='Status',default='0')
    
    _sql_constraints = [
        ('faktur_unique', 'unique(nomor_perusahaan,tahun_penerbit,nomor_urut)', 'Number Faktur Must Be Unique.'),
    ]