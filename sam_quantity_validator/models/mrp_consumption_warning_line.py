from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class MrpConsumptionWarningLine(models.Model):
    """Extend mrp.consumption.warning.line to modify float fields precision."""
    
    _inherit = 'mrp.consumption.warning.line'
    
    # Override fields to set 4 decimal places
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
    
    @api.model
    def create(self, vals):
        """Override create to ensure values are properly rounded to 4 decimal places."""
        # Round quantity fields to 4 decimal places if they exist in vals
        float_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
        
        for field in float_fields:
            if field in vals and vals[field] is not None:
                try:
                    vals[field] = round(float(vals[field]), 4)
                except (TypeError, ValueError) as e:
                    _logger.error(
                        "%s: Error rounding %s value %s: %s",
                        self._name,
                        field,
                        vals.get(field),
                        str(e)
                    )
                    # Set to 0.0 in case of error to avoid issues
                    vals[field] = 0.0
        
        return super().create(vals)
    
    def write(self, vals):
        """Override write to ensure values are properly rounded to 4 decimal places."""
        # Round quantity fields to 4 decimal places if they exist in vals
        float_fields = ['product_consumed_qty_uom', 'product_expected_qty_uom']
        
        for field in float_fields:
            if field in vals and vals[field] is not None:
                try:
                    vals[field] = round(float(vals[field]), 4)
                except (TypeError, ValueError) as e:
                    _logger.error(
                        "%s: Error rounding %s value %s: %s",
                        self._name,
                        field,
                        vals.get(field),
                        str(e)
                    )
                    # Set to 0.0 in case of error to avoid issues
                    vals[field] = 0.0
        
        return super().write(vals)
