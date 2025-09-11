from odoo import models, api, _
import logging
from typing import Dict, Any, Optional, List

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    # Define move fields that should be validated
    _move_qty_fields = ['quantity_done']

    def _validate_move_quantity(self, move: 'StockMove', field: str = 'quantity_done') -> None:
        """Validate, round to 4 decimal places, and adjust quantity for a specific move field.
        
        Args:
            move: The stock.move record to validate
            field: The field name to validate (e.g., 'quantity_done')
            
        Raises:
            ValueError: If the quantity cannot be converted to a valid number
        """
        try:
            # Obtener el valor actual y redondear a 4 decimales
            current_value = move[field] or 0.0
            rounded_value = round(float(current_value), 4)
            
            # Si el valor redondeado es efectivamente 0, establecer a 0.0
            if abs(rounded_value) < 0.0001:
                move[field] = 0.0
                _logger.info(
                    "%s: Ajustando %s de %s a 0 en movimiento %s (transferencia: %s)",
                    self._name,
                    field,
                    current_value,
                    move.id,
                    self.name or 'Nueva'
                )
            # Solo actualizar si el valor ha cambiado significativamente
            elif abs(rounded_value - current_value) > 0.00001:
                move[field] = rounded_value
                _logger.debug(
                    "%s: Redondeando %s de %s a %s en movimiento %s (transferencia: %s)",
                    self._name,
                    field,
                    current_value,
                    rounded_value,
                    move.id,
                    self.name or 'Nueva'
                )
                
        except (TypeError, ValueError) as e:
            _logger.error(
                "%s: Error validando cantidad en movimiento %s, campo %s: %s",
                self._name,
                move.id,
                field,
                str(e)
            )
            # En caso de error, forzar a 0.0 para evitar problemas
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