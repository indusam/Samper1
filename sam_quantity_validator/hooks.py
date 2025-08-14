from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """ Corrección masiva de datos existentes """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    models_to_check = [
        ('stock.lot', 'product_qty'),
        ('stock.quant', 'quantity'),
        ('stock.move', 'quantity_done'),
        ('mrp.production', 'product_qty'),
        ('mrp.production', 'qty_produced')
    ]
    
    for model, field in models_to_check:
        try:
            records = env[model].search([
                (field, '>', 0),
                (field, '<', 0.0001)
            ])
            if records:
                records.write({field: 0})
                _logger.info(f"Corregidas {len(records)} registros en {model}.{field}")
        except Exception as e:
            _logger.error(f"Error corrigiendo {model}.{field}: {str(e)}")