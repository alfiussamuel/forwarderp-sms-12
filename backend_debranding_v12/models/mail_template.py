# Copyright 2018 Planet Odoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# This is used for replacing odoo to Planet Odoo in emails

import re
from odoo import _, api, models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.multi
    def generate_email(self, res_ids, fields=None):
        obj = self.with_context(mail_debrand=True)
        return super(MailTemplate, obj).generate_email(res_ids, fields=fields)

    @api.model
    def _debrand_body(self, body):
        using_word = _('using')
        # print(body)
        body=re.sub(
            _('Odoo') , "forwardERP", body,
        )
        return re.sub(
             'https://www.odoo.com','http://www.planet-odoo.com/', body,
        )

    @api.model
    def render_template(self, template_txt, model, res_ids,
                        post_process=False):
        res = super(MailTemplate, self).render_template(
            template_txt, model, res_ids, post_process=post_process,
        )
        if self.env.context.get('mail_debrand'):
            if isinstance(res, str):
                res = self._debrand_body(res)
            else:
                for res_id, body in res.items():
                    res[res_id] = self._debrand_body(body)
        return res

