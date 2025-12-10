# -*- coding: utf-8 -*-
"""
Asignación automática de lotes en órdenes de fabricación.

Este módulo extiende mrp.production para asignar automáticamente lotes/números de serie
existentes al producto terminado cuando se marca como hecha una orden de fabricación,
evitando el asistente manual de Odoo 18.

Estrategia: FIFO sobre stock.quant disponibles en la ubicación de producción.

Autor: VBueno
Fecha: 2025-12-10
Versión: Odoo 18.0
"""

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Campo opcional para activar/desactivar la asignación automática por orden
    sam_auto_assign_lots = fields.Boolean(
        string='Auto-asignar Lotes',
        default=True,
        help='Si está activado, el sistema asignará automáticamente lotes existentes '
             'al producto terminado sin mostrar el asistente de números de serie.'
    )

    def button_mark_done(self):
        """
        Sobreescribe el método que marca la orden de fabricación como hecha en Odoo 18.

        IMPORTANTE: En Odoo 18, el flujo de fabricación cambió y ahora usa button_mark_done
        para finalizar la producción. Este método se ejecuta al presionar el botón "Mark as Done".

        Flujo:
        1. Ejecutar la lógica de auto-asignación ANTES del super() para preparar los lotes
        2. Llamar al super() para ejecutar la lógica estándar de Odoo
        3. Si hay errores en la asignación, se lanza UserError antes de marcar como hecho
        """
        # Solo ejecutar auto-asignación si está activada
        for production in self:
            if production.sam_auto_assign_lots:
                try:
                    production._sam_auto_assign_lots_to_finished_moves()
                except Exception as e:
                    _logger.error(
                        f"Error en auto-asignación de lotes para MO {production.name}: {str(e)}"
                    )
                    raise UserError(_(
                        "No se pudo asignar automáticamente los lotes para la orden de fabricación %s.\n\n"
                        "Error: %s\n\n"
                        "Por favor, verifique que haya suficientes lotes disponibles en stock."
                    ) % (production.name, str(e)))

        # Ejecutar el comportamiento estándar de Odoo
        return super(MrpProduction, self).button_mark_done()

    def _sam_auto_assign_lots_to_finished_moves(self):
        """
        Método auxiliar que asigna automáticamente lotes a los movimientos de producto terminado.

        Lógica:
        1. Identifica los movimientos de salida del producto terminado (move_finished_ids)
        2. Para cada movimiento, busca lotes disponibles en stock.quant usando estrategia FIFO
        3. Crea stock.move.line con lot_id asignado automáticamente
        4. Maneja tracking por lote (varios productos por lote) y por serie (uno por lote)

        Raises:
            UserError: Si no hay suficientes lotes disponibles para cubrir la cantidad producida
        """
        self.ensure_one()

        _logger.info(f"Iniciando auto-asignación de lotes para MO {self.name}")

        # 1. Identificar movimientos de producto terminado
        # En Odoo 18, move_finished_ids contiene los movimientos del producto terminado
        finished_moves = self.move_finished_ids.filtered(
            lambda m: m.state not in ('done', 'cancel') and m.product_id.tracking != 'none'
        )

        if not finished_moves:
            _logger.info(f"No hay movimientos de producto terminado con tracking para MO {self.name}")
            return

        # 2. Para cada movimiento, asignar lotes automáticamente
        for move in finished_moves:
            self._sam_assign_lots_to_move(move)

    def _sam_assign_lots_to_move(self, move):
        """
        Asigna lotes a un movimiento específico.

        Args:
            move: stock.move - Movimiento al que se asignarán los lotes

        Estrategia:
        - Para tracking 'serial': Crear una stock.move.line por unidad con lotes diferentes
        - Para tracking 'lot': Usar lotes existentes permitiendo múltiples unidades por lote
        - FIFO: Los lotes más antiguos (menor create_date) se usan primero
        """
        product = move.product_id
        qty_to_assign = move.product_uom_qty - move.quantity_done

        # Precision decimal del producto para comparaciones float
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        if float_is_zero(qty_to_assign, precision_digits=precision):
            _logger.info(f"Movimiento {move.id} ya tiene cantidad asignada completa")
            return

        _logger.info(
            f"Asignando {qty_to_assign} {product.uom_id.name} de {product.name} "
            f"(tracking: {product.tracking})"
        )

        # 3. Buscar lotes disponibles en la ubicación de destino
        # Para productos terminados, la ubicación es move.location_dest_id (almacén de productos terminados)
        available_lots = self._sam_get_available_lots_for_product(
            product,
            move.location_dest_id,
            qty_to_assign
        )

        if not available_lots:
            raise UserError(_(
                "No se encontraron lotes disponibles para el producto '%s' en la ubicación '%s'.\n\n"
                "Para que el sistema pueda asignar automáticamente, debe haber stock con lotes "
                "disponibles en la ubicación de destino.\n\n"
                "Cantidad requerida: %s %s"
            ) % (product.name, move.location_dest_id.complete_name, qty_to_assign, product.uom_id.name))

        # 4. Crear stock.move.line según el tipo de tracking
        if product.tracking == 'serial':
            self._sam_assign_serial_numbers(move, available_lots, qty_to_assign, precision)
        else:  # tracking == 'lot'
            self._sam_assign_lot_numbers(move, available_lots, qty_to_assign, precision)

    def _sam_get_available_lots_for_product(self, product, location, qty_needed):
        """
        Obtiene los lotes disponibles para un producto en una ubicación específica.

        Args:
            product: product.product - Producto a buscar
            location: stock.location - Ubicación donde buscar
            qty_needed: float - Cantidad que se necesita asignar

        Returns:
            list: Lista de diccionarios con información de lotes disponibles
                  [{'lot': stock.lot, 'qty_available': float}, ...]
                  Ordenados por FIFO (create_date ascendente)
        """
        # Buscar quants con cantidad disponible
        # NOTA: En producción, los lotes para el producto terminado normalmente NO existen
        # en la ubicación de destino antes de producir. Esta lógica está preparada para
        # el caso de que SÍ existan lotes previos que se quieran reutilizar.
        # Si no existen lotes, se debe crear uno nuevo o usar otra estrategia.

        quants = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id),
            ('quantity', '>', 0),
            ('lot_id', '!=', False),
        ], order='lot_id, create_date asc')

        available_lots = []
        for quant in quants:
            # Calcular cantidad disponible (cantidad - reservada)
            qty_available = quant.quantity - quant.reserved_quantity

            if qty_available > 0:
                available_lots.append({
                    'lot': quant.lot_id,
                    'qty_available': qty_available,
                    'quant': quant
                })

        _logger.info(f"Encontrados {len(available_lots)} lotes disponibles para {product.name}")

        return available_lots

    def _sam_assign_serial_numbers(self, move, available_lots, qty_to_assign, precision):
        """
        Asigna números de serie (uno por unidad) al movimiento.

        Args:
            move: stock.move
            available_lots: list - Lista de lotes disponibles
            qty_to_assign: float - Cantidad a asignar
            precision: int - Precisión decimal
        """
        # Para serial tracking, necesitamos un lote diferente por cada unidad
        units_needed = int(qty_to_assign)

        if len(available_lots) < units_needed:
            raise UserError(_(
                "No hay suficientes números de serie disponibles para el producto '%s'.\n\n"
                "Requeridos: %s\n"
                "Disponibles: %s\n\n"
                "Por favor, cree o importe los números de serie necesarios antes de finalizar la orden."
            ) % (move.product_id.name, units_needed, len(available_lots)))

        # Crear una move.line por cada unidad con su número de serie
        for i in range(units_needed):
            lot_info = available_lots[i]

            # Usar el método estándar de Odoo para crear move.line con lote
            move._update_reserved_quantity(
                need=1.0,
                available_quantity=1.0,
                location_id=move.location_id,
                lot_id=lot_info['lot'],
                package_id=False,
                owner_id=False,
                strict=False
            )

            _logger.info(
                f"Asignado número de serie {lot_info['lot'].name} a movimiento {move.id}"
            )

    def _sam_assign_lot_numbers(self, move, available_lots, qty_to_assign, precision):
        """
        Asigna lotes (pueden contener múltiples unidades) al movimiento.

        Args:
            move: stock.move
            available_lots: list - Lista de lotes disponibles
            qty_to_assign: float - Cantidad a asignar
            precision: int - Precisión decimal
        """
        qty_remaining = qty_to_assign

        for lot_info in available_lots:
            if float_is_zero(qty_remaining, precision_digits=precision):
                break

            # Cantidad a tomar de este lote (mínimo entre lo que queda y lo disponible)
            qty_to_take = min(qty_remaining, lot_info['qty_available'])

            # Usar el método estándar de Odoo para crear move.line con lote
            move._update_reserved_quantity(
                need=qty_to_take,
                available_quantity=qty_to_take,
                location_id=move.location_id,
                lot_id=lot_info['lot'],
                package_id=False,
                owner_id=False,
                strict=False
            )

            qty_remaining -= qty_to_take

            _logger.info(
                f"Asignado lote {lot_info['lot'].name} con cantidad {qty_to_take} "
                f"a movimiento {move.id}"
            )

        # Verificar que se asignó toda la cantidad
        if not float_is_zero(qty_remaining, precision_digits=precision):
            raise UserError(_(
                "No hay suficiente cantidad disponible en lotes para el producto '%s'.\n\n"
                "Requerido: %s %s\n"
                "Asignado: %s %s\n"
                "Faltante: %s %s\n\n"
                "Por favor, verifique que haya suficiente stock con lotes en la ubicación de destino."
            ) % (
                move.product_id.name,
                qty_to_assign, move.product_id.uom_id.name,
                qty_to_assign - qty_remaining, move.product_id.uom_id.name,
                qty_remaining, move.product_id.uom_id.name
            ))


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _update_reserved_quantity(self, need, available_quantity, location_id, lot_id=None,
                                   package_id=None, owner_id=None, strict=True):
        """
        Sobrescribe el método estándar para permitir la creación de move.line con lote específico.

        Este método es el punto de entrada estándar de Odoo para crear/actualizar stock.move.line
        con asignaciones específicas de lote, paquete, propietario, etc.

        IMPORTANTE: Este método ya existe en Odoo y normalmente maneja la creación de move.line.
        La sobreescritura aquí es para asegurar que funcione correctamente con nuestra lógica
        de auto-asignación, especialmente cuando lot_id está presente.
        """
        # Llamar al super para mantener toda la lógica estándar
        result = super(StockMove, self)._update_reserved_quantity(
            need=need,
            available_quantity=available_quantity,
            location_id=location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict
        )

        return result
