# -*- coding: utf-8 -*-

# descarga_archivos.py
# Descarga masiva de cfdi en xml y pdf.
# Descarga masiva de los xml y pdf de cfdi (facturas, notas de crédito, recibos de pago).
# VBueno 0510202110:13

import datetime
import logging
import requests
import zipfile

from odoo import models, fields, http
from odoo.exceptions import UserError
import base64
import io
import os
import mimetypes
# from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class DescargaXml(models.TransientModel):
    _name = 'descarga_xml.wizard'
    _description = 'Descarga XML'

    dfinal = datetime.date.today()
    dinicial = dfinal - datetime.timedelta(days=31)
    facturas = fields.Boolean(string="Facturas", default=True )
    notas_credito = fields.Boolean(string="Notas de crédito", default=True )
    pagos = fields.Boolean(string="CFDI de pago", default=True )
    marca = fields.Char(string="Marca", required=False, )
    fecha_inicial = fields.Date(string="Fecha inicial", required=True, default=dinicial)
    fecha_final = fields.Date(string="Fecha final", required=True, default=dfinal)


    def dl(self,archivo):

        action = {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(
                archivo.id) + "&filename_field=name&field=datas&download=true&name=" + archivo.name,
            'target': 'self'
        }

        return action


    # Descarga los xml
    def descargaxml(self):

        if not self.facturas and not self.pagos and not self.notas_credito:
            raise UserError('Debes seleccionar un tipo de comprobante')

        if self.facturas:
          cfdis = self.env['ir.attachment'].search([('res_model','=','account.move'),
                                                       ('name','not ilike','RINV'),
                                                       ('mimetype','=','text/plain'),
                                                       ('create_date','>=',self.fecha_inicial),
                                                       ('create_date','<=',self.fecha_final)])

          if not cfdis:
              raise UserError('No hay registros en ese rango de fechas')

          for cfdi in cfdis:
              descarga = self.dl(cfdi)

    # escribe una funcion para crear un archivo zip
    # con los archivos de un directorio

    def crear_zip(directorio, archivo):
        import zipfile
        import os
        # crear el archivo zip
        zip = zipfile.ZipFile(archivo,'w')
        # recorrer el directorio
        for raiz, dirs, files in os.walk(directorio):
            # recorrer los archivos
            for file in files:
                # agregar el archivo al zip
                zip.write(os.path.join(raiz, file))
                # cerrar el archivo zip
                zip.close()

    # escribe una funcion para descargar el archivo zip
    # de una URL

    def descargar_zip(url, archivo):
        import urllib.request
        # descargar el archivo
        with urllib.request.urlopen(url) as response, open(archivo, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
