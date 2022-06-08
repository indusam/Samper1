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
        default=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        addenda_liverpool_id = self.env.ref('w_addenda_liverpool.addenda_liverpool').id
        for move in self:
            if move.partner_id.l10n_mx_edi_addenda.id == addenda_liverpool_id or move.partner_id.commercial_partner_id.l10n_mx_edi_addenda.id == addenda_liverpool_id:
                move.require_addenda_liverpool = True
            else: 
                move.require_addenda_liverpool = False
        return super(AccountMove, self)._onchange_partner_id()

    def read(self, fields=None, load='_classic_read'):   
        addenda_liverpool_id = self.env.ref('w_addenda_liverpool.addenda_liverpool').id
        for invoice in self: 
            if invoice.partner_id.l10n_mx_edi_addenda.id == addenda_liverpool_id:
                invoice.require_addenda_liverpool = True
            else:
                invoice.require_addenda_liverpool = False
        return super(AccountMove, self).read(fields=fields, load=load)


    def unescape_characters(self, value):
        return unidecode.unidecode(value)
   
    def get_total_amount(self):
        return "%.2f" % round(self.amount_untaxed, 2)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def get_price_gross(self):
        taxes_line = self.filtered('price_subtotal').tax_ids.flatten_taxes_hierarchy()
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