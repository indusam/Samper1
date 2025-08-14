from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)

class QuantityValidatorAction(models.Model):
    _name = 'quantity.validator.action'
    _description = 'Quantity Validator Server Actions'

    @api.model
    def validate_quantities(self):
        """Server action to validate quantities across all models."""
        _logger.info("Starting quantity validation process")
        
        # Get all models that need quantity validation
        models_to_check = [
            'stock.quant',
            'stock.move',
            'mrp.production',
            'stock.lot',
            'stock.picking'
        ]
        
        for model_name in models_to_check:
            try:
                model = self.env[model_name]
                if hasattr(model, '_validate_quantities'):
                    _logger.info("Validating quantities for model: %s", model_name)
                    model._validate_quantities()
            except Exception as e:
                _logger.error("Error validating quantities for model %s: %s", model_name, str(e))
        
        _logger.info("Quantity validation process completed")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Quantity validation completed successfully'),
                'sticky': False,
                'type': 'success',
            }
        }
