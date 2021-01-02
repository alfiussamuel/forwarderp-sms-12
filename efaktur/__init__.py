# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import wizard
import models
import report

def _post_init(cr, registry):
    """Import CSV data as it is faster than xml and because we can't use noupdate anymore with csv"""
    from odoo.tools import convert_file
    
    filename_1 = 'data/res.kabupaten.csv'
    filename_2 = 'data/res.kecamatan.csv'
    filename_3 = 'data/res.kelurahan.csv'
    
    convert_file(cr, 'efaktur', filename_1, None, mode='init', noupdate=True, kind='init', report=None)
    convert_file(cr, 'efaktur', filename_2, None, mode='init', noupdate=True, kind='init', report=None)
    convert_file(cr, 'efaktur', filename_3, None, mode='init', noupdate=True, kind='init', report=None)

