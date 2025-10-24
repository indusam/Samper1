# -*- coding: utf-8 -*-
"""
Post-installation hooks para sam_quantity_validator
Actualizado para Odoo v18
"""

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Corrección masiva de datos existentes al instalar/actualizar el módulo.

    Este hook se ejecuta después de la instalación o actualización del módulo
    y ajusta a cero todas las cantidades menores a 0.0001 en los modelos
    especificados.

    Args:
        cr: Database cursor
        registry: Odoo registry object
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Lista de modelos y campos a verificar
    models_to_check = [
        ('stock.lot', 'product_qty'),
        ('stock.quant', 'quantity'),
        ('stock.move', 'quantity_done'),
        ('mrp.production', 'product_qty'),
        ('mrp.production', 'qty_produced')
    ]

    total_adjusted = 0

    for model, field in models_to_check:
        try:
            # Buscar registros con cantidades muy pequeñas (pero no cero)
            records = env[model].search([
                (field, '!=', False),
                (field, '!=', 0),
                (field, '<', 0.0001),
                (field, '>', -0.0001)  # También manejar valores negativos muy pequeños
            ])

            if records:
                count = len(records)
                _logger.info(
                    "Ajustando %d registros en %s.%s con valores menores a 0.0001",
                    count,
                    model,
                    field
                )
                records.write({field: 0})
                total_adjusted += count

        except Exception as e:
            _logger.error(
                "Error al actualizar %s.%s: %s",
                model,
                field,
                str(e)
            )

    if total_adjusted > 0:
        _logger.info(
            "Post-init hook completado: %d registros ajustados en total",
            total_adjusted
        )
    else:
        _logger.info("Post-init hook completado: No se encontraron registros que ajustar")