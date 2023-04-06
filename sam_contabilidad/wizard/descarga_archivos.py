# -*- coding: utf-8 -*-

# descarga_archivos.py
# Descarga masiva de cfdi en xml y pdf.
# Descarga masiva de los xml y pdf de cfdi (facturas, notas de crédito, recibos de pago).
# VBueno 0510202110:13

import datetime
import logging
import requests

from odoo import models, fields, http
from odoo.exceptions import UserError
import io
from io import BytesIO
import base64
import os
import zipfile



# import mimetypes
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


    def descargaxml(self):
        if not self.facturas and not self.pagos and not self.notas_credito:
            raise UserError('Debes seleccionar un tipo de comprobante')

        if self.fecha_final < self.fecha_inicial:
            raise UserError('Rango de fechas erroneo')

        if self.facturas:
            #facturas
            archivos = self.env['account.move'].search_read([('invoice_date','>=',self.fecha_inicial),
                                                             ('invoice_date','<=',self.fecha_final),
                                                             ('l10n_mx_edi_cfdi_uuid','=',True)])

        if archivos:

            # Creamos una carpeta temporal para almacenar los archivos descargados
            carpeta_temporal = os.path.expanduser('~/Temp/Facturas')
            os.makedirs(carpeta_temporal, exist_ok=True)

            raise UserError('se creó la carpeta')

            for archivo in archivos:

                nombre_archivo = archivo.name

                # Descargamos el archivo XML
                archivo_xml = archivo.export_as_xml()
                if archivo_xml:
                    nombre_archivo_xml = f'{nombre_archivo}.xml'
                    ruta_archivo_xml = os.path.join(carpeta_temporal,
                                                    nombre_archivo_xml)
                    with open(ruta_archivo_xml, 'wb') as f:
                        f.write(base64.b64decode(archivo_xml))

                # Descargamos el archivo PDF
                archivo_pdf = archivo.get_report_data()[0]
                if archivo_pdf:
                    nombre_archivo_pdf = f'{nombre_archivo}.pdf'
                    ruta_archivo_pdf = os.path.join(carpeta_temporal,
                                                    nombre_archivo_pdf)
                    with open(ruta_archivo_pdf, 'wb') as f:
                        f.write(base64.b64decode(archivo_pdf))
