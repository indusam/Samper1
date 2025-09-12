from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from typing import Dict, Any, Optional, Union

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _validate_qty(self, qty: Union[float, int]) -> float:
        """Valida, redondea a 4 decimales y ajusta los valores de cantidad.
        
        Args:
            qty: La cantidad a validar y redondear
            
        Regresa:
            float: La cantidad validada y redondeada (0 si abs(qty) < 0.0001)
            
        Lanza:
            ValidationError: Si la cantidad no es un número válido
        """
        try:
            # Convertir a float y redondear a 4 decimales
            qty_float = float(qty)
            qty_rounded = round(qty_float, 4)
            
            # Si el valor redondeado es efectivamente 0, retornar 0.0
            if abs(qty_rounded) < 0.0001:
                _logger.info(
                    "%s: Ajustando cantidad %s a 0 en existencia %s",
                    self._name,
                    qty_float,
                    self.id or 'nueva'
                )
                return 0.0
                
            return qty_rounded
            
        except (TypeError, ValueError) as e:
            _logger.error(
                "%s: Error validando cantidad %s: %s",
                self._name,
                qty,
                str(e)
            )
            raise ValidationError(_("La cantidad debe ser un número válido")) from e

    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescribe create para validar campos de cantidad en lote."""
        for vals in vals_list:
            if 'quantity' in vals and vals['quantity'] is not None:
                # Crear un registro temporal para validar la cantidad
                temp = self.new(vals)
                try:
                    validated_qty = temp._validate_qty(vals['quantity'])
                    vals['quantity'] = validated_qty
                except ValidationError:
                    # Si la validación falla para un registro, saltarlo y dejar que el método super maneje el error
                    continue
        return super().create(vals_list)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Sobrescribe write para validar campos de cantidad.
        
        Args:
            vals: Diccionario de valores de campos
            
        Returns:
            bool: True si write fue exitoso
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