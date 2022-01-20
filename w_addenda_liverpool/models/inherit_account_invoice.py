# -*- encoding: utf-8 -*-
#
# Module written to Odoo, Open Source Management Solution
#
# Copyright (c) 2017 Telematel - http://www.telematel.com/
# All Rights Reserved.
#
# Developer(s): Alan Guzmán
#               (age@wedoo.tech)
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
from odoo import _, api, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from lxml import etree
from lxml.objectify import fromstring
import base64
from datetime import datetime
from dateutil.relativedelta import relativedelta
import unidecode
from io import BytesIO
import logging


CFDI_TEMPLATE_33 = 'l10n_mx_edi.cfdiv33'
CFDI_XSLT_CADENA = 'l10n_mx_edi/data/%s/cadenaoriginal.xslt'
CFDI_XSLT_CADENA_TFD = 'l10n_mx_edi/data/xslt/3.3/cadenaoriginal_TFD_1_1.xslt'

_logger = logging.getLogger(__name__)

def create_list_html(array):
    '''Convert an array of string to a html list.
    :param array: A list of strings
    :return: an empty string if not array, an html list otherwise.
    '''
    if not array:
        return ''
    msg = ''
    for item in array:
        msg += '<li>' + item + '</li>'
    return '<ul>' + msg + '</ul>'


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
    use_addenda = fields.Boolean(
        compute='_get_addenda_from_partner'
    )

    def unescape_characters(self, value):
        return unidecode.unidecode(value)

    @api.depends('partner_id.l10n_mx_edi_addenda')
    def _get_addenda_from_partner(self):
        for move in self:
            # validate if the partner has addenda.
            if move.partner_id and move.partner_id.generate_addenda_liverpool:
                move.use_addenda = True
            else:
                move.use_addenda = False

    def get_total_amount(self):
        return round(self.amount_untaxed)

    def _l10n_mx_edi_create_cfdi(self):
        self.ensure_one()
        if not self.use_addenda:
            return super(AccountMove, self)._l10n_mx_edi_create_cfdi()
        else:
            qweb = self.env['ir.qweb']
            error_log = []
            company_id = self.company_id
            pac_name = company_id.l10n_mx_edi_pac
            if self.l10n_mx_edi_external_trade:
                # Call the onchange to obtain the values of l10n_mx_edi_qty_umt
                # and l10n_mx_edi_price_unit_umt, this is necessary when the
                # invoice is created from the sales order or from the picking
                self.invoice_line_ids.onchange_quantity()
                self.invoice_line_ids._set_price_unit_umt()
            values = self._l10n_mx_edi_create_cfdi_values()

            # -----------------------
            # Check the configuration
            # -----------------------
            # -Check certificate
            certificate_ids = company_id.l10n_mx_edi_certificate_ids
            certificate_id = certificate_ids.sudo().get_valid_certificate()
            if not certificate_id:
                error_log.append(_('No valid certificate found'))

            # -Check PAC
            if pac_name:
                pac_test_env = company_id.l10n_mx_edi_pac_test_env
                pac_password = company_id.l10n_mx_edi_pac_password
                if not pac_test_env and not pac_password:
                    error_log.append(_('No PAC credentials specified.'))
            else:
                error_log.append(_('No PAC specified.'))

            if error_log:
                return {'error': _(
                    'Please check your configuration: ') + create_list_html(
                        error_log)}

            # -Compute date and time of the invoice
            time_invoice = datetime.strptime(self.l10n_mx_edi_time_invoice,
                                            DEFAULT_SERVER_TIME_FORMAT).time()
            # -----------------------
            # Create the EDI document
            # -----------------------
            version = self.l10n_mx_edi_get_pac_version()

            # -Compute certificate data
            values['date'] = datetime.combine(
                fields.Datetime.from_string(
                    self.invoice_date), time_invoice).strftime('%Y-%m-%dT%H:%M:%S')
            values['certificate_number'] = certificate_id.serial_number
            values['certificate'] = certificate_id.sudo().get_data()[0]

            # -Compute cfdi
            cfdi = qweb.render(CFDI_TEMPLATE_33, values=values)
            cfdi = cfdi.replace(b'xmlns__', b'xmlns:')
            #Patch for Finkok specifications
            cfdi_str = cfdi.decode('utf-8')
            cfdi_str = cfdi_str.replace('xmlns:detallista="http://www.sat.gob.mx/detallista"','')
            cfdi_str = cfdi_str.replace('<cfdi:Comprobante','<cfdi:Comprobante xmlns:detallista="http://www.sat.gob.mx/detallista" ')
            cfdi = cfdi_str.encode('utf-8')
            #End patch
            node_sello = 'Sello'
            attachment = self.env.ref('l10n_mx_edi.xsd_cached_cfdv33_xsd', False)
            xsd_datas = base64.b64decode(attachment.datas) if attachment else b''
            # -Compute cadena
            tree = self.l10n_mx_edi_get_xml_etree(cfdi)
            cadena = self.l10n_mx_edi_generate_cadena(
                CFDI_XSLT_CADENA % version, tree)
            tree.attrib[node_sello] = certificate_id.sudo().get_encrypted_cadena(
                cadena)

            # Check with xsd
            if xsd_datas:
                try:
                    with BytesIO(xsd_datas) as xsd:
                        _check_with_xsd(tree, xsd)
                except (IOError, ValueError):
                    _logger.info(
                        _('The xsd file to validate the XML structure was not found'))
                except Exception as e:
                    return {'error': (
                        _('The cfdi generated is not valid') +
                                        create_list_html(str(e).split('\\n')))}
            return {'cfdi': etree.tostring(
                tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')}


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
        return round(price_gross, 2)

    def get_price_net(self):
        return round(self.price_unit * self.quantity, 2)

    def get_gross_amount(self):
        return round(self.price_total, 2)

    def get_net_amount(self):
        return round(self.price_subtotal, 2)
