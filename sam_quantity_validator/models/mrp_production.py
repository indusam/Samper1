from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from odoo.addons.mrp.models.mrp_production import MrpProduction as Production
    from odoo.addons.stock.models.stock_move import StockMove

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
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
            qty_rounded = round(qty_float, 4)
            if abs(qty_rounded) < 0.0001:
                return 0.0
            return qty_rounded
        except (TypeError, ValueError) as e:
            raise ValidationError(_("Cantidad inválida: %s") % str(e)) from e

    def _validate_move_quantity(self, move: 'StockMove', field: str) -> None:
        """Validate and adjust quantity for a specific move field."""
        if not move or not field:
            raise ValidationError(_("Movimiento o campo no válido"))
            
        value = move[field] or 0.0
        value_rounded = round(float(value), 4)
        
        if abs(value_rounded) < 0.0001:
            move[field] = 0.0
        else:
            move[field] = value_rounded

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields."""
        if 'product_qty' in vals:
            vals['product_qty'] = self._validate_qty(vals['product_qty'], 'write')
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'MrpProduction':
        """Override create to validate quantity fields."""
        for vals in vals_list:
            if 'product_qty' in vals:
                vals['product_qty'] = self._validate_qty(vals['product_qty'], 'create')
        return super().create(vals_list)

    def _generate_moves(self) -> 'StockMove':
        """Override _generate_moves to validate move quantities."""
        moves = super()._generate_moves()
        # Handle both tuple and StockMove objects
        if isinstance(moves, (list, tuple)):
            for move in moves:
                if hasattr(move, 'product_uom_qty'):
                    if abs(move.product_uom_qty) < 0.0001:
                        move.product_uom_qty = 0.0
        elif hasattr(moves, 'product_uom_qty'):
            if abs(moves.product_uom_qty) < 0.0001:
                moves.product_uom_qty = 0.0
        return moves

    def _update_raw_moves(self, factor: float) -> 'StockMove':
        """Override _update_raw_moves to validate quantities."""
        moves = super()._update_raw_moves(factor)
        # Handle both tuple and StockMove objects
        if isinstance(moves, (list, tuple)):
            for move in moves:
                if hasattr(move, 'product_uom_qty'):
                    if abs(move.product_uom_qty) < 0.0001:
                        move.product_uom_qty = 0.0
        elif hasattr(moves, 'product_uom_qty'):
            if abs(moves.product_uom_qty) < 0.0001:
                moves.product_uom_qty = 0.0
        return moves

    def _check_quantities(self) -> None:
        """Check and fix quantities before action_confirm."""
        for order in self:
            order._force_zero_quantities()
        return super()._check_quantities()

    def _force_zero_quantities(self) -> None:
        """Force problematic quantities to zero."""
        for move in self.move_ids:
            if abs(move.quantity_done) < 0.000001:
                move.quantity_done = 0.0