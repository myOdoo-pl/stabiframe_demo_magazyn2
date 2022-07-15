from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    company_bank_id = fields.Many2one('res.partner.bank', string='Your Bank Account', help='Your bank account number.')
