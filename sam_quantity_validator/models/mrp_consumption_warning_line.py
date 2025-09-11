from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class MrpConsumptionWarningLine(models.TransientModel):
    """Extend mrp.consumption.warning.line to modify float fields precision and handle quantity adjustments.
    
    This is a transient model used for consumption warnings in manufacturing.
    """
    
    _inherit = 'mrp.consumption.warning.line'
    
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
    
    def _round_quantity(self, qty):
        """Helper method to round quantity to 4 decimal places and handle very small values."""
        try:
            rounded = round(float(qty or 0.0), 4)
            return 0.0 if abs(rounded) < 0.0001 else rounded
        except (TypeError, ValueError) as e:
            _logger.error("Error rounding quantity %s: %s", qty, str(e))
            return 0.0
    
    @api.model
    def create(self, vals):
        """Override create to ensure values are properly rounded to 4 decimal places."""
        # Round quantity fields to 4 decimal places if they exist in vals
        float_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
        
        for field in float_fields:
            if field in vals and vals[field] is not None:
                vals[field] = self._round_quantity(vals[field])
        
        return super().create(vals)
    
    def write(self, vals):
        """Override write to ensure values are properly rounded to 4 decimal places."""
        # Round quantity fields to 4 decimal places if they exist in vals
        float_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
        
        for field in float_fields:
            if field in vals and vals[field] is not None:
                vals[field] = self._round_quantity(vals[field])
        
        return super().write(vals)
    
    @api.model
    def default_get(self, fields_list):
        """Override default_get to ensure quantities are properly rounded when the wizard opens."""
        res = super().default_get(fields_list)
        
        # Round the quantities when they're first loaded
        for field in ['product_consumed_qty_uom', 'product_expected_qty_uom']:
            if field in res and res[field] is not None:
                res[field] = self._round_quantity(res[field])
        
        return res
