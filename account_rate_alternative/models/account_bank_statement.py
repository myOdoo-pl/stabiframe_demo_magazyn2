# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _

from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class AccountBankStatement(models.Model):
    _inherit="account.bank.statement"

    custom_currency_rate = fields.Float('Inny kurs waluty', digits=(12,6), help="To pole służy do jednorazowej zmiany kursu waluty. Aby wykorzystać kurs pobrany z NBP, pozostaw to pole bez zmian.")
    inverse_rate = fields.Boolean('Wartość odwrócona', help="Zaznaczone, jeśli kurs waluty jest wpisywany zgodnie z Polskimi standardami, np. PLN/EUR = 4.36; odznaczone, jeśli kurs jest wpisywny zgodnie ze standardem Odoo, np. EUR/PLN = 0.23", default=True)

class AccountBankStatementLine(models.Model):
    _inherit="account.bank.statement.line"

    custom_currency_rate_line = fields.Float('Inny kurs waluty', digits=(12,6), help="To pole służy do jednorazowej zmiany kursu waluty. Aby wykorzystać kurs pobrany z NBP, pozostaw to pole bez zmian.")
    inverse_rate = fields.Boolean('Wartość odwrócona', help="Zaznaczone, jeśli kurs waluty jest wpisywany zgodnie z Polskimi standardami, np. PLN/EUR = 4.36; odznaczone, jeśli kurs jest wpisywny zgodnie ze standardem Odoo, np. EUR/PLN = 0.23", default=True)

    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        CurrencyRate = self.env['res.currency.rate']
        currency_id = self.currency_id or self.statement_id.currency_id
        rate_id = CurrencyRate.search([('currency_id', '=', currency_id.id), ('name', '=', self.date)])
        custom_rate = self.statement_id.custom_currency_rate
        custom_rate_line = self.custom_currency_rate_line

        if self.statement_id.inverse_rate and custom_rate:
            custom_rate = 1/custom_rate
        if self.inverse_rate and custom_rate_line:
            custom_rate_line = 1/custom_rate_line

        if rate_id:
            old_rate = rate_id.rate
            if custom_rate_line:
                rate_id.write({'rate': custom_rate_line})
            elif custom_rate:
                rate_id.write({'rate': custom_rate})
        elif custom_rate_line or custom_rate:
            new_rate_id = CurrencyRate.create({'currency_id': currency_id.id, 'name': self.date, 'rate': custom_rate_line or custom_rate})

        res = super(AccountBankStatementLine, self).process_reconciliation(counterpart_aml_dicts=counterpart_aml_dicts, payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts)

        if rate_id:
            rate_id.rate = old_rate
        elif custom_rate_line or custom_rate:
            new_rate_id.unlink()

        return res
