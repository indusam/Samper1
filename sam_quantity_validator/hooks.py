from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """Corrección masiva de datos existentes al instalar/actualizar el módulo."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Lista de modelos y campos a verificar
    models_to_check = [
        ('stock.lot', 'product_qty'),
        ('stock.quant', 'quantity'),
        ('stock.move', 'quantity_done'),
        ('mrp.production', 'product_qty'),
        ('mrp.production', 'qty_produced')
    ]
    
    for model, field in models_to_check:
        try:
            # Buscar registros con cantidades muy pequeñas
            records = env[model].search([
                (field, '!=', False),
                (field, '!=', 0),
                (field, '<', 0.0001)
            ])
            
            if records:
                _logger.info("Ajustando %d registros en %s.%s", len(records), model, field)
                records.write({field: 0})
                
        except Exception as e:
            _logger.error("Error al actualizar %s.%s: %s", model, field, str(e))