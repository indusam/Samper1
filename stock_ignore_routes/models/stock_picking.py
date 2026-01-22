# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPicking(models.Model):
    """Herencia de stock.picking para agregar campo de ignorar rutas automáticas."""
    _inherit = 'stock.picking'

    x_ignorar_rutas = fields.Boolean(
        string='Ignorar rutas automáticas',
        default=False,
        help='Si está marcado, este traslado cancelará automáticamente los movimientos '
             'secundarios generados por rutas de productos. '
             'Solo se ejecutará el movimiento directo.',
    )
