# -*- coding: utf-8 -*-

# descarga_archivos.py
# Descarga masiva de cfdi en xml y pdf.
# Descarga masiva de los xml y pdf de cfdi (facturas, notas de crédito, recibos de pago).
# VBueno 0510202110:13


import logging
import zipfile
import datetime
from io import BytesIO

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class DownloadInvoices(http.Controller):

    _name = 'descarga_xml_wizard'
    _description = 'Descarga XML'
    
    @http.route('/download_invoices', type='http', auth='user')
    def download_invoices(self, start_date=None, end_date=None, **kw):

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=31)

        if not start_date or not end_date:
            return "Debe especificar un rango de fechas válido."

        invoices = request.env['account.move'].search([
            ('type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
        ])

        if not invoices:
            return "No se encontraron facturas para el rango de fechas especificado."

        file_name = 'facturas_{}_{}.zip'.format(start_date, end_date)

        # Generar archivo zip
        zip_file = BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as my_zip:
            for invoice in invoices:
                file_data = invoice._get_report_from_name(
                    'account.report_invoice_with_payments')
                file_name = invoice.name.replace('/', '-') + '.pdf'
                my_zip.writestr(file_name, file_data[0])
        zip_file.seek(0)

        # Descargar archivo zip
        headers = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', 'attachment; filename=%s' % file_name),
            ('Content-Length', len(zip_file.getvalue())),
        ]

        return request.make_response(zip_file.getvalue(), headers=headers)

"""
import datetime
import requests                       
import zipfile                        
                                      
from odoo import models, fields, http 
from odoo.exceptions import UserError 
import base64                         
import io                             
import os                             
import mimetypes    
# from werkzeug.utils import redirect                     

class DescargaXml(models.TransientModel):
    _name = 'descarga_xml_wizard'
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
 
"""