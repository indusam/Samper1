from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from typing import Dict, Any, Optional, Union

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _validate_qty(self, qty: Union[float, int]) -> float:
        """Validate, round to 4 decimal places, and adjust quantity values.
        
        Args:
            qty: The quantity to validate and round
            
        Returns:
            float: The validated and rounded quantity (0 if abs(qty) < 0.0001)
            
        Raises:
            ValidationError: If qty is not a valid number
        """
        try:
            # Convertir a float y redondear a 4 decimales
            qty_float = float(qty)
            rounded_qty = round(qty_float, 4)
            
            # Si el valor redondeado es efectivamente 0, retornar 0.0
            if abs(rounded_qty) < 0.0001:
                _logger.info(
                    "%s: Ajustando cantidad %s a 0 en existencia %s",
                    self._name,
                    qty_float,
                    self.id or 'nueva'
                )
                return 0.0
                
            return rounded_qty
            
        except (TypeError, ValueError) as e:
            _logger.error(
                "%s: Error validando cantidad %s: %s",
                self._name,
                qty,
                str(e)
            )
            raise ValidationError(_("La cantidad debe ser un número válido")) from e

    @api.model
    def create(self, vals: Dict[str, Any]) -> 'StockQuant':
        """Override create to validate quantity fields.
        
        Args:
            vals: Dictionary of field values
            
        Returns:
            Record created
        """
        if 'quantity' in vals and vals['quantity'] is not None:
            try:
                vals['quantity'] = self._validate_qty(vals['quantity'])
            except ValidationError as e:
                _logger.error(
                    "Error al crear existencia: %s",
                    str(e)
                )
                raise
        return super().create(vals)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields.
        
        Args:
            vals: Dictionary of field values
            
        Returns:
            bool: True if write was successful
        """
        if 'quantity' in vals and vals['quantity'] is not None:
            try:
                vals['quantity'] = self._validate_qty(vals['quantity'])
            except ValidationError as e:
                _logger.error(
                    "Error al actualizar existencia %s: %s",
                    self.id,
                    str(e)
                )
                raise
        return super().write(vals)