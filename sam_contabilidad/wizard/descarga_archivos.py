# -*- coding: utf-8 -*-

# descarga_archivos.py
# Descarga masiva de cfdi en xml y pdf.
# Descarga masiva de los xml y pdf de cfdi (facturas, notas de crédito, recibos de pago).
# VBueno 0510202110:13

import datetime
import logging
import zipfile

from odoo import models, fields, http
from odoo.exceptions import UserError
import io
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from odoo import http
from odoo.http import request

import requests
import tempfile
import base64
from io import BytesIO
import mimetypes
# from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class DescargaXml(models.TransientModel):
    _name = 'descarga_xml_wizard'
    _description = 'Descarga XML'

    dfinal = datetime.date.today()
    dinicial = dfinal - datetime.timedelta(days=31)
    facturas = fields.Boolean(string="Facturas", default=True )
    notas_credito = fields.Boolean(string="Notas de crédito", default=True )
    pagos = fields.Boolean(string="CFDI de pago", default=True )
    fecha_inicial = fields.Date(string="Fecha inicial", required=True, default=dinicial)
    fecha_final = fields.Date(string="Fecha final", required=True, default=dfinal)


    # Descarga los xml
    def descargaxml(self):

        if not self.facturas and not self.pagos and not self.notas_credito:
            raise UserError('Debes seleccionar un tipo de comprobante')

        cfdis = self.env['ir.attachment'].search([('res_model','=','account.move'),
                                                    ('name','not ilike','RINV'),
                                                    ('mimetype','=','text/plain'),
                                                    ('create_date','>=',self.fecha_inicial),
                                                    ('create_date','<=',self.fecha_final)])

        if not cfdis:
            raise UserError('No hay registros en ese rango de fechas')

        # Crea un buffer para guardar los archivos en la memoria.
        zip_buffer = io.BytesIO()

        # Crea el archivo Zip en la memoria
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED,
                             False) as zip_file:
            for attachment in cfdis:
                zip_file.writestr(attachment.name, attachment.datas)

        # Fija la posición del buffer al principio para poder leerlo
        zip_buffer.seek(0)

        # Genera el nombre del archivo basado en la fecha y hora
        current_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        file_name = f'attachments_{current_date_time}.zip'

        # Obtiene el directorio home del usuario y crea la carpeta "descarga_archivos" si no existe.
        home_dir = os.path.expanduser('~')
        download_dir = os.path.join(home_dir, 'descarga_archivos')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Construye el directorio del archivo y escribe el Zip en el disco.
        file_path = os.path.join(download_dir, file_name)
        with open(file_path, 'wb') as f:
                f.write(zip_buffer.read())

        # Muestra un diálogo de guardado para que el usuario elija dónde guardar el archivo ZIP
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix('.zip')
        file_path, _ = file_dialog.getSaveFileName(
            None, 'Guardar archivo', 'attachments.zip',
                  'Archivos ZIP (*.zip)')
        if file_path:
            # Escribe el archivo ZIP en el disco
            with open(file_path, 'wb') as f:
                    f.write(zip_buffer.getvalue())

            # Muestra un mensaje de éxito
            #QMessageBox.information(None, 'Descarga completa',
            #                          f'Se descargó el archivo ZIP en {file_path}')

        # Regresa el archivo al usuario
        #return {
        #        'type': 'ir.actions.act_url',
        #        'url': f'https://{file_path + "&download=true"}',
        #        'target': 'self',
        #        }
