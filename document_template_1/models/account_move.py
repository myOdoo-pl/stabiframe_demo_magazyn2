from odoo import api, fields, models
import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_origin')
    def _set_main_so(self):
        """Compute method for obtaining sale document from which invoice originated."""
        for invoice in self:
            invoice.main_so_id = None

            if invoice.invoice_origin:
                # Check invoice type, to avoid searching wrong source document.
                if invoice.move_type in ['out_invoice', 'out_refund']:
                    # Search for sale document and assign it to new field as clickable record.
                    origin_sp = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])
                    invoice.main_so_id = origin_sp.id

    def _get_ref_from_ref(self):
        self.correction_ref = ''
        if self.ref:
            self.correction_ref = self.ref.split(', ')[0]

    def _get_reason_from_ref(self):
        self.correction_reason = ''
        if self.ref:
            reason = self.ref.split(', ')[1:]
            self.correction_reason = ''.join([s+', ' for s in reason])[:-2]

    main_so_id = fields.Many2one('sale.order', string='Origin Sale Document', compute='_set_main_so',
                                 help='Field for storing origin document for this invoice.')

    correction_ref = fields.Char(compute='_get_ref_from_ref')

    correction_reason = fields.Char(compute='_get_reason_from_ref')

    payment_method = fields.Selection(
        [('bank', 'Bank transfer'), ('cash', 'Cash'), ('prepayment', 'Prepayment')],
        string="Payment method",
        default="bank"
    )

    days_to_payment = fields.Integer(compute='_compute_days_to_payment')

    def _compute_days_to_payment(self):
        if self.invoice_date_due and self.invoice_date:
            self.days_to_payment = (self.invoice_date_due - self.invoice_date).days