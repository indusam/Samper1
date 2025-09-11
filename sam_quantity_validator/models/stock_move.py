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

    def _action_assign(self, force_qty=None):
        """Override _action_assign to validate and round quantities before assigning.
        
        Args:
            force_qty: Optional quantity to force assign (used by parent method)
            
        Returns:
            bool: Result of the parent's _action_assign method
        """
        for move in self:
            try:
                # Usar force_qty si se proporciona, de lo contrario usar product_uom_qty
                qty_to_validate = force_qty if force_qty is not None else (move.product_uom_qty or 0.0)
                
                # Redondear a 4 decimales
                rounded_qty = round(float(qty_to_validate), 4)
                
                # Si el valor redondeado es efectivamente 0, establecer a 0.0
                if abs(rounded_qty) < 0.0001:
                    rounded_qty = 0.0
                
                # Actualizar el campo correspondiente
                if force_qty is not None:
                    # Si se está forzando una cantidad, devolver el valor redondeado
                    # para que el método padre lo utilice
                    force_qty = rounded_qty
                else:
                    # De lo contrario, actualizar el campo product_uom_qty
                    move.product_uom_qty = rounded_qty
                    
            except (TypeError, ValueError) as e:
                _logger.error(
                    "%s: Error redondeando cantidad en movimiento %s: %s",
                    self._name,
                    move.id,
                    str(e)
                )
                # En caso de error, forzar a 0.0 para evitar problemas
                if force_qty is not None:
                    force_qty = 0.0
                else:
                    move.product_uom_qty = 0.0
                
        # Llamar al método padre con el force_qty actualizado si es necesario
        return super()._action_assign(force_qty=force_qty if force_qty is not None else None)