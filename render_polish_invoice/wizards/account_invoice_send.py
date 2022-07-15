from odoo import api, fields, models, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    @api.onchange('attachment_ids')
    def add_polish_invoice(self):
        invoice = self.env['account.move'].search(
            [('id', 'in', self._context.get('active_ids'))])[0]  # Search for active invoice

        if invoice.is_polish_invoice_required and (not invoice.is_already_rendered):  # Check if invoice was added once
            invoice.is_already_rendered = True  # Set flag as True
            self.create_polish_invoice()  # Attach polish invoice

    def create_polish_invoice(self):
        lang = self.env['res.lang'].search([('code', '=', 'pl_PL')])[0]

        for invoice in self.invoice_ids:

            original_lang = invoice.partner_id.lang
            invoice.partner_id.lang = lang.code  # Change partner lang for pl_PL
            pdf = self.env.ref('account.account_invoices').sudo()._render_qweb_pdf([invoice.id])[0]
            invoice.partner_id.lang = original_lang

            invoice_name = f"Faktura_{invoice.name}.pdf".replace("/", "_")
            self.attachment_ids += self.env['ir.attachment'].create({
                'name': invoice_name,
                'type': 'binary',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'mimetype': 'application/pdf',
                'datas': base64.b64encode(pdf),  # base64.b64encode(xml)
            })
