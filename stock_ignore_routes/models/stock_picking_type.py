# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPickingType(models.Model):
    """Herencia de stock.picking.type para agregar campo de ignorar rutas automáticas."""
    _inherit = 'stock.picking.type'

    x_ignorar_rutas = fields.Boolean(
        string='Ignorar rutas automáticas',
        default=False,
        help='Si está marcado, los traslados de este tipo de operación cancelarán '
             'automáticamente los movimientos secundarios generados por rutas de productos. '
             'Solo se ejecutará el movimiento directo.',
    )
