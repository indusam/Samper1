from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
from typing import Dict, Any, Optional, Union

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _validate_qty(self, qty: Union[float, int]) -> float:
        """Valida, redondea a 4 decimales y ajusta los valores de cantidad.
        
        Args:
            qty: La cantidad a validar y redondear
            
        Returns:
            float: La cantidad validada y redondeada (0 si abs(qty) < 0.0001)
            
        Raises:
            ValidationError: Si la cantidad no es un número válido
        """
        try:
            qty_float = float(qty)
            qty_rounded = round(qty_float, 6)
            
            if abs(qty_rounded) < 0.000001:
                return 0.0
                
            return qty_rounded
            
        except (TypeError, ValueError) as e:
            raise ValidationError(_("Cantidad inválida: %s") % str(e)) from e

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to validate quantity fields in batch."""
        for vals in vals_list:
            if 'quantity' in vals and vals['quantity'] is not None:
                try:
                    temp = self.new(vals)
                    validated_qty = temp._validate_qty(vals['quantity'])
                    vals['quantity'] = validated_qty
                except ValidationError:
                    continue
        return super().create(vals_list)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields."""
        if 'quantity' in vals and vals['quantity'] is not None:
            try:
                validated_qty = self._validate_qty(vals['quantity'])
                vals['quantity'] = validated_qty
            except ValidationError as e:
                raise
        return super().write(vals)