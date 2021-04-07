from odoo import fields, models


class StockWarnInsufficientQtyScrap(models.TransientModel):
    _inherit = 'stock.warn.insufficient.qty.scrap'

    scrap_backdate = fields.Datetime(string='Scrap Backdate')

    def action_done(self):
        if self.scrap_backdate:
            return super(StockWarnInsufficientQtyScrap, self.with_context(
                manual_validate_date_time=self.scrap_backdate,
                force_period_date=self.scrap_backdate)).action_done()
        return super(StockWarnInsufficientQtyScrap, self).action_done()
