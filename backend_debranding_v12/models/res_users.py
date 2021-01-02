# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models, modules
from odoo.tools import pycompat


class Users(models.Model):
    """ Update of res.users class
        - add a preference about sending emails about notifications
        - make a new user follow itself
        - add a welcome message
        - add suggestion preference
        - if adding groups to an user, check mail.channels linked to this user
          group, and the user. This is done by overriding the write method.
    """
    _inherit = 'res.users'

    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in forwardERP')],
        'Notification Management', required=True, default='email',
        help="Policy on how to handle Chatter notifications:\n"
             "- Emails: notifications are sent to your email\n"
             "- forwardERP: notifications appear in your forwardERP Inbox")