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
                return 0, []
                
            domain = [
                (quantity_field, '!=', 0),
                (quantity_field, '!=', False),
                '&',
                (quantity_field, '<=', 0.0001),
                (quantity_field, '>=', -0.0001)
            ]
            
            records = model.search(domain)
            if not records:
                return 0, []
                
            _logger.info("Found %s records with small quantities in %s", len(records), model_name)
            
            # Process records one by one to handle potential validation errors
            fixed_count = 0
            error_records = []
            
            for record in records:
                try:
                    # Create a copy of the record's values to avoid modifying the original
                    vals = {quantity_field: 0}
                    # For stock.quant, we need to handle the in_date field
                    if model_name == 'stock.quant' and hasattr(record, 'in_date'):
                        vals['in_date'] = record.in_date or fields.Datetime.now()
                    
                    # Update the record
                    record.write(vals)
                    fixed_count += 1
                except Exception as e:
                    error_msg = f"{model_name}({record.id}): {str(e)[:100]}"
                    _logger.warning("Could not update %s: %s", model_name, error_msg)
                    error_records.append(error_msg)
                    continue
            
            return fixed_count, error_records
            
        except Exception as e:
            error_msg = str(e)
            _logger.error("Error processing %s: %s", model_name, error_msg)
            return 0, [f"{model_name}: {error_msg}"]

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
        all_errors = []
        
        # First, fix existing small quantities
        for model_name, qty_field in models_config:
            if qty_field:
                count, errors = self._fix_existing_small_quantities(model_name, qty_field)
                if count > 0:
                    fixed_counts[model_name] = count
                if errors:
                    all_errors.extend(errors)
        
        # Then run model-specific validations
        for model_name, _ in models_config:
            try:
                model = self.env[model_name]
                if hasattr(model, '_validate_quantities'):
                    _logger.info("Running validation for model: %s", model_name)
                    model._validate_quantities()
            except Exception as e:
                error_msg = f"Error in {model_name}._validate_quantities: {str(e)[:200]}"
                _logger.error(error_msg)
                all_errors.append(error_msg)
        
        _logger.info("Quantity validation process completed")
        
        # Prepare the result message
        message_parts = []
        
        if fixed_counts:
            details = ", ".join([f"{model}: {count}" for model, count in fixed_counts.items()])
            message_parts.append(f"Fixed small quantities in: {details}")
        
        if all_errors:
            error_count = len(all_errors)
            error_summary = "\n".join([f"- {e}" for e in all_errors[:5]])  # Show first 5 errors
            if error_count > 5:
                error_summary += f"\n... and {error_count - 5} more errors"
            message_parts.append(f"Encountered {error_count} errors:\n{error_summary}")
        
        if not message_parts:
            message_parts.append("No quantities needed adjustment")
        
        # Return the result
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Quantity Validation Complete',
                'message': "\n\n".join(message_parts),
                'sticky': True,  # Keep the message visible until dismissed
                'type': 'success' if not all_errors else 'warning',
            }
        }
