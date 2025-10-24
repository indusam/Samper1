# -*- coding: utf-8 -*-

"""
Módulo: borra_pdf.py
Descripción:
    Este módulo proporciona una funcionalidad en Odoo v18 para eliminar archivos PDF
    de los CFDI (Comprobantes Fiscales Digitales por Internet). Se eliminan los
    archivos PDF asociados a facturas, notas de crédito y recibos de pago con
    una fecha de creación anterior a una fecha de corte definida por el usuario.

Autor: VBueno
Fecha: 19/08/2021 - 12:04 - 2606202510:53
Actualizado para v18: 2025
"""

import logging

from odoo import models, fields
from odoo.exceptions import UserError

# Configuración del logger para registrar eventos y depuración
_logger = logging.getLogger(__name__)

class BorraPdf(models.TransientModel):
    """
    Modelo transitorio (wizard) para la eliminación de archivos PDF antiguos en Odoo v18.

    Permite seleccionar una fecha de corte y eliminar los archivos PDF almacenados
    en el sistema mediante la API de Odoo, respetando los mecanismos de seguridad.
    """

    _name = 'borra_pdf.wizard'  # Nombre del modelo en Odoo
    _description = 'Wizard para Borrar PDFs Antiguos'  # Descripción del modelo

    # Fecha de corte predeterminada: hoy
    corte = fields.Date(
        string="Fecha de Corte",
        required=True,
        default=lambda self: fields.Date.today(),
        help="Los archivos PDF creados antes de esta fecha serán eliminados"
    )

    def deletepdf(self):
        """
        Método que elimina los archivos PDF almacenados en el servidor si su
        fecha de creación es anterior a la fecha de corte definida.

        En Odoo v18, se utiliza la API nativa de eliminación de adjuntos
        para garantizar la integridad y seguridad del sistema.

        Se eliminan los archivos PDF que cumplan con las siguientes condiciones:
        - Fueron creados antes de la fecha de corte seleccionada.
        - Su nombre contiene la extensión '.pdf'.

        :return: Notificación del resultado de la operación
        """
        self.ensure_one()

        # Buscar archivos PDF con fecha anterior a la fecha de corte
        archivos = self.env['ir.attachment'].search([
            ('create_date', '<=', self.corte),
            ('name', 'ilike', '.pdf')  # Filtra solo archivos PDF
        ])

        if not archivos:
            raise UserError("No se encontraron archivos PDF anteriores a la fecha de corte.")

        # Contar archivos antes de eliminar
        archivos_eliminados = len(archivos)

        # Log de depuración antes de eliminar
        _logger.info(f"Iniciando eliminación de {archivos_eliminados} archivos PDF anteriores a {self.corte}")

        # Eliminar archivos usando el método unlink() que maneja tanto el registro
        # de la base de datos como el archivo físico de manera segura
        try:
            for archivo in archivos:
                _logger.info(f"Eliminando archivo: {archivo.name} (ID: {archivo.id})")

            archivos.unlink()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Proceso completado',
                    'message': f'Se eliminaron {archivos_eliminados} archivos PDF.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error(f"Error al eliminar archivos PDF: {str(e)}")
            raise UserError(f"Error al eliminar archivos: {str(e)}")
