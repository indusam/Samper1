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
from odoo import models, fields, api, _
import base64
from lxml.objectify import fromstring
from lxml import etree
import unidecode
from datetime import timedelta

ENCODING='<?xml version="1.0" encoding="UTF-8"?>'



class AccountMove(models.Model):
    _inherit = 'account.move'

    mexican_commercial_addenda = fields.Boolean(
        compute='_get_addenda_from_partner'
    )
    amount_letters = fields.Char(
        string="Amount in letters",
        compute="_compute_amount_in_letters"
    )
    order_id = fields.Many2one(
        'sale.order',
        compute="_get_order_id",
        string="Sale order"
    )
    generate_mexican_commercial_addenda = fields.Boolean(
        related="partner_id.generate_mexican_commercial_addenda")

    @api.depends('partner_id.l10n_mx_edi_addenda')
    def _get_addenda_from_partner(self):
        for move in self:
            # validate if the partner has addenda.
            if move.partner_id and move.partner_id.generate_mexican_commercial_addenda:
                move.mexican_commercial_addenda = True
            else:
                move.mexican_commercial_addenda = False
                
    def geting_contact_person(self):
        for invoice in self:
            contact_name = False
            try:
                contact_id = invoice.partner_id.child_ids.filtered(
                    lambda x: x.type == 'contact')[0]
                contact_name = contact_id.name
            except Exception as e:
                print(e)
            return contact_name

    def getting_delivery_date(self):
        for invoice in self:
            commitment_date = False
            try:
                sale_line_id = invoice.invoice_line_ids.mapped('sale_line_ids')[0]
                commitment_date = sale_line_id.order_id.commitment_date.date()
            except Exception as e:
                print(e)
            return commitment_date

    def getting_days_of_payment(self):
        for invoice in self:
            invoice_date = invoice.invoice_date or fields.Date.today()
            days = invoice.invoice_date_due - invoice_date
            return days.days

    def unescape_characters(self, value):
        return unidecode.unidecode(value)

    def _get_order_id(self):
        for move in self:
            order_id = self.env['sale.order'].search([('invoice_ids','in', [move.id])], limit=1)
            move.order_id = order_id.id

    @api.depends('amount_total')
    def _compute_amount_in_letters(self):
        for move in self:
            move.amount_letters = move._l10n_mx_edi_cfdi_amount_to_text()

    @api.depends('currency_id', 'company_currency_id')
    def get_rate(self):
        for move in self:
            if move.currency_id == move.company_currency_id:
                return 1.00
            else:
                return "%.2f" % round(move.currency_id.rate, 2)

    def get_percent(self):
        price_sub = 0
        for r in self.invoice_line_ids:
            price_sub += r.price_subtotal
        if self.amount_untaxed:
            return "%.2f" % round((self.amount_residual - price_sub) * 100 / self.amount_untaxed, 2)
        return 0

    def get_taxes_aux(self):
        price_sub = 0
        for r in self.invoice_line_ids:
            price_sub += r.price_subtotal
        return "%.2f" % (self.amount_residual - price_sub)
        
    
    def get_sequence(self):
        for move in self:
            try:
                sequence, folio = move.name.split('/', 1)
            except Exception as e:
                return move.name, move.name
            return sequence, folio
    
    def get_rate(self):
        ctx = dict(company_id=self.company_id.id, date=self.invoice_date)
        mxn = self.env.ref('base.MXN').with_context(ctx)
        invoice_currency = self.currency_id.with_context(ctx)
        if self.currency_id.id != self.env.ref('base.MXN').id:
            return ('%.2f' % (
                invoice_currency._convert(1, mxn, self.company_id,
                                      self.invoice_date or fields.Date.today(),
                                      round=False))) if self.currency_id.name \
                                                        != 'MXN' else False
        else:
            return 1.0


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_price_gross(self):
        taxes_line = self.filtered(
            'price_subtotal').tax_ids.flatten_taxes_hierarchy()
        transferred = taxes_line.filtered(lambda r: r.amount >= 0)
        price_net = self.price_unit * self.quantity
        price_gross = price_net
        if transferred:
            for tax in transferred:
                tasa = abs(tax.amount if tax.amount_type == 'fixed' else (
                            tax.amount / 100.0)) * 100
                price_gross += (price_net * tasa / 100)
        return "%.2f" % round(price_gross, 2)

    def get_price_net(self):
        return "%.2f" % round(self.price_unit * self.quantity, 2)

    def get_gross_amount(self):
        return "%.2f" % round(self.price_total, 2)

    def get_net_amount(self):
        return "%.2f" % round(self.price_subtotal, 2)

    def get_tax(self, tax):
        return "%.2f" % round((self.price_subtotal * (tax / 100)), 2)

    def get_quantity(self):
        return "%.2f" % round(self.quantity, 2)
    

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'
    
    @api.model
    def _l10n_mx_edi_cfdi_append_addenda(self, move, cfdi, addenda):
        ''' Append an additional block to the signed CFDI passed as parameter.
        :param move:    The account.move record.
        :param cfdi:    The invoice's CFDI as a string.
        :param addenda: The addenda to add as a string.
        :return cfdi:   The cfdi including the addenda.
        '''
        cfdi_node = fromstring(cfdi)
        if addenda.id == self.env.ref('addenda_comercial_mexicana.mexican_commercial_addenda').id:
            addenda_values = {'record': move, 'cfdi': cfdi}
            addenda = addenda._render(values=addenda_values).strip()
            if not addenda:
                return cfdi
            addenda_node = fromstring(addenda)
            # Add a root node Addenda if not specified explicitly by the user.
            if addenda_node.tag != '{http://www.sat.gob.mx/cfd/3}Addenda':
                node = etree.Element(etree.QName('http://www.sat.gob.mx/cfd/3', 'Addenda'))
                node.append(addenda_node)
                addenda_node = node
            cfdi_node.append(addenda_node)
            return etree.tostring(cfdi_node, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        else:
            return super(AccountMove, self)._l10n_mx_edi_cfdi_append_addenda(
                move, cfdi, addenda)