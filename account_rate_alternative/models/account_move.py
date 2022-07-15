# -*- coding: utf-8 -*-
import pprint
import logging
import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang

from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    date_custom_curr_rate = fields.Date(string='Custom currency rate date',
        readonly=True, states={'draft': [('readonly', False)], 'new': [('readonly', False)]},
        copy=False)

    custom_currency_rate_view = fields.Float(digits=(12,4), string="Custom currency rate", store=True)
    custom_currency_rate = fields.Float(related='custom_currency_rate_view', readonly=True, digits=(12,4))



    date_tax_curr_rate = fields.Date(string='Tax Currency Rate Date',
        readonly=True, states={'draft': [('readonly', False)], 'new': [('readonly', False)]},
        help="Date of currency rate for VAT. Use if VAT should be paid with different currency difference account (account has to b change manually). Instead you can also enter VAT home currency value manually. ", copy=False)

    tax_home_currency_view = fields.Float()
    tax_home_currency = fields.Float(related='tax_home_currency_view', string='Tax in Home Currency (PLN)', store=True,
            digits=(16,2), readonly=True, states={'draft': [('readonly', False)], 'new': [('readonly', False)]},
            help="Enter tax value in home currency (PLN) to have tax in home currency calculated different way than net value (different rate, different currency rate difference account). Leave empty for standard calculation.")

    base_home_currency_view = fields.Float()
    base_home_currency = fields.Float(related='base_home_currency_view', string="Tax Base in Home Currency (PLN)", store=True, digits=(16,2), readonly=True, states={'draft': [('readonly', False)], 'new': [('readonly', False)]}, help="Enter tax base in home currency (PLN), to have tax base in home currency calculated different way. Leave empty to preserve current value or to compute from Tax in Home Currency field if set.")



    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for inv in self:
            if inv.custom_currency_rate_view == 0.0 or inv.custom_currency_rate_view == False:
                if inv.date_custom_curr_rate and inv.currency_id:
                    inv.custom_currency_rate_view = 1/inv.currency_id.with_context(date=inv.date_custom_curr_rate).rate
                elif inv.invoice_date and inv.currency_id:
                    inv.custom_currency_rate_view = 1/inv.currency_id.with_context(date=inv.invoice_date).rate
        return res


    @api.onchange('date_tax_curr_rate')
    def _onchange_date_tax_curr_rate(self):
        self.tax_home_currency_view = self.amount_tax / self.currency_id.with_context(date=self.date_tax_curr_rate).rate
        self.base_home_currency_view = self.amount_untaxed / self.currency_id.with_context(date=self.date_tax_curr_rate).rate

    @api.onchange('date_custom_curr_rate', 'currency_id', 'invoice_date')
    def _onchange_custom_curr_date_rate(self):
        if self.date_custom_curr_rate and self.currency_id:
            self.custom_currency_rate_view = 1/self.currency_id.with_context(date=self.date_custom_curr_rate).rate
        elif not self.date_custom_curr_rate and self.currency_id:
            self.custom_currency_rate_view = 1/self.currency_id.with_context(date=self.invoice_date).rate
        for line in self.line_ids:
            line._onchange_amount_currency()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    @api.onchange('amount_currency', 'currency_id', 'account_id')
    def _onchange_amount_currency(self):
        force_date = False
        for line in self:
            if line.move_id.date_custom_curr_rate:
                force_date = line.move_id.date_custom_curr_rate
            break
        if force_date:
            super(AccountMoveLine, self.with_context(force_date=force_date))._onchange_amount_currency()
        else:
            super(AccountMoveLine, self)._onchange_amount_currency()
