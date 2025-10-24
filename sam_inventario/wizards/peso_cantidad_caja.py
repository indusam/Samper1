# -*- coding: utf-8 -*-
"""
peso_cantidad_caja.py
Captura de peso y cantidad por caja de un producto.
VBueno 1903202411:29
Actualizado para Odoo v18
"""

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PesoCantidadCaja(models.TransientModel):
    """
    Wizard para capturar el peso y cantidad por caja de un producto.
    Actualizado para Odoo v18.
    """
    _name = 'wizard.pesocajacantidad'
    _description = 'Peso y cantidad en caja'

    # Campos del modelo:
    producto = fields.Many2one(
        'product.template',
        string="Producto",
        required=True
    )
    cantidad = fields.Char(
        string="Cantidad por caja",
        help="Cantidad de productos por caja"
    )
    peso = fields.Char(
        string="Peso por caja",
        help="Peso total de la caja"
    )

    @api.onchange('producto')
    def _onchange_producto(self):
        """
        Al cambiar el producto, se cargan automáticamente el peso y cantidad
        por caja del producto seleccionado.
        """
        if self.producto:
            self.peso = str(self.producto.x_peso_por_caja) if hasattr(self.producto, 'x_peso_por_caja') else '0'
            self.cantidad = str(self.producto.x_cantidad_por_caja) if hasattr(self.producto, 'x_cantidad_por_caja') else '0'
        else:
            self.peso = '0'
            self.cantidad = '0'

    def aplicar_peso_cantidad(self):
        """
        Aplica los cambios en el peso y cantidad por caja al producto seleccionado.

        :raises UserError: Si no se ha seleccionado un producto
        :return: True si se actualizó correctamente
        """
        self.ensure_one()

        if not self.producto:
            raise UserError("Debe seleccionar un producto.")

        # Actualiza los campos 'x_peso_por_caja' y 'x_cantidad_por_caja' en el producto
        self.producto.write({
            'x_peso_por_caja': self.peso,
            'x_cantidad_por_caja': self.cantidad
        })

        _logger.info(f"Actualizado peso y cantidad por caja para producto {self.producto.name}")

        return {'type': 'ir.actions.act_window_close'}

