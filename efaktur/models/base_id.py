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
import time
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning

class res_country_state(models.Model):
    _inherit = "res.country.state"
    
    name = fields.Char(string='Province')
    kabupaten_line = fields.One2many('res.kabupaten', 'state_id', string='Kabupaten')

class res_kabupaten(models.Model):
    _name = "res.kabupaten"
    _description = "List Kabupaten"
    
    name = fields.Char(string='Kabupaten')
    state_id = fields.Many2one('res.country.state', string="Province")
    kecamatan_line = fields.One2many('res.kecamatan', 'kabupaten_id', string='Kecamatan')
    

class res_kecamatan(models.Model):
    _name = "res.kecamatan"
    _description = "List Kecamatan"
    
    name = fields.Char(string='Kecamatan')
    state_id = fields.Many2one('res.country.state', string="Province")
    kabupaten_id = fields.Many2one('res.kabupaten', string="Kabupaten")
    kelurahan_line = fields.One2many('res.kelurahan', 'kecamatan_id', string='Kelurahan')

class res_kelurahan(models.Model):
    _name = "res.kelurahan"
    _description = "List Kelurahan"
    
    name = fields.Char(string='Kelurahan')
    state_id = fields.Many2one('res.country.state', string="Province")
    kabupaten_id = fields.Many2one('res.kabupaten', string="Kabupaten")
    kecamatan_id = fields.Many2one('res.kecamatan', string="Kabupaten")
    zip = fields.Char("Kode Post")