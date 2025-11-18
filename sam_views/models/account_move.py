# -*- coding: utf-8 -*-

from odoo import api, fields, models
from lxml import etree
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    x_cfdi_sello_emisor = fields.Text(
        string="Sello Digital Emisor",
        compute='_compute_cfdi_sellos',
        store=True,
        help="Sello digital del emisor extraído del XML del CFDI"
    )

    x_cfdi_sello_sat = fields.Text(
        string="Sello Digital SAT",
        compute='_compute_cfdi_sellos',
        store=True,
        help="Sello digital del SAT extraído del XML del CFDI"
    )

    x_cfdi_certificado_emisor = fields.Char(
        string="Certificado Emisor",
        compute='_compute_cfdi_sellos',
        store=True,
        help="Número de certificado del emisor"
    )

    x_cfdi_certificado_sat = fields.Char(
        string="Certificado SAT",
        compute='_compute_cfdi_sellos',
        store=True,
        help="Número de certificado del SAT"
    )

    x_cfdi_fecha_certificacion = fields.Char(
        string="Fecha Certificación",
        compute='_compute_cfdi_sellos',
        store=True,
        help="Fecha de certificación del CFDI"
    )

    @api.depends('l10n_mx_edi_cfdi_uuid')
    def _compute_cfdi_sellos(self):
        """
        Extrae información de los sellos digitales del XML del CFDI adjunto.
        """
        for move in self:
            # Valores por defecto
            move.x_cfdi_sello_emisor = False
            move.x_cfdi_sello_sat = False
            move.x_cfdi_certificado_emisor = False
            move.x_cfdi_certificado_sat = False
            move.x_cfdi_fecha_certificacion = False

            # Solo procesar si hay UUID (factura timbrada)
            if not move.l10n_mx_edi_cfdi_uuid:
                continue

            try:
                # Buscar el archivo XML del CFDI en los attachments
                cfdi_attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'account.move'),
                    ('res_id', '=', move.id),
                    ('name', 'ilike', '.xml'),
                    '|',
                    ('name', 'ilike', move.name),
                    ('name', 'ilike', 'MX-Invoice')
                ], limit=1)

                if not cfdi_attachment:
                    _logger.warning(
                        'No se encontró XML del CFDI para la factura %s',
                        move.name
                    )
                    continue

                # Leer y parsear el XML
                xml_content = cfdi_attachment.raw
                if not xml_content:
                    xml_content = cfdi_attachment.datas
                    if xml_content:
                        import base64
                        xml_content = base64.b64decode(xml_content)

                if not xml_content:
                    continue

                # Parsear el XML
                root = etree.fromstring(xml_content)

                # Namespaces del CFDI 4.0
                namespaces = {
                    'cfdi': 'http://www.sat.gob.mx/cfd/4',
                    'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
                }

                # Extraer Sello del emisor (atributo Sello del elemento Comprobante)
                sello_emisor = root.get('Sello')
                if sello_emisor:
                    move.x_cfdi_sello_emisor = sello_emisor

                # Extraer Certificado del emisor
                certificado_emisor = root.get('NoCertificado')
                if certificado_emisor:
                    move.x_cfdi_certificado_emisor = certificado_emisor

                # Buscar el complemento TimbreFiscalDigital
                complemento = root.find('.//cfdi:Complemento', namespaces)
                if complemento is not None:
                    tfd = complemento.find('.//tfd:TimbreFiscalDigital', namespaces)

                    if tfd is not None:
                        # Extraer Sello del SAT
                        sello_sat = tfd.get('SelloSAT')
                        if sello_sat:
                            move.x_cfdi_sello_sat = sello_sat

                        # Extraer Certificado del SAT
                        cert_sat = tfd.get('NoCertificadoSAT')
                        if cert_sat:
                            move.x_cfdi_certificado_sat = cert_sat

                        # Extraer Fecha de Certificación
                        fecha_cert = tfd.get('FechaTimbrado')
                        if fecha_cert:
                            move.x_cfdi_fecha_certificacion = fecha_cert

            except Exception as e:
                _logger.error(
                    'Error al extraer sellos del CFDI para factura %s: %s',
                    move.name,
                    str(e)
                )
                continue
