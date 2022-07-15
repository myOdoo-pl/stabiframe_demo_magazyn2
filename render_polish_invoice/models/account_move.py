from odoo import api, fields, models
import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_already_rendered = fields.Boolean(defualt=False, store=True)
    is_polish_invoice_required = fields.Boolean(compute='compute_partner_fr')

    def action_invoice_sent(self):
        self.is_already_rendered = False
        return super(AccountMove, self).action_invoice_sent()

    def compute_partner_fr(self):
        self.is_polish_invoice_required = self.partner_id.lang in \
                                          ['fr_FR', 'fr_BE', 'en_US']  # Partners Lang that need polish invoice
