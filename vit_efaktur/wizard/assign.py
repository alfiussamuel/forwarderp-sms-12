from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AssignConfirm(models.TransientModel):
    _name = 'vit.assign_wizard'
    _description = 'Assign Confirmation'


    def _get_active_invoices(self):
        if self._context.get('active_model') == 'account.invoice':
            return self._context.get('active_ids', False)
        return False
    
    invoice_ids = fields.Many2many(comodel_name="account.invoice", string="Invoices", required=True,
                                 default=_get_active_invoices)

    efaktur_id = fields.Many2one(comodel_name="vit.efaktur", string="Nomor E-Faktur", required=False, )

    """
    logika:
    update invoice_ids.efaktur_id dengan yang dipilih
    :return:
    """

    @api.multi
    def confirm_button(self):
        self.ensure_one()

        for inv in self.invoice_ids:
            inv.efaktur_id = self.efaktur_id
        
        return {'type': 'ir.actions.act_window_close'}
