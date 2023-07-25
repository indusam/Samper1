# -*- coding: utf-8 -*-

# borra_pdf.py
# Borra los pdf de los CFDI.
# Borra los pdf de facturas, notas de crédito y recibos de pago de un rango de
# determinado para liberar espacio en disco.
# VBueno 1908202112:04

import datetime
import logging
# import requests

from odoo import models, fields, http
from odoo.exceptions import UserError
import base64
import io
import os

import mimetypes
# from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class BorraPdf(models.TransientModel):
    _name = 'borra_pdf.wizard'
    _description = 'Borra PDF'

    dfinal = datetime.date.today()
    dinicial = dfinal - datetime.timedelta(days=365)
    corte = fields.Date(string="Corte", required=True,
                              default=dfinal)

    def deletepdf(self):

        archivos = self.env['ir.attachment'].search([('create_date','<=',self.corte),
                                                     ('name','ilike','.pdf')])

        for archivo in archivos:

            file = '/home/odoo/data/filestore/indusam-samper1-samper-v13-875997/'+archivo.store_fname  # directorio de producción
            #file = '/home/odoo/data/filestore/indusam-samper1-master-9090991/'+archivo.store_fname # directorio de pruebas

            if os.path.exists(file):
                os.remove(file)
                archivo.write({'res_id': 0})