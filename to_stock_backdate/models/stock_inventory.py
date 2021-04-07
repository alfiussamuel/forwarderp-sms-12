from odoo import models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_validate(self):
        # somewhere this is called with multi in self, so we need to fallback to the default behaviour in such the case
        if not self._context.get('manual_validate_date_time') and self.env.user.has_group('to_backdate.group_backdate') and not len(self) > 1:
            view = self.env.ref('to_stock_backdate.stock_inventory_backdate_wizard_form_view')
            ctx = dict(self._context or {})
            ctx.update({'default_inventory_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.inventory.backdate.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }
        return super(StockInventory, self).action_validate()

