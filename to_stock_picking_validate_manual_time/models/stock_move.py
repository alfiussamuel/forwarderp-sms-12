from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _set_backdate(self, backdate):
        """
        set backdate for done stock moves and their conresponding done stock move lines
        """
        self.filtered(lambda x: x.state == 'done').write({'date': backdate})
        move_line_ids = self.mapped('move_line_ids').filtered(lambda x: x.state == 'done')
        if move_line_ids:
            move_line_ids.write({'date': backdate})

    def _action_done(self):
        res = super(StockMove, self)._action_done()
        manual_validate_date_time = self._context.get('manual_validate_date_time', False)
        if manual_validate_date_time:
            self._set_backdate(manual_validate_date_time)
        return res

