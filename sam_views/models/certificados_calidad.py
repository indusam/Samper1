# -*- coding: utf-8 -*-
from odoo import fields, models


class CertificadosCalidad(models.Model):
    _inherit = 'x_certificados_calidad'

    x_apariencia = fields.Char(string="Apariencia")
