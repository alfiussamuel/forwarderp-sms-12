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


from odoo import api, fields, models, tools, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.osv.orm import browse_record

ADDRESS_FIELDS = ('street', 'street2', 'rt', 'rw', 'kelurahan_id', 'kecamatan_id_new', 'kabupaten_id', 'zip', 'city', 'state_id', 'country_id')

class res_partner(models.Model):
    _inherit = 'res.partner'
    _description = 'res partner'
    
    is_npwp = fields.Boolean('Is NPWP Address?')
    npwp = fields.Char('NPWP')
    ktp = fields.Char('KTP')
    type = fields.Selection(selection_add=[
                             ('npwp', 'NPWP'),
                             ('ktp', 'KTP'),
                             ('technical', 'Technical')])
    cluster = fields.Selection([('yes','YES'),('no','NO')], string='Cluster', help='Cluster') 
    code_transaction = fields.Selection([('01','01 Normal'),
                                         ('02','02 Bendaharawan (Tdk Terlampir)'),
                                         ('03','03 Bendaharawan (Terlampir)'),
                                         ('08','08 Tanpa PPN')], string='Kode Transaksi', 
                                        default='01', help='Kode Transaksi Faktur Pajak')
    blok = fields.Char('Blok', size=8)
    nomor = fields.Char('Nomor', size=8)
    rt = fields.Char('RT', size=3)
    rw = fields.Char('RW', size=3)
    kelurahan_id = fields.Many2one('res.kelurahan', string="Kelurahan")
    kecamatan_id_new = fields.Many2one('res.kecamatan', string="Kecamatan")
    kabupaten_id = fields.Many2one('res.kabupaten', string="Kabupaten")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')], string='Status') 
    
#     _sql_constraints = [
#         ('npwp_uniq', 'unique(npwp)', 'The npwp of the customer must be unique!'),
#     ]
    
    @api.multi
    def _display_address(self, without_company=False):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        #address_format = self.country_id.address_format or \
        address_format =      "%(street)s\n%(street2)s Blok %(blok)s/No.%(nomor)s RT/RW: %(rt)s/%(rw)s\nKel. %(kelurahan_name)s, Kec. %(kecamatan_name)s, Kab. %(kabupaten_name)s\n%(city)s - %(state_name)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': self.commercial_company_name or '',
            'blok': self.blok or '',
            'nomor': self.nomor or '',
            'rt': self.rt or '',
            'rw': self.rw or '',
            'kabupaten_name': self.kabupaten_id.name or '',
            'kecamatan_name': self.kecamatan_id_new.name or '',
            'kelurahan_name': self.kelurahan_id.name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    
    @api.onchange('kelurahan_id')
    def onchange_kelurahan_id(self):
        if not self.kelurahan_id:
            return
        if self.kelurahan_id.kecamatan_id:
            self.kecamatan_id_new = self.kelurahan_id.kecamatan_id.id
        if self.kelurahan_id.kabupaten_id:
            self.kabupaten_id = self.kelurahan_id.kabupaten_id.id
        if self.kelurahan_id.kabupaten_id and self.kelurahan_id.kabupaten_id.state_id:
            self.state_id = self.kelurahan_id.kabupaten_id.state_id.id
        if self.kelurahan_id.kabupaten_id and self.kelurahan_id.kabupaten_id.state_id and self.kelurahan_id.kabupaten_id.state_id.country_id:
            self.country_id = self.kelurahan_id.kabupaten_id.state_id.country_id.id
        
    @api.onchange('kecamatan_id_new')
    def onchange_kecamatan_id(self):
        if not self.kecamatan_id_new:
            return
        if self.kecamatan_id_new.kabupaten_id:
            self.kabupaten_id = self.kecamatan_id_new.kabupaten_id.id
        if self.kecamatan_id_new.kabupaten_id and self.kecamatan_id_new.kabupaten_id.state_id:
            self.state_id = self.kecamatan_id_new.kabupaten_id.state_id.id
        if self.kecamatan_id_new.kabupaten_id and self.kecamatan_id_new.kabupaten_id.state_id and self.kecamatan_id_new.kabupaten_id.state_id.country_id:
            self.country_id = self.kecamatan_id_new.kabupaten_id.state_id.country_id.id
            
    @api.onchange('kabupaten_id')
    def onchange_kabupaten_id(self):
        if not self.kabupaten_id:
            return
        if self.kabupaten_id.state_id:
            self.state_id = self.kabupaten_id.state_id.id or False
        if self.kabupaten_id.state_id and self.kabupaten_id.state_id.country_id:
            self.country_id = self.kabupaten_id.state_id.country_id.id
    
    # @api.onchange('npwp')
    # def onchange_npwp(self):
    #     res = {}
    #     vals = {}
    #     if not self.npwp:
    #         return
    #     elif len(npwp)==20:
    #         self.npwp = npwp
    #     elif len(npwp)==15:
    #         formatted_npwp = npwp[:2]+'.'+npwp[2:5]+'.'+npwp[5:8]+'.'+npwp[8:9]+'-'+npwp[9:12]+'.'+npwp[12:15]
    #         self.npwp = formatted_npwp
    #     else:
    #         warning = {
    #             'title': _('Warning'),
    #             'message': _('Wrong Format must 15 digit'),
    #         }
    #         return {'warning': warning, 'value' : {'npwp' : False}}
    #     return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
