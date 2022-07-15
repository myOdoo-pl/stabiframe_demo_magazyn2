from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        """Extended method for generating values for the invoice that's about to be created.

        :param order: Origin sale order.
        :param name: Downpayment name.
        :param amount: Downpayment value.
        :param so_line: Record from origin sale order line that represents downpayment.
        :return: Values for create method of invoice model.
        """
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)

        # If this is downpayment invoice, add new value.
        if self.advance_payment_method != 'delivered':
            invoice_vals['is_downpayment'] = True

        if order.company_bank_id:
            invoice_vals['partner_bank_id'] = order.company_bank_id

        return invoice_vals

    def _get_advance_details(self, order):
        context = {'lang': order.partner_id.lang}

        taxes = self._check_same_taxes(order)

        if self.advance_payment_method == 'percentage':
            # CHANGED TO ALWAYS USE UNTAXED AMOUNT
            # if all(self.product_id.taxes_id.mapped('price_include')):
            #     amount = order.amount_total * self.amount / 100
            # else:
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount)
        else:
            amount = self.fixed_amount / (1 + (taxes.amount / 100))
            name = _('Down Payment')
        del context

        return amount, name

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices(final=self.deduct_down_payments)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                amount, name = self._get_advance_details(order)

                if self.product_id.invoice_policy != 'order':
                    raise UserError(
                        _('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(
                        _("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))

                # ORG: taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)

                taxes = self._check_same_taxes(order)

                tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
                so_line = sale_line_obj.create(so_line_values)
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    # METHOD CHECKING IF ALL TAXES ON SALE ORDER ARE THE SAME
    @staticmethod
    def _check_same_taxes(order):
        taxes_list = list()

        for line in order.order_line:
            taxes_list.append(line.tax_id)

        # check if taxes for all order lines are the same
        same_taxes = all(x == taxes_list[0] for x in taxes_list)

        if same_taxes:
            return taxes_list[0]
        else:
            raise UserError(_('In order to create a downpayment taxes for all order lines have to be identical.'))
