# -*- coding: utf-8 -*-

from odoo import models
from lxml import etree
import logging

_logger = logging.getLogger(__name__)


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_export_invoice_cfdi(self, invoice):
        """Override to add detallista namespace to Comprobante when Liverpool addenda is required."""
        cfdi = super()._l10n_mx_edi_export_invoice_cfdi(invoice)
        
        # Only modify if Liverpool addenda is required
        if invoice.require_addenda_liverpool:
            try:
                # Parse the CFDI XML
                cfdi_node = etree.fromstring(cfdi.encode('utf-8'))
                
                # Get current schema location
                xsi_ns = 'http://www.w3.org/2001/XMLSchema-instance'
                schema_loc_key = '{%s}schemaLocation' % xsi_ns
                current_schema = cfdi_node.get(schema_loc_key, '')
                
                # Add detallista schema if not already present
                if 'detallista' not in current_schema:
                    new_schema = current_schema.strip() + ' http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd'
                    cfdi_node.set(schema_loc_key, new_schema.strip())
                
                # Register detallista namespace if not already present
                if 'detallista' not in cfdi_node.nsmap:
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
                
                # Convert back to string with proper encoding
                cfdi = etree.tostring(cfdi_node, encoding='unicode', pretty_print=False)
                
            except Exception as e:
                _logger.error('Error adding detallista namespace to CFDI: %s', str(e))
        
        return cfdi
