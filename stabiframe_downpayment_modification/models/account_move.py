from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_downpayment = fields.Boolean(string='Downpayment', readonly=True,
                                    help='Set this to True, if this invoice is a downpayment.')
    account_currency = fields.Char(string='Account Currency', readonly=True, related='partner_bank_id.currency_id.name')
