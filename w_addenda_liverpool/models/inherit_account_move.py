# -*- encoding: utf-8 -*-
#
# Module written to Odoo, Open Source Management Solution
#
# Copyright (c) 2022 Birtum - http://www.birtum.com/
# All Rights Reserved.
#
# Developer(s): Eddy Luis Pérez Vila
#               (epv@birtum.com)
########################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
import logging
import unidecode

from lxml import etree

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """Extend account.move to add Liverpool addenda fields."""

    _inherit = 'account.move'

    purchase_order_liv = fields.Char(
        string='Purchase Order Liverpool',
        help='If the invoice is for the Liverpool customer, indicate the '
             'number of the purchase order.',
        copy=False,
    )
    delivery_folio = fields.Char(
        string='Delivery Folio',
        help='Specify the folio number. Number issued by the buyer when they '
             'receive the merchandise that is billed.',
        copy=False,
    )
    date_delivery = fields.Date(
        string='Date Delivery',
        help='Specify the date the receipt sheet number was assigned.',
        copy=False,
    )
    require_addenda_liverpool = fields.Boolean(
        string="Use Addenda Liverpool",
        compute='_compute_require_addenda_liverpool',
        store=True,
        help="Field used to show or hide the fields created for the Liverpool addenda.",
    )

    @api.depends('partner_id', 'partner_id.generate_addenda_liverpool')
    def _compute_require_addenda_liverpool(self):
        """Compute if Liverpool addenda is required based on partner configuration."""
        for move in self:
            move.require_addenda_liverpool = (
                move.partner_id.generate_addenda_liverpool
            )

    def unescape_characters(self, value):
        """Remove special characters and accents from text."""
        return unidecode.unidecode(value)

    def get_total_amount(self):
        """Return total amount without taxes formatted to 2 decimals."""
        return "%.2f" % round(self.amount_untaxed, 2)

    def _l10n_mx_edi_cfdi_amount_to_text(self):
        """
        Convert the invoice amount to text in Spanish for Mexican localization.

        Returns:
            str: Amount in text format (Spanish)
        """
        self.ensure_one()
        # Try to use the standard Odoo method if it exists
        if hasattr(super(AccountMove, self), '_l10n_mx_edi_cfdi_amount_to_text'):
            return super()._l10n_mx_edi_cfdi_amount_to_text()

        # Otherwise, use the currency's amount_to_text method
        try:
            from odoo.addons.l10n_mx_edi.models.account_edi_format import (
                CURRENCY_CODE_TO_NAME,
            )
            currency_name = CURRENCY_CODE_TO_NAME.get(
                self.currency_id.name, self.currency_id.name
            )
            amount_text = self.currency_id.with_context(
                lang='es_MX'
            ).amount_to_text(self.amount_total)
            return amount_text.upper()
        except Exception as e:
            _logger.warning(
                'Error converting amount to text for invoice %s: %s',
                self.name, str(e)
            )
            # Fallback: return empty string if conversion fails
            return ""

    def _l10n_mx_edi_cfdi_append_addenda(self, cfdi, addenda):
        """
        Append Liverpool addenda to the CFDI XML.

        Args:
            cfdi: XML element for the CFDI
            addenda: Unused parameter (kept for compatibility)

        Returns:
            None: Modifies cfdi in place
        """
        if not self.require_addenda_liverpool:
            return super()._l10n_mx_edi_cfdi_append_addenda(cfdi, addenda)

        # Get the root element (Comprobante)
        if cfdi.tag == '{http://www.sat.gob.mx/cfd/4}Comprobante':
            comprobante = cfdi
        else:
            comprobante = cfdi.find('{http://www.sat.gob.mx/cfd/4}Comprobante')

        if comprobante is None:
            _logger.warning(
                'Could not find Comprobante element in CFDI for invoice %s',
                self.name
            )
            return super()._l10n_mx_edi_cfdi_append_addenda(cfdi, addenda)

        # Create addenda element
        try:
            addenda_element = self._create_liverpool_addenda_element()
            comprobante.append(addenda_element)
        except Exception as e:
            _logger.error(
                'Error creating Liverpool addenda for invoice %s: %s',
                self.name, str(e)
            )

        return super()._l10n_mx_edi_cfdi_append_addenda(cfdi, addenda)

    def _create_liverpool_addenda_element(self):
        """
        Create the Liverpool addenda XML element.

        Returns:
            etree.Element: The Addenda element with Liverpool detallista
        """
        # Namespace definitions
        cfdi_ns = 'http://www.sat.gob.mx/cfd/4'
        detallista_ns = 'http://www.sat.gob.mx/detallista'

        # Create Addenda element
        addenda = etree.Element(
            f'{{{cfdi_ns}}}Addenda'
        )

        # Create detallista element
        detallista = etree.SubElement(
            addenda,
            f'{{{detallista_ns}}}detallista',
            attrib={
                'contentVersion': '1.3.1',
                'documentStructureVersion': 'AMC8.1',
                'type': 'SimpleInvoiceType',
                'documentStatus': 'ORIGINAL',
            },
            nsmap={'detallista': detallista_ns}
        )

        # Request for payment identification
        payment_id = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}requestForPaymentIdentification'
        )
        entity_type = etree.SubElement(
            payment_id,
            f'{{{detallista_ns}}}entityType'
        )
        entity_type.text = (
            'INVOICE' if self.move_type in ('out_invoice', 'in_invoice')
            else 'CREDIT_NOTE'
        )

        # Special instruction
        special_inst = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}specialInstruction',
            code='ZZZ'
        )
        inst_text = etree.SubElement(
            special_inst,
            f'{{{detallista_ns}}}text'
        )
        inst_text.text = self.unescape_characters(
            self._l10n_mx_edi_cfdi_amount_to_text() or ''
        )

        # Order identification
        order_id = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}orderIdentification'
        )
        order_ref = etree.SubElement(
            order_id,
            f'{{{detallista_ns}}}referenceIdentification',
            type='ON'
        )
        order_ref.text = self.purchase_order_liv or 'N/A'

        # Additional information
        add_info = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}AdditionalInformation'
        )
        add_ref = etree.SubElement(
            add_info,
            f'{{{detallista_ns}}}referenceIdentification',
            type='IV'
        )
        add_ref.text = self.unescape_characters(self.name or '')

        # Delivery note
        delivery = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}DeliveryNote'
        )
        delivery_ref = etree.SubElement(
            delivery,
            f'{{{detallista_ns}}}referenceIdentification'
        )
        delivery_ref.text = self.delivery_folio or 'N/A'
        delivery_date = etree.SubElement(
            delivery,
            f'{{{detallista_ns}}}ReferenceDate'
        )
        delivery_date.text = str(
            self.date_delivery or self.invoice_date or ''
        )

        # Buyer
        buyer = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}buyer'
        )
        buyer_gln = etree.SubElement(
            buyer,
            f'{{{detallista_ns}}}gln'
        )
        buyer_gln.text = (
            self.partner_id.global_localitation_number or '0000000000000'
        )
        if self.partner_id.person_order_department:
            contact = etree.SubElement(
                buyer,
                f'{{{detallista_ns}}}contactInformation'
            )
            person_name = etree.SubElement(
                contact,
                f'{{{detallista_ns}}}personOrDepartmentName'
            )
            person_text = etree.SubElement(
                person_name,
                f'{{{detallista_ns}}}text'
            )
            person_text.text = self.unescape_characters(
                self.partner_id.person_order_department
            )

        # Seller
        seller = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}seller'
        )
        seller_gln = etree.SubElement(
            seller,
            f'{{{detallista_ns}}}gln'
        )
        seller_gln.text = (
            self.company_id.global_localitation_number or '0000000000000'
        )
        seller_alt_id = etree.SubElement(
            seller,
            f'{{{detallista_ns}}}alternatePartyIdentification',
            type='SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY'
        )
        seller_alt_id.text = (
            self.partner_id.supplier_identification or
            self.company_id.vat or
            'N/A'
        )

        # Line items
        line_count = 0
        for line in self.invoice_line_ids.filtered(lambda l: l.product_id):
            line_count += 1
            line_item = etree.SubElement(
                detallista,
                f'{{{detallista_ns}}}lineItem',
                attrib={
                    'number': str(line_count),
                    'type': 'SimpleInvoiceLineItemType',
                }
            )

            # Trade item identification (GTIN/Barcode)
            trade_id = etree.SubElement(
                line_item,
                f'{{{detallista_ns}}}tradeItemIdentification'
            )
            gtin = etree.SubElement(
                trade_id,
                f'{{{detallista_ns}}}gtin'
            )
            gtin.text = line.product_id.barcode or '00000000000000'

            # Alternate trade item ID (product code)
            alt_trade_id = etree.SubElement(
                line_item,
                f'{{{detallista_ns}}}alternateTradeItemIdentification',
                type='SUPPLIER_ASSIGNED'
            )
            alt_trade_id.text = (
                line.product_id.default_code or str(line.product_id.id)
            )

            # Trade item description
            trade_desc = etree.SubElement(
                line_item,
                f'{{{detallista_ns}}}tradeItemDescriptionInformation',
                language='ES'
            )
            long_text = etree.SubElement(
                trade_desc,
                f'{{{detallista_ns}}}longText'
            )
            product_name = (
                line.product_id.name or line.name or 'PRODUCTO'
            )[:35]
            long_text.text = self.unescape_characters(product_name)

            # Invoiced quantity
            invoiced_qty = etree.SubElement(
                line_item,
                f'{{{detallista_ns}}}invoicedQuantity',
                unitOfMeasure=line.product_uom_id.name
            )
            invoiced_qty.text = line.get_quantity()

            # Gross price
            gross_price = etree.SubElement(
                line_item,
                f'{{{detallista_ns}}}grossPrice'
            )
            gross_amount_elem = etree.SubElement(
                gross_price,
                f'{{{detallista_ns}}}Amount'
            )
            gross_amount_elem.text = line.get_price_gross()

            # Net price
            net_price = etree.SubElement(
                line_item,
                f'{{{detallista_ns}}}netPrice'
            )
            net_amount_elem = etree.SubElement(
                net_price,
                f'{{{detallista_ns}}}Amount'
            )
            net_amount_elem.text = line.get_price_net()

            # Total line amount
            total_line = etree.SubElement(
                line_item,
                f'{{{detallista_ns}}}totalLineAmount'
            )
            gross_total = etree.SubElement(
                total_line,
                f'{{{detallista_ns}}}grossAmount'
            )
            gross_amt = etree.SubElement(
                gross_total,
                f'{{{detallista_ns}}}Amount'
            )
            gross_amt.text = line.get_gross_amount()

            net_total = etree.SubElement(
                total_line,
                f'{{{detallista_ns}}}netAmount'
            )
            net_amt = etree.SubElement(
                net_total,
                f'{{{detallista_ns}}}Amount'
            )
            net_amt.text = line.get_net_amount()

        # Total amount
        total_amount = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}totalAmount'
        )
        total_amt = etree.SubElement(
            total_amount,
            f'{{{detallista_ns}}}Amount'
        )
        total_amt.text = self.get_total_amount()

        # Total allowance charge
        total_allow = etree.SubElement(
            detallista,
            f'{{{detallista_ns}}}TotalAllowanceCharge',
            allowanceOrChargeType='ALLOWANCE'
        )
        allow_amt = etree.SubElement(
            total_allow,
            f'{{{detallista_ns}}}Amount'
        )
        allow_amt.text = '0.00'

        return addenda


