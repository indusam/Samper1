# -*- coding: utf-8 -*-

from odoo import models
from lxml import etree


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_export_invoice_cfdi(self, invoice):
        """Override to add detallista namespace to Comprobante when Liverpool addenda is required."""
        cfdi = super()._l10n_mx_edi_export_invoice_cfdi(invoice)
        
        # Only modify if Liverpool addenda is required
        if invoice.require_addenda_liverpool:
            try:
                # Parse the CFDI XML
                cfdi_node = etree.fromstring(cfdi)
                
                # Add detallista namespace to Comprobante
                cfdi_node.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                    'http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd '
                    'http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd')
                
                # Add detallista namespace declaration
                nsmap = cfdi_node.nsmap.copy()
                nsmap['detallista'] = 'http://www.sat.gob.mx/detallista'
                
                # Create new element with updated nsmap
                new_cfdi = etree.Element(cfdi_node.tag, nsmap=nsmap, attrib=cfdi_node.attrib)
                new_cfdi.text = cfdi_node.text
                new_cfdi.tail = cfdi_node.tail
                
                # Copy all children
                for child in cfdi_node:
                    new_cfdi.append(child)
                
                # Convert back to string
                cfdi = etree.tostring(new_cfdi, encoding='unicode')
            except Exception:
                # If anything fails, return original CFDI
                pass
        
        return cfdi
