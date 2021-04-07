from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AbstractInventoryBackdateWizard(models.AbstractModel):
    _name = 'abstract.inventory.backdate.wizard'
    _description = 'Inventory Backdate Wizard Abstract'

    date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True,
                                help="The date and time at which the operation was actually done.")

    @api.constrains('date')
    def _check_date(self):
        for r in self:
            if r.date > fields.Datetime.now():
                raise UserError(_("You may not be able to specify a date in the future!"))

    def process(self):
        raise UserError(_("The method process() has not been implemented for the model %s. This could be a programming error...") % self._name)
