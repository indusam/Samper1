from odoo import models, fields, api, _
import logging
import math

_logger = logging.getLogger(__name__)

class MrpConsumptionWarningLine(models.TransientModel):
    """Extend mrp.consumption.warning.line to modify float fields precision and handle quantity adjustments.
    """
    
    _inherit = 'mrp.consumption.warning.line'
    _name = 'mrp.consumption.warning.line'  # Explicitly set the model name
    
    # Override fields to set 4 decimal places and handle quantity adjustments
    product_consumed_qty_uom = fields.Float(
        string='Consumed',
        digits=(16, 4),  # Set precision to 4 decimal places
        readonly=True,
    )
    
    product_expected_qty_uom = fields.Float(
        string='Expected',
        digits=(16, 4),  # Set precision to 4 decimal places
        readonly=True,
    )
    
    # Add these computed fields to log and display the formatted quantities
    display_consumed_qty = fields.Char(
        string='Display Consumed',
        compute='_compute_display_quantities',
        store=False,
        readonly=True
    )
    
    display_expected_qty = fields.Char(
        string='Display Expected',
        compute='_compute_display_quantities',
        store=False,
        readonly=True
    )
    
    def _round_quantity(self, qty, digits=4, context_info=""):
        """Helper method to round quantity to specified decimal places and handle very small values."""
        try:
            if qty is None:
                return 0.0
                
            # Convert to float if it's a string
            if isinstance(qty, str):
                qty = float(qty)
                
            # Round to specified decimal places
            factor = 10.0 ** digits
            rounded = math.floor(qty * factor + 0.5) / factor
            
            # Log the rounding operation
            _logger.info(
                "[QUANTITY ROUNDING] %s\n"
                "  - Original: %.10f\n"
                "  - Rounded (%d decimals): %.10f",
                context_info or "No context",
                float(qty),
                digits,
                rounded
            )
            
            return rounded
            
        except (TypeError, ValueError) as e:
            _logger.error("Error rounding quantity %s: %s", qty, str(e), exc_info=True)
            return 0.0

    @api.depends('product_consumed_qty_uom', 'product_expected_qty_uom')
    def _compute_display_quantities(self):
        for record in self:
            # Format the quantities to 4 decimal places for display
            record.display_consumed_qty = f"{record.product_consumed_qty_uom:.4f}"
            record.display_expected_qty = f"{record.product_expected_qty_uom:.4f}"
            
            # Log the values being displayed
            _logger.info(
                "[DISPLAY] Product ID: %s | Consumed: %s (original: %.10f) | Expected: %s (original: %.10f)",
                record.product_id.id,
                record.display_consumed_qty,
                record.product_consumed_qty_uom,
                record.display_expected_qty,
                record.product_expected_qty_uom
            )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure all quantity values are properly rounded to 4 decimal places."""
        _logger.info("[CREATE] Starting batch create with %d records", len(vals_list))
        
        processed_vals_list = []
        for vals in vals_list:
            # Make a copy to avoid modifying the original
            new_vals = vals.copy()
            
            # Process quantity fields
            qty_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
            for field in qty_fields:
                if field in new_vals and new_vals[field] is not None:
                    before = new_vals[field]
                    new_vals[field] = self._round_quantity(before, 4, f"Create {field}")
                    _logger.info(
                        "[CREATE] %s: %.10f -> %.4f",
                        field, before, new_vals[field]
                    )
            
            processed_vals_list.append(new_vals)
        
        # Call the original create with the processed values
        records = super().create(processed_vals_list)
        _logger.info("[CREATE] Created %d records", len(records))
        return records

    def write(self, vals):
        """Override write to ensure all quantity values are properly rounded to 4 decimal places."""
        _logger.info("[WRITE] Writing to %d records with values: %s", len(self), vals)
        
        # Process quantity fields if they're being written
        qty_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
        for field in qty_fields:
            if field in vals and vals[field] is not None:
                before = vals[field]
                vals[field] = self._round_quantity(before, 4, f"Write {field}")
                _logger.info(
                    "[WRITE] %s: %.10f -> %.4f",
                    field, before, vals[field]
                )
        
        return super().write(vals)

    @api.model
    def default_get(self, fields_list):
        """Override default_get to ensure default quantities are properly rounded."""
        _logger.info("[DEFAULT_GET] Getting defaults for fields: %s", fields_list)
        
        res = super().default_get(fields_list)
        
        # Process quantity fields if they're in the result
        qty_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
        for field in qty_fields:
            if field in res and res[field] is not None:
                before = res[field]
                res[field] = self._round_quantity(before, 4, f"Default {field}")
                _logger.info(
                    "[DEFAULT_GET] %s: %.10f -> %.4f",
                    field, before, res[field]
                )
        
        return res
