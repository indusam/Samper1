from odoo import models, api, _
import logging
from typing import Optional, Union, Dict, Any

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    # Define quantity fields that should be validated
    _qty_fields = ['product_uom_qty', 'quantity_done', 'reserved_availability']

    def _validate_qty(self, qty: float, field_name: str = '') -> float:
        """Validate and adjust quantity values.
        
        Args:
            qty: The quantity to validate
            field_name: Name of the field being validated (for logging)
            
        Returns:
            float: The validated quantity (0 if abs(qty) < 0.0001)
        """
        if abs(qty) < 0.0001:
            _logger.info(
                "%s: Ajustando %s de %s a 0 en movimiento %s",
                self._name,
                field_name or 'quantity',
                qty,
                self.id
            )
            return 0.0
        return qty

    def _validate_quantity_fields(self, vals: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all quantity fields in the provided values dict."""
        for field in self._qty_fields:
            if field in vals and vals[field] is not None:
                vals[field] = self._validate_qty(vals[field], field)
        return vals

    @api.model
    def create(self, vals: Dict[str, Any]) -> 'StockMove':
        """Override create to validate quantity fields."""
        vals = self._validate_quantity_fields(vals)
        return super().create(vals)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields."""
        vals = self._validate_quantity_fields(vals)
        return super().write(vals)

    def _action_assign(self) -> bool:
        """Override _action_assign to validate and round quantities before assigning."""
        for move in self:
            try:
                # Redondear a 4 decimales
                rounded_qty = round(float(move.product_uom_qty or 0.0), 4)
                
                # Si el valor redondeado es efectivamente 0, establecer a 0.0
                if abs(rounded_qty) < 0.0001:
                    move.product_uom_qty = 0.0
                else:
                    move.product_uom_qty = rounded_qty
                    
            except (TypeError, ValueError) as e:
                _logger.error(
                    "%s: Error redondeando cantidad en movimiento %s: %s",
                    self._name,
                    move.id,
                    str(e)
                )
                # En caso de error, forzar a 0.0 para evitar problemas
                move.product_uom_qty = 0.0
                
        return super()._action_assign()