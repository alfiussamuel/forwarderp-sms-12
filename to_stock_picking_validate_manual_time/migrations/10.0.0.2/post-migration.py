# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    cr.execute("""
        UPDATE stock_pack_operation AS spo
        SET date = sp.date
        FROM stock_picking AS sp
        WHERE sp.id = spo.picking_id
            AND sp.state = 'done'
            AND spo.date != sp.date
    """)

