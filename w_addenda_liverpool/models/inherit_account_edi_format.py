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
from odoo import models, api
import logging
from lxml import etree
from lxml.objectify import fromstring

_logger = logging.getLogger(__name__)


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_cfdi_append_addenda(self, move, cfdi, addenda):
        ''' Append an additional block to the signed CFDI passed as parameter.
        :param move:    The account.move record.
        :param cfdi:    The invoice's CFDI as a string.
        :param addenda: The addenda to add as a string.
        :return cfdi:   The cfdi including the addenda.
        '''
        cfdi_node = fromstring(cfdi)
        if addenda and addenda.id == self.env.ref('w_addenda_liverpool.addenda_liverpool').id:
            # Prepare tax details for Liverpool addenda
            tax_details_transferred, tax_details_withholding = self._l10n_mx_edi_prepare_tax_details_for_addenda(move)

            addenda_values = {
                'record': move,
                'cfdi': cfdi,
                'liverpool_tax_details_transferred': tax_details_transferred,
                'liverpool_tax_details_withholding': tax_details_withholding,
            }
            addenda_content = addenda.with_context(addenda_context=True)._render(values=addenda_values).strip()
            if not addenda_content:
                return cfdi
            addenda_node = fromstring(addenda_content)
            # Add a root node Addenda if not specified explicitly by the user.
            if addenda_node.tag != '{http://www.sat.gob.mx/cfd/4}Addenda':
                node = etree.Element(etree.QName('http://www.sat.gob.mx/cfd/4', 'Addenda'))
                node.append(addenda_node)
                addenda_node = node
            cfdi_node.append(addenda_node)
            return etree.tostring(cfdi_node, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        else:
            return super(AccountEdiFormat, self)._l10n_mx_edi_cfdi_append_addenda(
                move, cfdi, addenda)

    def _l10n_mx_edi_prepare_tax_details_for_addenda(self, move):
        """Prepare tax details in the format expected by the Liverpool addenda template."""
        tax_details_transferred = {'invoice_line_tax_details': {}, 'tax_details': {}, 'tax_amount_currency': 0.0}
        tax_details_withholding = {'invoice_line_tax_details': {}, 'tax_details': {}, 'tax_amount_currency': 0.0}

        # Process each invoice line
        for line in move.invoice_line_ids.filtered(lambda l: not l.display_type):
            line_tax_details_transferred = []
            line_tax_details_withholding = []

            # Get taxes for this line
            taxes = line.tax_ids.flatten_taxes_hierarchy()

            for tax in taxes:
                tax_amount = tax._compute_amount(line.price_subtotal, line.price_unit, line.quantity, line.product_id, move.partner_id)

                tax_detail = {
                    'tax': tax,
                    'base_amount_currency': line.price_subtotal,
                    'tax_amount_currency': abs(tax_amount),
                    'tax_rate_transferred': abs(tax.amount / 100.0) if tax.amount_type == 'percent' else 0.0,
                }

                if tax.amount >= 0:  # Transferred taxes (IVA, etc.)
                    line_tax_details_transferred.append(tax_detail)
                    tax_details_transferred['tax_amount_currency'] += tax_detail['tax_amount_currency']
                else:  # Withholding taxes (ISR, etc.)
                    tax_detail['tax_rate_transferred'] = abs(tax.amount / 100.0)
                    line_tax_details_withholding.append(tax_detail)
                    tax_details_withholding['tax_amount_currency'] += tax_detail['tax_amount_currency']

            tax_details_transferred['invoice_line_tax_details'][line] = {
                'tax_details': {i: detail for i, detail in enumerate(line_tax_details_transferred)},
                'base_amount_currency': line.price_subtotal,
                'tax_amount_currency': sum(d['tax_amount_currency'] for d in line_tax_details_transferred),
            }

            tax_details_withholding['invoice_line_tax_details'][line] = {
                'tax_details': {i: detail for i, detail in enumerate(line_tax_details_withholding)},
                'base_amount_currency': line.price_subtotal,
                'tax_amount_currency': sum(d['tax_amount_currency'] for d in line_tax_details_withholding),
            }

        return tax_details_transferred, tax_details_withholding