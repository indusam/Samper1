# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPicking(models.Model):
    """Herencia de stock.picking para agregar campo de ignorar rutas automáticas."""
    _inherit = 'stock.picking'

    x_ignorar_rutas = fields.Boolean(
        string='Ignorar rutas automáticas',
        default=False,
        help='Si está marcado, este traslado no generará movimientos secundarios '
             'por rutas de productos. Solo se ejecutará el movimiento directo.',
    )

    def action_confirm(self):
        """Sobreescribir para limpiar rutas antes de confirmar si x_ignorar_rutas está activo."""
        for picking in self.filtered('x_ignorar_rutas'):
            # Limpiar rutas y procure_method en los movimientos para evitar
            # que se generen movimientos secundarios por pull rules
            picking.move_ids.filtered(lambda m: m.state == 'draft').write({
                'procure_method': 'make_to_stock',
                'route_ids': [(5, 0, 0)],
                'rule_id': False,
            })
        return super().action_confirm()


class StockMove(models.Model):
    """Herencia de stock.move para ignorar push rules cuando el picking lo indica."""
    _inherit = 'stock.move'

    def _push_apply(self):
        """Excluir movimientos cuyo picking tiene x_ignorar_rutas activo."""
        moves_to_push = self.filtered(
            lambda m: not m.picking_id.x_ignorar_rutas
        )
        if moves_to_push:
            return super(StockMove, moves_to_push)._push_apply()
        return self.env['stock.move']
