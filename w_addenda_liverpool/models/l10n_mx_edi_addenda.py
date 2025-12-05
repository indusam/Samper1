# -*- encoding: utf-8 -*-
from odoo import models, api


class L10nMxEdiAddenda(models.Model):
    _inherit = 'l10n_mx_edi.addenda'

    @api.model
    def _l10n_mx_edi_render_addenda_liverpool(self, move):
        """Generate complete Liverpool addenda XML."""
        # Build line items
        line_items_xml = ''
        line_count = 0

        for line in move.invoice_line_ids.filtered(lambda l: l.product_id and not l.display_type):
            line_count += 1
            barcode = line.product_id.barcode or '00000000000000'
            code = line.product_id.default_code or str(line.product_id.id)
            name = move.unescape_characters((line.product_id.name or line.name or 'PRODUCTO')[:35])
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

        # Build complete addenda XML
        entity_type = 'INVOICE' if move.move_type in ('out_invoice', 'in_invoice') else 'CREDIT_NOTE'
        amount_text = move.unescape_characters(move._l10n_mx_edi_cfdi_amount_to_text())
        purchase_order = move.purchase_order_liv or 'N/A'
        invoice_name = move.unescape_characters(move.name)
        delivery_folio = move.delivery_folio or 'N/A'
        delivery_date = move.date_delivery or move.invoice_date
        buyer_gln = move.partner_id.global_localitation_number or '0000000000000'
        buyer_contact = move.partner_id.person_order_department
        seller_gln = move.company_id.global_localitation_number or '0000000000000'
        supplier_id = move.partner_id.supplier_identification or move.company_id.vat or 'N/A'
        total_amount = move.get_total_amount()

        contact_xml = ''
        if buyer_contact:
            contact_text = move.unescape_characters(buyer_contact)
            contact_xml = f'''
                            <detallista:contactInformation>
                                <detallista:personOrDepartmentName>
                                    <detallista:text>{contact_text}</detallista:text>
                                </detallista:personOrDepartmentName>
                            </detallista:contactInformation>'''

        addenda_xml = f'''<detallista:detallista xmlns:detallista="http://www.sat.gob.mx/detallista" contentVersion="1.3.1" documentStructureVersion="AMC8.1" type="SimpleInvoiceType" documentStatus="ORIGINAL">
                    <detallista:requestForPaymentIdentification>
                        <detallista:entityType>{entity_type}</detallista:entityType>
                    </detallista:requestForPaymentIdentification>
                    <detallista:specialInstruction code="ZZZ">
                        <detallista:text>{amount_text}</detallista:text>
                    </detallista:specialInstruction>
                    <detallista:orderIdentification>
                        <detallista:referenceIdentification type="ON">{purchase_order}</detallista:referenceIdentification>
                    </detallista:orderIdentification>
                    <detallista:AdditionalInformation>
                        <detallista:referenceIdentification type="IV">{invoice_name}</detallista:referenceIdentification>
                    </detallista:AdditionalInformation>
                    <detallista:DeliveryNote>
                        <detallista:referenceIdentification>{delivery_folio}</detallista:referenceIdentification>
                        <detallista:ReferenceDate>{delivery_date}</detallista:ReferenceDate>
                    </detallista:DeliveryNote>
                    <detallista:buyer>
                        <detallista:gln>{buyer_gln}</detallista:gln>{contact_xml}
                    </detallista:buyer>
                    <detallista:seller>
                        <detallista:gln>{seller_gln}</detallista:gln>
                        <detallista:alternatePartyIdentification type="SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY">{supplier_id}</detallista:alternatePartyIdentification>
                    </detallista:seller>{line_items_xml}
                    <detallista:totalAmount>
                        <detallista:Amount>{total_amount}</detallista:Amount>
                    </detallista:totalAmount>
                    <detallista:TotalAllowanceCharge allowanceOrChargeType="ALLOWANCE">
                        <detallista:Amount>0.00</detallista:Amount>
                    </detallista:TotalAllowanceCharge>
                </detallista:detallista>'''

        return addenda_xml
