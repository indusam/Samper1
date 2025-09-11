from odoo import models, fields, api, _
import logging

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
    
    def _round_quantity(self, qty, context_info=""):
        """Helper method to round quantity to 4 decimal places and handle very small values."""
        try:
            original = float(qty or 0.0)
            rounded = round(original, 4)
            result = 0.0 if abs(rounded) < 0.0001 else rounded
            
            # Enhanced logging with more context
            _logger.info(
                "[QUANTITY ROUNDING] %s\n"
                "  - Original: %.10f\n"
                "  - Rounded:  %.10f\n"
                "  - Final:    %.10f\n"
                "  - Type:     %s",
                context_info or "No context",
                original,
                rounded,
                result,
                type(qty).__name__
            )
            
            return result
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
        """Override create to handle batch creation and ensure values are properly rounded."""
        _logger.info("[CREATE] Starting batch create with %d records", len(vals_list))
        
        # Process each set of values in the batch
        for index, vals in enumerate(vals_list):
            _logger.info("[CREATE] Processing record %d: %s", index + 1, vals)
            
            # Round quantity fields to 4 decimal places if they exist in vals
            float_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
            for field in float_fields:
                if field in vals and vals[field] is not None:
                    before = vals[field]
                    vals[field] = self._round_quantity(before, f"Create {field}")
                    _logger.info(
                        "[CREATE] Field '%s' transformed: %s -> %s",
                        field, before, vals[field]
                    )
        
        result = super().create(vals_list)
        _logger.info("[CREATE] Created %d records: %s", len(result), result.ids)
        return result
    
    def write(self, vals):
        """Override write to ensure values are properly rounded to 4 decimal places."""
        _logger.info("[WRITE] Original values: %s", vals)
        
        # Round quantity fields to 4 decimal places if they exist in vals
        float_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
        for field in float_fields:
            if field in vals and vals[field] is not None:
                vals[field] = self._round_quantity(vals[field], f"Write {field}")
        
        _logger.info("[WRITE] Processed values: %s", vals)
        return super().write(vals)
    
    @api.model
    def default_get(self, fields_list):
        """Override default_get to ensure quantities are properly rounded when the wizard opens."""
        res = super().default_get(fields_list)
        _logger.info("[DEFAULT_GET] Original values: %s", res)
        
        # Round the quantities when they're first loaded
        for field in ['product_consumed_qty_uom', 'product_expected_qty_uom']:
            if field in res and res[field] is not None:
                res[field] = self._round_quantity(res[field], f"Default {field}")
        
        _logger.info("[DEFAULT_GET] Processed values: %s", res)
        return res
