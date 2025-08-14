from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _validate_qty(self, qty, context=False):
        if 0 < qty < 0.0001:
            _logger.info(
                f"Ajustando cantidad {qty} a 0 en producción {self.name or 'Nueva'}"
            )
            return 0
        return qty

    # ============ VALIDACIONES BÁSICAS ============
    @api.model
    def create(self, vals):
        if 'product_qty' in vals:
            vals['product_qty'] = self._validate_qty(vals['product_qty'], 'create')
        return super().create(vals)

    def write(self, vals):
        if 'product_qty' in vals:
            vals['product_qty'] = self._validate_qty(vals['product_qty'], 'write')
        return super().write(vals)

    # ============ VALIDACIONES EN PROCESO PRODUCTIVO ============
    def _generate_moves(self):
        moves = super()._generate_moves()
        for move in moves:
            if 0 < move.product_uom_qty < 0.0001:
                move.product_uom_qty = 0
        return moves

    def _pre_button_mark_done(self):
        for move in self.move_raw_ids:
            if 0 < move.quantity_done < 0.0001:
                move.quantity_done = 0
        return super()._pre_button_mark_done()

    def _post_inventory(self):
        for move in self.move_finished_ids:
            if 0 < move.quantity_done < 0.0001:
                move.quantity_done = 0
        return super()._post_inventory()

    # ============ VALIDACIÓN EN COMPONENTES ============
    def _update_raw_moves(self, factor):
        moves = super()._update_raw_moves(factor)
        for move in moves:
            if 0 < move.product_uom_qty < 0.0001:
                move.product_uom_qty = 0
        return moves

    def _check_consumption(self):
        for move in self.move_raw_ids:
            if 0 < move.quantity_done < 0.0001:
                move.quantity_done = 0
        return super()._check_consumption()

    # ============ MANEJO DE ERRORES ============
    def button_mark_done(self):
        try:
            return super().button_mark_done()
        except UserError as e:
            if 'minimum' in str(e).lower():
                self._force_zero_quantities()
                return super().button_mark_done()
            raise

    def _force_zero_quantities(self):
        """ Fuerza a cero cantidades problemáticas """
        for move in self.move_ids:
            if 0 < move.quantity_done < 0.0001:
                move.quantity_done = 0
                _logger.warning(
                    f"Producción {self.name}: Ajustada cantidad a 0 en movimiento {move.id}"
                )