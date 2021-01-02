from odoo import models, fields, api
import os

SCSS_COLOR_URL = 'static/src/css/colors.scss'
FULL_PATH = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '..', SCSS_COLOR_URL))


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    theme_color_brand = fields.Char(
        string="Brand (#7E4861)", default='#7E4861')
    theme_color_primary = fields.Char(
        string="Primary (#01A29D)", default='#01A29D')

    @api.multi
    def set_values(self):
        if not self.theme_color_brand:
            self.theme_color_brand = '#7E4861'

        if not self.theme_color_primary:
            self.theme_color_primary = '#01A29D'
        colors = {
            '$o-community-color': self.theme_color_brand,
            '$o-community-primary-color': self.theme_color_primary
        }
        self._set_colors(colors)

        res = super(ResConfigSettings, self).set_values()
        return res

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        colors = self._get_colors()
        res.update({
            'theme_color_brand': colors['$o-community-color'],
            'theme_color_primary': colors['$o-community-primary-color']
        })
        return res

    def _get_colors(self):
        colors = {}
        with open(FULL_PATH, 'rt') as f:
            colors = dict(x.rstrip().split(':', 1) for x in f)

        return colors

    def _set_colors(self, d):
        with open(FULL_PATH, 'w') as f:
            for key, val in d.items():
                f.write(key + ':' + val + ';\n')

        self.env["ir.qweb"].clear_caches()
