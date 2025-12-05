# -*- encoding: utf-8 -*-
from odoo import models, fields, api
from lxml import etree
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_order_liv = fields.Char(
        string='Purchase order liverpool',
        copy=False
    )
    delivery_folio = fields.Char(
        string='Delivery folio',
        copy=False
    )
    date_delivery = fields.Date(
        string='Date delivery',
        copy=False
    )
    require_addenda_liverpool = fields.Boolean(
        string="Use Addenda Liverpool",
        compute='_compute_require_addenda_liverpool',
        store=True
    )

    @api.depends('partner_id', 'partner_id.generate_addenda_liverpool')
    def _compute_require_addenda_liverpool(self):
        for move in self:
            move.require_addenda_liverpool = move.partner_id.generate_addenda_liverpool
            if move.partner_id.generate_addenda_liverpool and not move.l10n_mx_edi_addenda_id:
                liverpool_addenda = self.env.ref('w_addenda_liverpool.addenda_liverpool', raise_if_not_found=False)
                if liverpool_addenda:
                    move.l10n_mx_edi_addenda_id = liverpool_addenda

    def _l10n_mx_edi_addenda_liverpool(self):
        """Generate Liverpool addenda XML with line items."""
        self.ensure_one()

        # Build line items XML
        line_items_xml = ''
        line_count = 0

        for line in self.invoice_line_ids.filtered(lambda l: l.product_id and not l.display_type):
            line_count += 1
            barcode = line.product_id.barcode or '00000000000000'
            code = line.product_id.default_code or str(line.product_id.id)
            name = self.unescape_characters((line.product_id.name or line.name or 'PRODUCTO')[:35])
            quantity = line.get_quantity()
            unit = line.product_uom_id.name
            price_gross = line.get_price_gross()
            price_net = line.get_price_net()
            amount_gross = line.get_gross_amount()
            amount_net = line.get_net_amount()

            line_items_xml += f'''
                        <detallista:lineItem type="SimpleInvoiceLineItemType" number="{line_count}">
                            <detallista:tradeItemIdentification>
                                <detallista:gtin>{barcode}</detallista:gtin>
                            </detallista:tradeItemIdentification>
                            <detallista:alternateTradeItemIdentification type="SUPPLIER_ASSIGNED">{code}</detallista:alternateTradeItemIdentification>
                            <detallista:tradeItemDescriptionInformation language="ES">
                                <detallista:longText>{name}</detallista:longText>
                            </detallista:tradeItemDescriptionInformation>
                            <detallista:invoicedQuantity unitOfMeasure="{unit}">{quantity}</detallista:invoicedQuantity>
                            <detallista:grossPrice>
                                <detallista:Amount>{price_gross}</detallista:Amount>
                            </detallista:grossPrice>
                            <detallista:netPrice>
                                <detallista:Amount>{price_net}</detallista:Amount>
                            </detallista:netPrice>
                            <detallista:totalLineAmount>
                                <detallista:grossAmount>
                                    <detallista:Amount>{amount_gross}</detallista:Amount>
                                </detallista:grossAmount>
                                <detallista:netAmount>
                                    <detallista:Amount>{amount_net}</detallista:Amount>
                                </detallista:netAmount>
                            </detallista:totalLineAmount>
                        </detallista:lineItem>'''

        # Return the line items XML to be inserted
        return line_items_xml

    def unescape_characters(self, value):
        """Remove accents and special characters from text."""
        import unidecode
        return unidecode.unidecode(value)

    def get_total_amount(self):
        """Get total amount formatted for addenda."""
        return "%.2f" % round(self.amount_untaxed, 2)

    def _l10n_mx_edi_cfdi_amount_to_text(self):
        """Convert the invoice amount to text in Spanish."""
        self.ensure_one()
        if hasattr(super(AccountMove, self), '_l10n_mx_edi_cfdi_amount_to_text'):
            return super()._l10n_mx_edi_cfdi_amount_to_text()
        try:
            from odoo.addons.l10n_mx_edi.models.account_edi_format import CURRENCY_CODE_TO_NAME
            amount_text = self.currency_id.with_context(lang='es_MX').amount_to_text(self.amount_total)
            return amount_text.upper()
        except:
            return ""


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_price_gross(self):
        taxes_line = self.tax_ids
        if hasattr(taxes_line, 'flatten_taxes_hierarchy'):
            taxes_line = taxes_line.flatten_taxes_hierarchy()
        transferred = taxes_line.filtered(lambda r: r.amount >= 0)
        price_net = self.price_unit * self.quantity
        price_gross = price_net
        if transferred:
            for tax in transferred:
                tasa = abs(tax.amount if tax.amount_type == 'fixed' else (tax.amount / 100.0)) * 100
                price_gross += (price_net * tasa / 100)
        return "%.2f" % round(price_gross, 2)

    def get_price_net(self):
        return "%.2f" % round(self.price_unit * self.quantity, 2)

    def get_gross_amount(self):
        return "%.2f" % round(self.price_total, 2)

    def get_net_amount(self):
        return "%.2f" % round(self.price_subtotal, 2)

    def get_quantity(self):
        return "%.2f" % round(self.quantity, 2)
