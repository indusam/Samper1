# -*- coding: utf-8 -*-

# peso_cantidad_caja.py
# captura de peso y cantidad por caja de un producto.
# VBueno 1903202411:29
# .

import logging
from odoo.tools.float_utils import float_round
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PesoCantidadCaja(models.TransientModel):

    _name = 'wizard.pesocajacantidad'
    _description = 'Peso y cantidad en caja'

    producto = fields.Many2one('product.template', string="Producto")
    cantidad = fields.Float(string="Cantidad por caja", digits=(10, 4))
    peso = fields.Float(string="Peso por caja", digits=(10, 4))
    
    @api.multi
    def aplicar_peso_cantidad(self):
        if not self.producto:
            raise UserError("Debe seleccionar un producto.")
        self.producto.x_peso_por_caja = self.peso
        self.producto.x_cantidad_por_caja = self.cantidad
        return True

