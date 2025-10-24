# -*- coding: utf-8 -*-
"""
Extensión del modelo stock.move para Samper - Actualizado para Odoo v18
"""

from odoo import models, fields, api
from odoo.exceptions import UserError

class StockMove(models.Model):
    """
    Modelo que extiende 'stock.move' para agregar campos adicionales y lógica
    relacionada con la existencia del almacén de origen en los traslados.
    Actualizado para Odoo v18.

    Atributos:
        - x_exis_origen (Float): Indica la existencia del producto en el almacén de origen.
        - x_merma_pct (Float): Permite registrar el porcentaje de merma del producto en el traslado.
    """
    _inherit = 'stock.move'

    x_exis_origen = fields.Float(
        string='Existencia Origen',
        help="Existencia del producto en la ubicación de origen."
    )
    x_merma_pct = fields.Float(
        string='% Merma',
        digits=(3, 2),
        help="Porcentaje de merma del producto durante el traslado."
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Método que se ejecuta al cambiar el producto en un movimiento de stock.

        - Obtiene la cantidad disponible del producto en la ubicación de origen
          y la asigna a `x_exis_origen`.
        - Establece el nombre del movimiento como 'Nuevo' si se selecciona un producto.
        """
        if self.product_id and self.location_id:
            # Busca la cantidad disponible del producto en la ubicación de origen
            stock_quant = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id', '=', self.location_id.id)
            ], limit=1)

            # Si hay existencia, la asigna al campo x_exis_origen
            if stock_quant and stock_quant.quantity > 0:
                self.x_exis_origen = stock_quant.quantity
            else:
                self.x_exis_origen = 0.0

            # Asigna un nombre por defecto al movimiento si no tiene uno
            if not self.name or self.name == '/':
                self.name = 'Nuevo'  # La descripción es obligatoria
