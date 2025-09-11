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

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to validate quantity fields in batch."""
        for vals in vals_list:
            self._validate_quantity_fields(vals, 'create')
        return super().create(vals_list)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields."""
        vals = self._validate_quantity_fields(vals, 'write')
        return super().write(vals)

    def _compute_quantities(self) -> None:
        """Override _compute_quantities to validate and round quantities to 4 decimal places."""
        super()._compute_quantities()
        for lot in self:
            try:
                # Redondear a 4 decimales
                rounded_qty = round(float(lot.product_qty or 0.0), 4)
                
                # Si el valor redondeado es efectivamente 0, establecer a 0.0
                if abs(rounded_qty) < 0.0001:
                    lot.product_qty = 0.0
                else:
                    lot.product_qty = rounded_qty
                    
            except (TypeError, ValueError) as e:
                _logger.error(
                    "%s: Error redondeando cantidad en lote %s: %s",
                    self._name,
                    lot.id,
                    str(e)
                )
                # En caso de error, forzar a 0.0 para evitar problemas
                lot.product_qty = 0.0