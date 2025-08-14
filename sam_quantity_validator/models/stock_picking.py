from odoo import models, api, _
import logging
from typing import Dict, Any, Optional, List

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    # Define move fields that should be validated
    _move_qty_fields = ['quantity_done']

    def _validate_move_quantity(self, move: 'StockMove', field: str = 'quantity_done') -> None:
        """Validate and adjust quantity for a specific move field.
        
        Args:
            move: The stock.move record to validate
            field: The field name to validate
        """
        if abs(move[field]) < 0.0001:
            _logger.info(
                "%s: Ajustando %s a 0 en movimiento %s (transferencia: %s)",
                self._name,
                field,
                move.id,
                self.name or 'Nueva'
            )
            move[field] = 0.0

    def _validate_move_quantities(self) -> None:
        """Validate quantities for all moves in the picking."""
        for move in self.move_ids:
            for field in self._move_qty_fields:
                self._validate_move_quantity(move, field)

    def button_validate(self) -> Dict[str, Any]:
        """Override button_validate to validate quantities before processing."""
        self._validate_move_quantities()
        return super().button_validate()

    def action_confirm(self) -> bool:
        """Override action_confirm to validate quantities."""
        self._validate_move_quantities()
        return super().action_confirm()

    def action_assign(self) -> bool:
        """Override action_assign to validate quantities."""
        self._validate_move_quantities()
        return super().action_assign()