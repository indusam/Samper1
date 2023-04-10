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
    _name = 'descarga_xml_wizard'
    _description = 'Descarga XML'

    dfinal = datetime.date.today()
    dinicial = dfinal - datetime.timedelta(days=31)
    facturas = fields.Boolean(string="Facturas", default=True )
    notas_credito = fields.Boolean(string="Notas de crédito", default=True )
    pagos = fields.Boolean(string="CFDI de pago", default=True )
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

          for record in cfdis:
              if record.datas_fname:
                  file_name = record.datas_fname
                  file_content = base64.b64decode(record.datas)
                  with open(file_name, 'wb') as file:
                      file.write(file_content)


          #for cfdi in cfdis:
          #    descarga = self.dl(cfdi)

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


          try:
              # import zlib
              compression = zipfile.ZIP_DEFLATED
          except:
              compression = zipfile.ZIP_STORED

          # getting working module where your current python file (model.py) exists
          path = os.path.dirname(os.path.realpath(__file__))

          file_name = "static\\src\\any_folder\\" + "cfdi.zip"

          zipfilepath = os.path.join(path, file_name)

          zf = zipfile.ZipFile(zipfilepath, mode="w")

          for cfdi in cfdis:
              adjunto = path + '/' + cfdi.name
              zf.write(adjunto, compress_type=compression)

          zf.close()

          action = {
                   'type': 'ir.actions.act_url',
                   'url': str('/your_module/static/src/any_folder/' + str(
                       zf)),
                   'target': 'self'
               }

          return action


          # creating file name (like example.txt) in which we have to write binary field data or attachment
          # object_name = self.binary_field_name
          # object_handle = open(object_name, "w")

          # writing binary data into file handle
          # object_handle.write(isBase64_decodestring(self.attachment))
          # object_handle.close()

          # writing file into zip file
          # zip_archive.write(object_name)
          # zip_archive.close()

          # code snipet for downloading zip file
          # return {
          #         'type': 'ir.actions.act_url',
          #         'url': str('/your_module/static/src/any_folder/' + str(
          #             file_name_zip),
          #         'target': 'new'
          #     }


          #for cfdi in cfdis:
          #     dfile = self.dl(cfdi)

        # return True

=============

        # data = io.BytesIO(base64.standard_b64decode(archivo.datas))
        # we follow what is done in ir_http's binary_content for the extension management
        # extension = os.path.splitext(archivo.name or '')[1]
        # extension = extension if extension else mimetypes.guess_extension(
        #    archivo.mimetype or '')
        # filename = archivo.name
        # filename = filename if os.path.splitext(filename)[
        #     1] else filename + extension

        vals = []
        if not self.cliente:
            self.env.cr.execute("UPDATE res_partner SET x_limite_credito = 0;")

            clientes = self.env['res.partner'].search([('ref','!=','010'),('vat','!=','XAXX010101000'),
                                                       ('x_studio_lc_fijo','=',False)])
            for cte in clientes:
                nprecios = [381,378]
                ventas = self.env['sale.order'].search([('partner_id.id','=',cte.id),('invoice_status','=','invoiced'),
                                                ('pricelist_id','in',nprecios)]).mapped('amount_total')

                cte.write({'x_studio_total_facturado': sum(ventas)})
                if sum(ventas) > self.total_ventas_min:
                    cte.write({'x_limite_credito': sum(ventas) / 4})


        if self.cliente:
            clientes = self.env['res.partner'].search([('id', '=', self.cliente.id),
                                                       ('x_studio_lc_fijo','=',False)])
            for cte in clientes:
                cte.write({'x_limite_credito': 0})
                nprecios = [381, 378]
                ventas = self.env['sale.order'].search(
                    [('partner_id.id', '=', cte.id),
                     ('invoice_status', '=', 'invoiced'),
                     ('pricelist_id', 'in', nprecios)]).mapped('amount_total')

                cte.write({'x_studio_total_facturado': sum(ventas)})
                if sum(ventas) > self.total_ventas_min:
                    cte.write({'x_limite_credito': sum(ventas) / 4})

        return True
"""