class AccountMoveLine(models.Model):
    """Extend account.move.line to add price calculation methods for Liverpool addenda."""

    _inherit = 'account.move.line'

    def get_price_gross(self):
        """
        Calculate gross price (price + taxes) for Liverpool addenda.

        Returns:
            str: Formatted gross price with 2 decimals
        """
        # Get taxes for the line
        taxes_line = self.tax_ids
        # In v18, use taxes directly
        if hasattr(taxes_line, 'flatten_taxes_hierarchy'):
            taxes_line = taxes_line.flatten_taxes_hierarchy()
        transferred = taxes_line.filtered(lambda r: r.amount >= 0)
        price_net = self.price_unit * self.quantity
        price_gross = price_net
        if transferred:
            for tax in transferred:
                tasa = abs(
                    tax.amount if tax.amount_type == 'fixed'
                    else (tax.amount / 100.0)
                ) * 100
                price_gross += (price_net * tasa / 100)
        return "%.2f" % round(price_gross, 2)

    def get_price_net(self):
        """
        Calculate net price (price without taxes) for Liverpool addenda.

        Returns:
            str: Formatted net price with 2 decimals
        """
        return "%.2f" % round(self.price_unit * self.quantity, 2)

    def get_gross_amount(self):
        """
        Get total line amount with taxes for Liverpool addenda.

        Returns:
            str: Formatted gross amount with 2 decimals
        """
        return "%.2f" % round(self.price_total, 2)

    def get_net_amount(self):
        """
        Get total line amount without taxes for Liverpool addenda.

        Returns:
            str: Formatted net amount with 2 decimals
        """
        return "%.2f" % round(self.price_subtotal, 2)

    def get_quantity(self):
        """
        Get line quantity for Liverpool addenda.

        Returns:
            str: Formatted quantity with 2 decimals
        """
        return "%.2f" % round(self.quantity, 2)