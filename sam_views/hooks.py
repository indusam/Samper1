# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Hook ejecutado después de la instalación del módulo.
    Busca y desactiva templates que usen 'formatted_amount' (incompatible con Odoo 18).

    El template será desactivado para que Odoo use el template estándar de Odoo 18.
    Esto es más seguro que intentar modificar el XML del template de Studio.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Buscar templates que contengan 'formatted_amount' en su código
    # Esto incluye el template account.document_tax_totals_copy_1 y cualquier otro similar
    all_templates = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        '|',
        ('name', 'ilike', 'tax_totals'),
        ('key', 'ilike', 'tax_totals')
    ])

    templates_fixed = 0

    for template in all_templates:
        old_arch = str(template.arch_db or '')

        # Verificar si el template tiene el problema de formatted_amount
        if "formatted_amount" in old_arch and "subtotal" in old_arch:
            _logger.warning(
                f"Template incompatible con Odoo 18 encontrado: {template.name} (ID: {template.id})"
            )

            try:
                # OPCIÓN 1: Intentar corregir el template
                new_arch = old_arch.replace(
                    "subtotal['formatted_amount']",
                    "subtotal.get('base_amount_currency', 0)"
                )

                # Reemplazar t-esc por t-out para usar el widget monetary
                new_arch = new_arch.replace(
                    't-esc="subtotal.get(\'base_amount_currency\'',
                    't-out="subtotal.get(\'base_amount_currency\''
                )
                new_arch = new_arch.replace(
                    't-esc="subtotal.get("base_amount_currency"',
                    't-out="subtotal.get("base_amount_currency"'
                )

                # Añadir t-options si falta (solo si el span tiene oe_subtotal_footer_separator)
                import re
                if 'oe_subtotal_footer_separator' in new_arch and 't-options' not in new_arch:
                    # Buscar spans con t-out y base_amount_currency
                    pattern = r'(<span[^>]*t-out="subtotal\.get\([\'"]base_amount_currency[\'"][^>]*)(/>|></span>)'

                    def add_options(match):
                        opening = match.group(1)
                        closing = match.group(2)
                        # Si ya tiene t-options, no hacer nada
                        if 't-options' in opening:
                            return match.group(0)
                        # Añadir t-options antes del cierre
                        return f'{opening} t-options=\'{{"widget": "monetary", "display_currency": o.currency_id}}\'{closing}'

                    new_arch = re.sub(pattern, add_options, new_arch)

                if new_arch != old_arch:
                    template.write({'arch_db': new_arch})
                    templates_fixed += 1
                    _logger.info(
                        f"✓ Template corregido: {template.name} (ID: {template.id})"
                    )
                else:
                    _logger.warning(
                        f"Template no pudo ser corregido automáticamente: {template.name} (ID: {template.id})"
                    )

            except Exception as e:
                _logger.error(
                    f"Error al corregir template {template.name} (ID: {template.id}): {str(e)}"
                )
                _logger.info(
                    f"Desactivando template problemático: {template.name} (ID: {template.id})"
                )
                try:
                    # Si falla la corrección, desactivar el template
                    template.write({'active': False})
                    templates_fixed += 1
                    _logger.info(
                        f"✓ Template desactivado: {template.name} (ID: {template.id})"
                    )
                except Exception as e2:
                    _logger.error(
                        f"No se pudo desactivar el template {template.name}: {str(e2)}"
                    )

    if templates_fixed > 0:
        _logger.info(
            f"✓ Corrección completada: {templates_fixed} template(s) procesado(s)"
        )
    else:
        _logger.info("No se encontraron templates que requieran corrección")


def uninstall_hook(cr, registry):
    """
    Hook ejecutado antes de desinstalar el módulo.
    Podemos dejar el template corregido o eliminarlo aquí.
    """
    _logger.info("Desinstalando sam_views - el template corregido permanecerá en el sistema")
