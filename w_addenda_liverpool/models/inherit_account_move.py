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
from odoo import models, fields, api
from lxml import etree
from lxml.objectify import fromstring
import logging
import unidecode

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_mx_edi_cfdi_invoice_append_addenda(self, cfdi, addenda):
        """Override to add Liverpool addenda to CFDI."""
        _logger.warning('=' * 80)
        _logger.warning('w_addenda_liverpool: _l10n_mx_edi_cfdi_invoice_append_addenda called for invoice %s', self.name)
        _logger.warning('=' * 80)

        # Check if Liverpool addenda is required
        if not self.require_addenda_liverpool:
            _logger.warning('Liverpool addenda not required for this invoice')
            return super()._l10n_mx_edi_cfdi_invoice_append_addenda(cfdi, addenda)

        try:
            _logger.warning('Adding Liverpool addenda to CFDI')

            # Parse the CFDI XML
            cfdi_node = fromstring(cfdi)

            # Render the addenda template
            addenda_template = self.env.ref('w_addenda_liverpool.liverpool_addenda_appendix', raise_if_not_found=False)
            if not addenda_template:
                _logger.error('Liverpool addenda template not found')
                return cfdi

            addenda_values = {'record': self}
            addenda_str = addenda_template._render(values=addenda_values).strip()

            if not addenda_str:
                _logger.warning('Liverpool addenda template rendered empty')
                return cfdi

            # Parse the rendered addenda
            addenda_node = fromstring(addenda_str)

            # Find the Complemento element
            cfdi_ns = 'http://www.sat.gob.mx/cfd/4'
            complemento = cfdi_node.find('{%s}Complemento' % cfdi_ns)

            if complemento is None:
                _logger.info('Creating Complemento element')
                complemento = etree.SubElement(cfdi_node, '{%s}Complemento' % cfdi_ns)

            # Insert the addenda as the first child of Complemento (before TimbreFiscalDigital)
            complemento.insert(0, addenda_node)

            _logger.warning('Liverpool addenda added successfully')

            # Return as bytes with UTF-8 encoding
            return etree.tostring(cfdi_node, pretty_print=False, xml_declaration=True, encoding='UTF-8')

        except Exception as e:
            _logger.error('Error adding Liverpool addenda to CFDI: %s', str(e), exc_info=True)
            return cfdi

    purchase_order_liv =  fields.Char(
        string='Purchase order liverpool',
        help='If the invoice is for the liverpool customer, indicate the '
             'number of the purchase order.',
        copy=False
    )
    delivery_folio = fields.Char(
        string='Delivery folio',
        help='Specify the folio number. Number issued by the buyer when he '
             'receives the merchandise that is billed',
        copy=False
    )
    date_delivery = fields.Date(
        string='Date delivery',
        help='Specify the date the no was assigned. of receipt sheet',
        copy=False
    )
    require_addenda_liverpool = fields.Boolean(help="Field used to show or hide the fields create for the Liverpool addenda",
        string="Use Addenda Liverpool",
        compute='_compute_require_addenda_liverpool',
        store=True)

    @api.depends('partner_id', 'partner_id.generate_addenda_liverpool')
    def _compute_require_addenda_liverpool(self):
        for move in self:
            move.require_addenda_liverpool = move.partner_id.generate_addenda_liverpool

    def unescape_characters(self, value):
        return unidecode.unidecode(value)
   
    def get_total_amount(self):
        return "%.2f" % round(self.amount_untaxed, 2)
    
    def _l10n_mx_edi_cfdi_amount_to_text(self):
        """Convert the invoice amount to text in Spanish for Mexican localization."""
        self.ensure_one()
        # Try to use the standard Odoo method if it exists
        if hasattr(super(AccountMove, self), '_l10n_mx_edi_cfdi_amount_to_text'):
            return super()._l10n_mx_edi_cfdi_amount_to_text()
        
        # Otherwise, use the currency's amount_to_text method
        try:
            from odoo.addons.l10n_mx_edi.models.account_edi_format import CURRENCY_CODE_TO_NAME
            currency_name = CURRENCY_CODE_TO_NAME.get(self.currency_id.name, self.currency_id.name)
            amount_text = self.currency_id.with_context(lang='es_MX').amount_to_text(self.amount_total)
            return amount_text.upper()
        except:
            # Fallback: return empty string if conversion fails
            return ""


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def get_price_gross(self):
        # Get taxes for the line
        taxes_line = self.tax_ids
        # In v16, flatten_taxes_hierarchy is replaced by flatten_taxes_hierarchy or we use the taxes directly
        if hasattr(taxes_line, 'flatten_taxes_hierarchy'):
            taxes_line = taxes_line.flatten_taxes_hierarchy()
        transferred = taxes_line.filtered(lambda r: r.amount >= 0)
        price_net =  self.price_unit * self.quantity
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