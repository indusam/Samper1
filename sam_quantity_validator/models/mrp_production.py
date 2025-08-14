from odoo import models, api, _
from odoo.exceptions import UserError
import logging
from typing import Dict, Any, List, Optional, Union

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    # Define quantity fields that should be validated
    _qty_fields = ['product_qty']

    def _validate_qty(self, qty: float, context: str = '') -> float:
        """Validate and adjust quantity values.
        
        Args:
            qty: The quantity to validate
            context: Context string for logging (e.g., 'create', 'write')
            
        Returns:
            float: The validated quantity (0 if abs(qty) < 0.0001)
        """
        if abs(qty) < 0.0001:
            _logger.info(
                "%s: Ajustando cantidad %s a 0 en producción %s (contexto: %s)",
                self._name,
                qty,
                self.name or 'Nueva',
                context or 'default'
            )
            return 0.0
        return qty

    def _validate_move_quantity(self, move: 'StockMove', field: str = 'quantity_done') -> None:
        """Validate and adjust quantity for a specific move field."""
        if abs(move[field]) < 0.0001:
            _logger.info(
                "%s: Ajustando %s a 0 en movimiento %s (producción: %s)",
                self._name,
                field,
                move.id,
                self.name or 'Nueva'
            )
            move[field] = 0.0

    # ============ BASIC VALIDATIONS ============
    @api.model
    def create(self, vals: Dict[str, Any]) -> 'MrpProduction':
        """Override create to validate quantity fields."""
        if 'product_qty' in vals:
            vals['product_qty'] = self._validate_qty(vals['product_qty'], 'create')
        return super().create(vals)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields."""
        if 'product_qty' in vals:
            vals['product_qty'] = self._validate_qty(vals['product_qty'], 'write')
        return super().write(vals)

    # ============ PRODUCTION PROCESS VALIDATIONS ============
    def _generate_moves(self) -> 'StockMove':
        """Override _generate_moves to validate move quantities."""
        moves = super()._generate_moves()
        for move in moves:
            if abs(move.product_uom_qty) < 0.0001:
                move.product_uom_qty = 0.0
        return moves

    def _pre_button_mark_done(self) -> bool:
        """Override _pre_button_mark_done to validate quantities."""
        for move in self.move_raw_ids:
            self._validate_move_quantity(move, 'quantity_done')
        return super()._pre_button_mark_done()

    def _post_inventory(self) -> bool:
        """Override _post_inventory to validate quantities."""
        for move in self.move_finished_ids:
            self._validate_move_quantity(move, 'quantity_done')
        return super()._post_inventory()

    # ============ COMPONENT VALIDATION ============
    def _update_raw_moves(self, factor: float) -> 'StockMove':
        """Override _update_raw_moves to validate quantities."""
        moves = super()._update_raw_moves(factor)
        for move in moves:
            if abs(move.product_uom_qty) < 0.0001:
                move.product_uom_qty = 0.0
        return moves

    def _check_consumption(self) -> bool:
        """Override _check_consumption to validate quantities."""
        for move in self.move_raw_ids:
            self._validate_move_quantity(move, 'quantity_done')
        return super()._check_consumption()

    # ============ ERROR HANDLING ============
    def button_mark_done(self) -> Dict[str, Any]:
        """Override button_mark_done to handle minimum quantity errors."""
        try:
            return super().button_mark_done()
        except UserError as e:
            if 'minimum' in str(e).lower():
                self._force_zero_quantities()
                return super().button_mark_done()
            raise

    def _force_zero_quantities(self) -> None:
        """Force problematic quantities to zero."""
        for move in self.move_ids:
            if abs(move.quantity_done) < 0.0001:
                move.quantity_done = 0.0
                _logger.warning(
                    "%s: Ajustada cantidad a 0 en movimiento %s (producción: %s)",
                    self._name,
                    move.id,
                    self.name or 'Nueva'
                )