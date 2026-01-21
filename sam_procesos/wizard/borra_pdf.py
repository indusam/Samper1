# -*- coding: utf-8 -*-
"""
Módulo: borra_pdf.py
Descripción:
    Este módulo proporciona una funcionalidad en Odoo para eliminar archivos PDF
    de los CFDI (Comprobantes Fiscales Digitales por Internet). Se eliminan los
    archivos PDF asociados a facturas, notas de crédito y recibos de pago con
    una fecha de creación anterior a una fecha de corte definida por el usuario.

Autor: VBueno
Fecha: 19/08/2021
"""

import logging
import os

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BorraPdf(models.TransientModel):
    """
    Modelo transitorio (wizard) para la eliminación de archivos PDF antiguos en Odoo.
    """

    _name = 'borra_pdf.wizard'
    _description = 'Borra PDF'

    corte = fields.Date(
        string="Corte",
        required=True,
        default=lambda self: fields.Date.today()
    )

    def deletepdf(self):
        """
        Método que elimina los archivos PDF almacenados en el servidor si su
        fecha de creación es anterior a la fecha de corte definida.
        """
        archivos = self.env['ir.attachment'].search([
            ('create_date', '<=', self.corte),
            ('name', 'ilike', '.pdf')
        ])

        if not archivos:
            raise UserError("No se encontraron archivos PDF anteriores a la fecha de corte.")

        filestore_path = self.env['ir.config_parameter'].sudo().get_param(
            'ir_attachment.location', '/home/odoo/data/filestore'
        )

        archivos_eliminados = 0

        for archivo in archivos:
            file_path = os.path.join(filestore_path, archivo.store_fname or '')

            if archivo.store_fname and os.path.exists(file_path):
                os.remove(file_path)
                archivo.write({'res_id': 0})
                archivos_eliminados += 1
                _logger.info(f"Archivo eliminado: {archivo.name} ({file_path})")

        if archivos_eliminados > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Proceso completado',
                    'message': f'Se eliminaron {archivos_eliminados} archivos PDF.',
                    'sticky': False,
                }
            }
