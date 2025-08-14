from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class QuantityValidatorAction(models.Model):
    _name = 'quantity.validator.action'
    _description = 'Quantity Validator Server Actions'

    @api.model
    def _fix_existing_small_quantities(self, model_name, quantity_field='product_qty'):
        """Fix existing records with very small quantities."""
        try:
            model = self.env[model_name]
            if not model._fields.get(quantity_field):
                return 0
                
            domain = [
                (quantity_field, '!=', 0),
                (quantity_field, '!=', False),
                '&',
                (quantity_field, '<=', 0.0001),
                (quantity_field, '>=', -0.0001)
            ]
            
            records = model.search(domain)
            if not records:
                return 0
                
            _logger.info("Found %s records with small quantities in %s", len(records), model_name)
            records.write({quantity_field: 0})
            return len(records)
            
        except Exception as e:
            _logger.error("Error fixing small quantities in %s: %s", model_name, str(e))
            return 0

    @api.model
    def validate_quantities(self):
        """Server action to validate quantities across all models."""
        _logger.info("Starting quantity validation process")
        
        # Define models and their quantity fields
        models_config = [
            ('stock.quant', 'quantity'),
            ('stock.move', 'product_uom_qty'),
            ('stock.move.line', 'qty_done'),
            ('mrp.production', 'product_qty'),
            ('stock.lot', 'product_qty'),
            ('stock.picking', None)  # Handled by stock.move
        ]
        
        fixed_counts = {}
        
        # First, fix existing small quantities
        for model_name, qty_field in models_config:
            if qty_field:
                count = self._fix_existing_small_quantities(model_name, qty_field)
                if count > 0:
                    fixed_counts[model_name] = count
        
        # Then run model-specific validations
        for model_name, _ in models_config:
            try:
                model = self.env[model_name]
                if hasattr(model, '_validate_quantities'):
                    _logger.info("Running validation for model: %s", model_name)
                    model._validate_quantities()
            except Exception as e:
                _logger.error("Error in %s._validate_quantities: %s", model_name, str(e))
        
        _logger.info("Quantity validation process completed")
        
        # Create a more detailed success message
        message = "Quantity validation completed successfully"
        if fixed_counts:
            details = ", ".join([f"{model}: {count}" for model, count in fixed_counts.items()])
            message = f"Fixed small quantities in: {details}"
        
        # Return a simple success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': message,
                'sticky': False,
                'type': 'success',
            }
        }
