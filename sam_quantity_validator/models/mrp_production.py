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
            float: The validated quantity (0 if abs(qty) < 0.000001)
            
        Raises:
            ValidationError: If qty is not a valid number
        """
        try:
            qty_float = float(qty)
            if abs(qty_float) < 0.000001:
                return 0.0
            return qty_float
        except (TypeError, ValueError) as e:
            raise ValidationError(_("Cantidad inválida: %s") % str(e)) from e

    def _validate_move_quantity(self, move: 'StockMove', field: str) -> None:
        """Validate and adjust quantity for a specific move field."""
        if not move or not field:
            raise ValidationError(_("Movimiento o campo no válido"))
            
        value = move[field] or 0.0
        value = round(float(value), 6)
        
        if abs(value) < 0.000001:
            move[field] = 0.0

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
        for move in moves:
            if abs(move.product_uom_qty) < 0.000001:
                move.product_uom_qty = 0.0
        return moves

    def _update_raw_moves(self, factor: float) -> 'StockMove':
        """Override _update_raw_moves to validate quantities."""
        moves = super()._update_raw_moves(factor)
        for move in moves:
            if abs(move.product_uom_qty) < 0.000001:
                move.product_uom_qty = 0.0
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