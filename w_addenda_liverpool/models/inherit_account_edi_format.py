# -*- coding: utf-8 -*-

from odoo import models, api
from lxml import etree
from lxml.objectify import fromstring
import logging

_logger = logging.getLogger(__name__)


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_export_invoice_cfdi(self, invoice):
        """Override to add detallista namespace to CFDI when Liverpool addenda is required."""
        # Get the CFDI from parent method - this returns a dict with 'cfdi_str' and 'errors'
        res = super()._l10n_mx_edi_export_invoice_cfdi(invoice)

        _logger.info('Export CFDI for invoice %s, require_addenda_liverpool: %s', invoice.name, invoice.require_addenda_liverpool)

        # Only modify if Liverpool addenda is required and CFDI was generated successfully
        if invoice.require_addenda_liverpool and res.get('cfdi_str'):
            try:
                _logger.info('Adding detallista namespace to CFDI for invoice %s', invoice.name)

                # Parse the CFDI XML - cfdi_str is already bytes
                cfdi_node = etree.fromstring(res['cfdi_str'])

                _logger.info('Current nsmap: %s', cfdi_node.nsmap)

                # Get current schema location
                xsi_ns = 'http://www.w3.org/2001/XMLSchema-instance'
                schema_loc_key = '{%s}schemaLocation' % xsi_ns
                current_schema = cfdi_node.get(schema_loc_key, '')

                _logger.info('Current schema location: %s', current_schema)

                # Register detallista namespace if not already present
                if 'detallista' not in cfdi_node.nsmap:
                    _logger.info('Adding detallista namespace to nsmap')

                    # We need to recreate the element with the new namespace
                    nsmap = dict(cfdi_node.nsmap)
                    nsmap['detallista'] = 'http://www.sat.gob.mx/detallista'

                    # Create new root with updated namespace map
                    new_root = etree.Element(cfdi_node.tag, nsmap=nsmap)

                    # Copy all attributes
                    for key, value in cfdi_node.attrib.items():
                        new_root.set(key, value)

                    # Copy text
                    new_root.text = cfdi_node.text
                    new_root.tail = cfdi_node.tail

                    # Copy all children
                    for child in cfdi_node:
                        new_root.append(child)

                    cfdi_node = new_root
                    _logger.info('New nsmap: %s', cfdi_node.nsmap)

                # Add detallista schema if not already present
                if 'detallista' not in current_schema:
                    _logger.info('Adding detallista to schema location')
                    new_schema = current_schema.strip() + ' http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd'
                    cfdi_node.set(schema_loc_key, new_schema.strip())
                    _logger.info('New schema location: %s', cfdi_node.get(schema_loc_key))

                # Convert back to bytes - PAC expects bytes, not string
                res['cfdi_str'] = etree.tostring(cfdi_node, encoding='utf-8', pretty_print=False)
                _logger.info('CFDI updated successfully')

            except Exception as e:
                _logger.error('Error adding detallista namespace to CFDI for invoice %s: %s', invoice.name, str(e), exc_info=True)

        return res

    @api.model
    def _l10n_mx_edi_cfdi_append_addenda(self, move, cfdi, addenda):
        """Append Liverpool addenda to the CFDI Complemento section.

        This method is called by Odoo's EDI system to add custom addendas to the CFDI.
        The addenda is inserted into the Complemento element, before the TimbreFiscalDigital.

        :param move:    The account.move record
        :param cfdi:    The invoice's CFDI as bytes
        :param addenda: The addenda template (ir.ui.view record)
        :return cfdi:   The cfdi including the addenda as bytes
        """
        # Check if this is the Liverpool addenda template
        liverpool_addenda_ref = self.env.ref('w_addenda_liverpool.liverpool_addenda_appendix', raise_if_not_found=False)

        if not liverpool_addenda_ref or addenda.id != liverpool_addenda_ref.id:
            # Not Liverpool addenda, call parent method
            return super()._l10n_mx_edi_cfdi_append_addenda(move, cfdi, addenda)

        if not move.require_addenda_liverpool:
            # Liverpool addenda not required for this invoice
            return cfdi

        try:
            _logger.info('Adding Liverpool addenda to CFDI for invoice %s', move.name)

            # Parse the CFDI XML
            cfdi_node = fromstring(cfdi)

            # Render the addenda template
            addenda_values = {'record': move}
            addenda_str = addenda._render(values=addenda_values).strip()

            if not addenda_str:
                _logger.warning('Liverpool addenda template rendered empty for invoice %s', move.name)
                return cfdi

            # Parse the rendered addenda
            addenda_node = fromstring(addenda_str)

            # Find the Complemento element
            cfdi_ns = 'http://www.sat.gob.mx/cfd/4'
            complemento = cfdi_node.find('{%s}Complemento' % cfdi_ns)

            if complemento is None:
                # Create Complemento if it doesn't exist
                _logger.info('Creating Complemento element for invoice %s', move.name)
                complemento = etree.SubElement(cfdi_node, '{%s}Complemento' % cfdi_ns)

            # Insert the addenda as the first child of Complemento (before TimbreFiscalDigital)
            complemento.insert(0, addenda_node)

            _logger.info('Liverpool addenda added successfully to invoice %s', move.name)

            # Return as bytes with UTF-8 encoding
            return etree.tostring(cfdi_node, pretty_print=False, xml_declaration=True, encoding='UTF-8')

        except Exception as e:
            _logger.error('Error adding Liverpool addenda to CFDI for invoice %s: %s', move.name, str(e), exc_info=True)
            return cfdi
