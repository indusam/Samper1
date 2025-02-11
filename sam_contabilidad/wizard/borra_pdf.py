# -*- coding: utf-8 -*-

"""
Módulo: borra_pdf.py
Descripción: 
    Este módulo proporciona una funcionalidad en Odoo para eliminar archivos PDF 
    de los CFDI (Comprobantes Fiscales Digitales por Internet). Se eliminan los 
    archivos PDF asociados a facturas, notas de crédito y recibos de pago con 
    una fecha de creación anterior a una fecha de corte definida por el usuario.

Autor: VBueno
Fecha: 19/08/2021 - 12:04
"""

import datetime
import logging
import os

from odoo import models, fields, api
from odoo.exceptions import UserError

# Configuración del logger para registrar eventos y depuración
_logger = logging.getLogger(__name__)

class BorraPdf(models.TransientModel):
    """
    Modelo transitorio (wizard) para la eliminación de archivos PDF antiguos en Odoo.
    
    Permite seleccionar una fecha de corte y eliminar los archivos PDF almacenados 
    en el sistema de archivos del servidor que fueron creados antes de dicha fecha.
    """

    _name = 'borra_pdf.wizard'  # Nombre del modelo en Odoo
    _description = 'Borra PDF'  # Descripción del modelo

    # Fecha de corte predeterminada: hoy
    corte = fields.Date(
        string="Corte", 
        required=True, 
        default=lambda self: fields.Date.today()
    )

    def deletepdf(self):
        """
        Método que elimina los archivos PDF almacenados en el servidor si su 
        fecha de creación es anterior a la fecha de corte definida.
        
        Se eliminan los archivos PDF que cumplan con las siguientes condiciones:
        - Fueron creados antes de la fecha de corte seleccionada.
        - Su nombre contiene la extensión '.pdf'.
        
        Además, el método actualiza el campo `res_id` de los archivos eliminados
        para desvincularlos de los registros de Odoo.
        """

        # Buscar archivos PDF con fecha anterior a la fecha de corte
        archivos = self.env['ir.attachment'].search([
            ('create_date', '<=', self.corte),
            ('name', 'ilike', '.pdf')  # Filtra solo archivos PDF
        ])

        if not archivos:
            raise UserError("No se encontraron archivos PDF anteriores a la fecha de corte.")

        # Obtener la ruta base del almacenamiento de archivos en Odoo
        filestore_path = self.env['ir.config_parameter'].sudo().get_param('ir_attachment.location', '/home/odoo/data/filestore')

        raise UserError(filestore_path)

        archivos_eliminados = 0  # Contador de archivos eliminados

        for archivo in archivos:
            file_path = os.path.join(filestore_path, archivo.store_fname)  # Construir la ruta del archivo

            if os.path.exists(file_path):
                os.remove(file_path)  # Eliminar el archivo físico
                archivo.write({'res_id': 0})  # Desvincular de su registro en Odoo
                archivos_eliminados += 1

                # Log de depuración
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
