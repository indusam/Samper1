from odoo import models, api, _
from odoo.exceptions import ValidationError
import logging
from typing import Dict, Any, Optional, Union

_logger = logging.getLogger(__name__)

class StockLot(models.Model):
    _inherit = 'stock.lot'
    
    # Define quantity fields that should be validated
    _qty_fields = ['product_qty']

    def _validate_quantity(self, qty: float, context: str = '', record_id: Optional[int] = None) -> float:
        """Centralized method for quantity validation.
        
        Args:
            qty: The quantity to validate
            context: Context string for logging (e.g., 'create', 'write')
            record_id: Optional record ID for logging
            
        Returns:
            float: The validated quantity (0 if abs(qty) < 0.0001)
        """
        if abs(qty) < 0.0001:
            _logger.info(
                "%s: Ajustando cantidad %s a 0 en %s (ID: %s, contexto: %s)",
                self._name,
                qty,
                'stock.lot',
                record_id or self.id or 'Nuevo',
                context or 'default'
            )
            return 0.0
        return qty

    def _validate_quantity_fields(self, vals: Dict[str, Any], context: str = '') -> Dict[str, Any]:
        """Validate all quantity fields in the provided values dict."""
        for field in self._qty_fields:
            if field in vals and vals[field] is not None:
                vals[field] = self._validate_quantity(
                    vals[field],
                    f"{context or 'default'}.{field}",
                    self.id if self.ids else None
                )
        return vals

    @api.model
    def create(self, vals: Dict[str, Any]) -> 'StockLot':
        """Override create to validate quantity fields."""
        vals = self._validate_quantity_fields(vals, 'create')
        return super().create(vals)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields."""
        vals = self._validate_quantity_fields(vals, 'write')
        return super().write(vals)

    def _compute_quantities(self) -> None:
        """Override _compute_quantities to validate quantities."""
        super()._compute_quantities()
        for lot in self:
            if abs(lot.product_qty) < 0.0001:
                lot.product_qty = 0.0