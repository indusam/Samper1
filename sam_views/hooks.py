# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Hook ejecutado después de la instalación del módulo.
    Corrige el template account.document_tax_totals_copy_1 creado con Studio
    que usa 'formatted_amount' (incompatible con Odoo 18) y lo reemplaza
    con 'base_amount_currency' usando el widget monetary.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Buscar el template problemático creado con Studio
    template = env['ir.ui.view'].search([
        ('name', '=', 'account.document_tax_totals_copy_1'),
        ('type', '=', 'qweb')
    ], limit=1)

    if template:
        _logger.info("Corrigiendo template account.document_tax_totals_copy_1 para Odoo 18...")

        # El arch del template original tiene código incompatible con Odoo 18
        # Lo reemplazamos con un template que usa la estructura correcta
        old_arch = str(template.arch_db or '')

        # Verificar si el template tiene el problema de formatted_amount
        if "formatted_amount" in old_arch:
            _logger.info("Template contiene referencias a 'formatted_amount' - aplicando corrección...")

            # Reemplazar todas las referencias a formatted_amount
            # Caso 1: subtotal['formatted_amount']
            new_arch = old_arch.replace(
                "subtotal['formatted_amount']",
                "subtotal.get('base_amount_currency', subtotal.get('amount', 0))"
            )

            # Caso 2: t-esc a t-out y añadir t-options para monetary widget
            # Esta es una corrección aproximada - puede necesitar ajustes manuales
            if 't-esc="subtotal' in new_arch and 'formatted_amount' not in new_arch:
                # Reemplazar t-esc por t-out y añadir t-options
                new_arch = new_arch.replace(
                    't-esc="subtotal.get(',
                    't-out="subtotal.get('
                )

                # Añadir t-options después del span si no existe
                if 't-options' not in new_arch and 'oe_subtotal_footer_separator' in new_arch:
                    # Buscar el span con oe_subtotal_footer_separator y añadir t-options
                    import re
                    pattern = r'(<span[^>]*oe_subtotal_footer_separator[^>]*)(/>)'
                    replacement = r'\1 t-options=\'{"widget": "monetary", "display_currency": o.currency_id}\'\2'
                    new_arch = re.sub(pattern, replacement, new_arch)

            # Actualizar el template
            template.write({'arch_db': new_arch})
            _logger.info("Template corregido exitosamente")
        else:
            _logger.info("Template no contiene 'formatted_amount' - no se requiere corrección")
    else:
        _logger.info("Template account.document_tax_totals_copy_1 no encontrado - puede que ya haya sido eliminado o corregido")


def uninstall_hook(cr, registry):
    """
    Hook ejecutado antes de desinstalar el módulo.
    Podemos dejar el template corregido o eliminarlo aquí.
    """
    _logger.info("Desinstalando sam_views - el template corregido permanecerá en el sistema")
