# -*- coding: utf-8 -*-

# peso_cantidad_caja.py
# Captura de peso y cantidad por caja de un producto.
# VBueno 1903202411:29
# ...

import logging
from odoo.tools.float_utils import float_round
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Modelo 'wizard.pesocajacantidad' para capturar el peso y cantidad por caja de un producto.
class PesoCantidadCaja(models.TransientModel):
    _name = 'wizard.pesocajacantidad'  # Nombre del modelo
    _description = 'Peso y cantidad en caja'  # Descripción del modelo

    # Campos del modelo:
    producto = fields.Many2one('product.template', string="Producto")  # Relación con el producto
    cantidad = fields.Char(string="Cantidad por caja")  # Cantidad de productos por caja
    peso = fields.Char(string="Peso por caja")  # Peso total de la caja

    # Método que se activa cuando se selecciona un producto:
    @api.onchange('producto')
    def _onchange_producto(self):
        # Al cambiar el producto, se asignan el peso y cantidad por caja del producto seleccionado
        self.peso = self.producto.x_peso_por_caja if self.producto else 0
        self.cantidad = self.producto.x_cantidad_por_caja if self.producto else 0

    # Método para aplicar los cambios en el peso y cantidad por caja:
    def aplicar_peso_cantidad(self):
        # Verifica que se haya seleccionado un producto
        if not self.producto:
            raise UserError("Debe seleccionar un producto.")
        # Actualiza los campos 'x_peso_por_caja' y 'x_cantidad_por_caja' en el producto
        self.producto.write({'x_peso_por_caja': self.peso, 'x_cantidad_por_caja': self.cantidad})
        return True

