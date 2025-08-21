from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from odoo.addons.mrp.models.mrp_production import MrpProduction as Production
    from odoo.addons.stock.models.stock_move import StockMove

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    # Define quantity fields that should be validated
    _qty_fields = ['product_qty']

    def _validate_qty(self, qty: Union[float, int], context: str = '') -> float:
        """Validate and adjust quantity values.
        
        Args:
            qty: The quantity to validate
            context: Context string for logging (e.g., 'create', 'write')
            
        Returns:
            float: The validated quantity (0 if abs(qty) < 0.0001)
            
        Raises:
            ValidationError: If qty is not a valid number
        """
        try:
            qty_float = float(qty)
            if abs(qty_float) < 0.0001:
                _logger.info(
                    "%s: Ajustando cantidad %s a 0 en producción %s (contexto: %s)",
                    self._name,
                    qty_float,
                    self.name or 'Nueva',
                    context or 'default'
                )
                return 0.0
            return qty_float
        except (TypeError, ValueError) as e:
            _logger.error(
                "%s: Error validando cantidad %s (contexto: %s): %s",
                self._name,
                qty,
                context or 'default',
                str(e)
            )
            raise ValidationError(_("La cantidad debe ser un número válido")) from e

    def _validate_move_quantity(self, move: 'StockMove', field: str = 'quantity_done') -> None:
        """Validate and adjust quantity for a specific move field.
        
        Args:
            move: The stock move to validate
            field: The field name to validate
            
        Raises:
            ValidationError: If the move or field is invalid
        """
        try:
            if not move or not hasattr(move, field):
                raise ValidationError(_("Movimiento o campo no válido"))
                
            value = move[field] or 0.0
            if abs(value) < 0.0001:
                _logger.info(
                    "%s: Ajustando %s a 0 en movimiento %s (producción: %s)",
                    self._name,
                    field,
                    move.id,
                    self.name or 'Nueva'
                )
                move[field] = 0.0
        except Exception as e:
            _logger.error(
                "%s: Error validando movimiento %s, campo %s: %s",
                self._name,
                move.id if move else 'N/A',
                field,
                str(e)
            )
            raise ValidationError(_("Error al validar la cantidad del movimiento")) from e

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

    def _post_inventory(self, cancel_backorder: bool = False) -> bool:
        """Override _post_inventory to validate quantities.
        
        Args:
            cancel_backorder: If True, cancel backorder after posting inventory
            
        Returns:
            bool: True if the operation was successful
            
        Raises:
            UserError: If there's an error during the operation
        """
        try:
            _logger.debug(
                "%s: Validando cantidades antes de publicar inventario (cancel_backorder=%s)",
                self._name,
                cancel_backorder
            )
            
            # Validar movimientos de productos terminados
            if not self.move_finished_ids:
                _logger.warning("%s: No hay movimientos de productos terminados", self._name)
            
            for move in self.move_finished_ids:
                self._validate_move_quantity(move, 'quantity_done')
                
            # Llamar al método original
            result = super()._post_inventory(cancel_backorder=cancel_backorder)
            
            _logger.info(
                "%s: Inventario publicado exitosamente (ID: %s, cancel_backorder=%s)",
                self._name,
                self.id,
                cancel_backorder
            )
            
            return result
            
        except Exception as e:
            _logger.error(
                "%s: Error al publicar inventario (ID: %s): %s",
                self._name,
                self.id,
                str(e),
                exc_info=True
            )
            raise UserError(_("Error al publicar el inventario: %s") % str(e)) from e

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