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
import os
import tempfile
import uuid
import logging
from lxml import etree
from datetime import datetime
import unidecode

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

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

    # def read(self, fields=None, load='_classic_read'):
    #     addenda_liverpool_id = self.env.ref('w_addenda_liverpool.addenda_liverpool').id
    #     for invoice in self:
    #         if invoice.partner_id.l10n_mx_edi_addenda.id == addenda_liverpool_id:
    #             invoice.require_addenda_liverpool = True
    #         else:
    #             invoice.require_addenda_liverpool = False
    #     return super(AccountMove, self).read(fields=fields, load=load)


    def unescape_characters(self, value):
        return unidecode.unidecode(value)
   
    def get_total_amount(self):
        return "%.2f" % round(self.amount_untaxed, 2)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def get_price_gross(self):
        taxes_line = self.tax_ids.flatten_taxes_hierarchy()
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
    
    def _l10n_mx_edi_prepare_tax_details_for_addenda(self):
        """Prepare tax details in the format expected by the Liverpool addenda template."""
        tax_details_transferred = {'invoice_line_tax_details': {}, 'tax_details': {}, 'tax_amount_currency': 0.0}
        tax_details_withholding = {'invoice_line_tax_details': {}, 'tax_details': {}, 'tax_amount_currency': 0.0}

        # Process each invoice line
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            line_tax_details_transferred = []
            line_tax_details_withholding = []

            # Get taxes for this line
            taxes = line.tax_ids.flatten_taxes_hierarchy()

            for tax in taxes:
                tax_amount = tax._compute_amount(line.price_subtotal, line.price_unit, line.quantity, line.product_id, self.partner_id)

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