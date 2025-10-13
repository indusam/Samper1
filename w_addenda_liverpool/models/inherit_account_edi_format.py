# -*- encoding: utf-8 -*-
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
            addenda_values = {'record': move, 'cfdi': cfdi}
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

    def _l10n_mx_edi_prepare_tax_details_for_template(self, move):
        """Prepare tax details for template context."""
        if not move.require_addenda_liverpool:
            return {}

        tax_details_transferred, tax_details_withholding = move._l10n_mx_edi_prepare_tax_details_for_addenda()

        return {
            'tax_details_transferred': tax_details_transferred,
            'tax_details_withholding': tax_details_withholding,
        }