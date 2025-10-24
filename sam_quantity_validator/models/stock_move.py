from odoo import models, api, fields
from odoo.exceptions import UserError, ValidationError
from typing import Dict, Any, Optional, Union

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    # Define quantity fields that should be validated
    _qty_fields = ['product_uom_qty', 'quantity_done', 'reserved_availability']

    def _validate_qty(self, qty: float, field_name: str = '') -> float:
        """Validate and adjust quantity values.
        
        Args:
            qty: The quantity to validate
            field_name: Name of the field being validated (for reference)
            
        Returns:
            float: The validated quantity (0 if abs(qty) < 0.0001)
        """
        qty_rounded = round(float(qty), 4) if qty is not None else 0.0
        if abs(qty_rounded) < 0.0001:
            return 0.0
        return qty_rounded

    def _validate_quantity_fields(self, vals: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all quantity fields in the provided values dict."""
        for field in self._qty_fields:
            if field in vals and vals[field] is not None:
                vals[field] = self._validate_qty(vals[field], field)
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to validate quantity fields in batch."""
        for vals in vals_list:
            self._validate_quantity_fields(vals)
        return super().create(vals_list)

    def write(self, vals: Dict[str, Any]) -> bool:
        """Override write to validate quantity fields."""
        vals = self._validate_quantity_fields(vals)
        return super().write(vals)
        
    def _action_assign(self, force_qty=None):
        """Override _action_assign to handle quantity validation."""
        res = super()._action_assign(force_qty=force_qty)

        for move in self:
            try:
                qty_to_validate = force_qty if force_qty is not None else (move.product_uom_qty or 0.0)

                # Round to 4 decimal places
                rounded_qty = round(float(qty_to_validate), 4)

                # If the rounded value is effectively 0, set to 0.0
                if abs(rounded_qty) < 0.0001:
                    rounded_qty = 0.0

                # Update the corresponding field
                if force_qty is not None:
                    move.product_uom_qty = rounded_qty
                else:
                    move.quantity_done = rounded_qty

            except Exception:
                continue

        return res