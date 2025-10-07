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
        if addenda.id == self.env.ref('w_addenda_liverpool.addenda_liverpool').id:
            addenda_values = {'record': move, 'cfdi': cfdi}
            addenda = addenda._render(values=addenda_values).strip()
            if not addenda:
                return cfdi
            addenda_node = fromstring(addenda)
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