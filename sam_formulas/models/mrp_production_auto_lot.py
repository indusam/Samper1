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
        Método auxiliar que asigna automáticamente lotes a los movimientos de producto terminado
        y componentes consumidos.

        Lógica:
        1. Identifica los movimientos de componentes consumidos (move_raw_ids) con tracking
        2. Identifica los movimientos de producto terminado (move_finished_ids) con tracking
        3. Para cada movimiento, busca lotes disponibles en stock.quant usando estrategia FIFO
        4. Crea stock.move.line con lot_id asignado automáticamente
        5. Maneja tracking por lote (varios productos por lote) y por serie (uno por lote)

        Raises:
            UserError: Si no hay suficientes lotes disponibles para cubrir la cantidad producida
        """
        self.ensure_one()

        _logger.info(f"Iniciando auto-asignación de lotes para MO {self.name}")

        # 1. Asignar lotes a componentes consumidos (move_raw_ids)
        # IMPORTANTE: Los componentes deben tener lotes asignados ANTES del producto terminado
        raw_moves = self.move_raw_ids.filtered(
            lambda m: m.state not in ('done', 'cancel') and m.product_id.tracking != 'none'
        )

        _logger.info(f"Movimientos de componentes con tracking: {len(raw_moves)}")
        for move in raw_moves:
            self._sam_assign_lots_to_raw_move(move)

        # 2. Asignar lotes a producto terminado (move_finished_ids)
        finished_moves = self.move_finished_ids.filtered(
            lambda m: m.state not in ('done', 'cancel') and m.product_id.tracking != 'none'
        )

        _logger.info(f"Movimientos de producto terminado con tracking: {len(finished_moves)}")
        for move in finished_moves:
            self._sam_assign_lots_to_finished_move(move)

    def _sam_assign_lots_to_raw_move(self, move):
        """
        Asigna lotes a un movimiento de componente (materia prima).

        Args:
            move: stock.move - Movimiento de componente al que se asignarán los lotes

        Estrategia:
        - Busca lotes en la ubicación de ORIGEN (location_id) que es donde están los componentes
        - Para tracking 'serial': Crear una stock.move.line por unidad con lotes diferentes
        - Para tracking 'lot': Usar lotes existentes permitiendo múltiples unidades por lote
        - FIFO: Los lotes más antiguos (menor create_date) se usan primero
        """
        product = move.product_id
        # En Odoo 18, el campo correcto es 'quantity' no 'quantity_done'
        qty_to_assign = move.product_uom_qty - move.quantity

        # Precision decimal del producto para comparaciones float
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        if float_is_zero(qty_to_assign, precision_digits=precision):
            _logger.info(f"Movimiento {move.id} ya tiene cantidad asignada completa")
            return

        _logger.info(
            f"Asignando {qty_to_assign} {product.uom_id.name} de componente {product.name} "
            f"(tracking: {product.tracking})"
        )

        # Para componentes, buscar lotes en la ubicación de ORIGEN (donde están almacenados)
        available_lots = self._sam_get_available_lots_for_product(
            product,
            move.location_id,  # Ubicación de origen (stock)
            qty_to_assign
        )

        if not available_lots:
            raise UserError(_(
                "No se encontraron lotes disponibles para el componente '%s' en la ubicación '%s'.\n\n"
                "Para que el sistema pueda asignar automáticamente, debe haber stock con lotes "
                "disponibles en la ubicación de origen.\n\n"
                "Cantidad requerida: %s %s"
            ) % (product.name, move.location_id.complete_name, qty_to_assign, product.uom_id.name))

        # Crear stock.move.line según el tipo de tracking
        if product.tracking == 'serial':
            self._sam_assign_serial_numbers(move, available_lots, qty_to_assign, precision)
        else:  # tracking == 'lot'
            self._sam_assign_lot_numbers(move, available_lots, qty_to_assign, precision)

    def _sam_assign_lots_to_finished_move(self, move):
        """
        Asigna lotes a un movimiento de producto terminado.

        Args:
            move: stock.move - Movimiento de producto terminado al que se asignarán los lotes

        Estrategia:
        - Para productos terminados, NO buscamos lotes existentes porque se están produciendo
        - En su lugar, CREAMOS lotes nuevos automáticamente
        - Para tracking 'serial': Crear un serial por unidad
        - Para tracking 'lot': Crear un lote para toda la cantidad
        """
        product = move.product_id
        # En Odoo 18, el campo correcto es 'quantity' no 'quantity_done'
        qty_to_assign = move.product_uom_qty - move.quantity

        # Precision decimal del producto para comparaciones float
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        if float_is_zero(qty_to_assign, precision_digits=precision):
            _logger.info(f"Movimiento {move.id} ya tiene cantidad asignada completa")
            return

        _logger.info(
            f"Creando lotes para {qty_to_assign} {product.uom_id.name} de producto terminado {product.name} "
            f"(tracking: {product.tracking})"
        )

        # Para productos terminados, CREAR lotes nuevos en lugar de buscar existentes
        if product.tracking == 'serial':
            self._sam_create_serial_numbers_for_finished(move, qty_to_assign, precision)
        else:  # tracking == 'lot'
            self._sam_create_lot_for_finished(move, qty_to_assign, precision)

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

    def _sam_create_serial_numbers_for_finished(self, move, qty_to_assign, precision):
        """
        Crea números de serie automáticamente para el producto terminado.

        Args:
            move: stock.move - Movimiento de producto terminado
            qty_to_assign: float - Cantidad a asignar (número de seriales a crear)
            precision: int - Precisión decimal
        """
        units_needed = int(qty_to_assign)

        for i in range(units_needed):
            # Crear un nuevo número de serie
            serial_name = self._sam_generate_lot_name(move.product_id, is_serial=True)

            new_serial = self.env['stock.lot'].create({
                'name': serial_name,
                'product_id': move.product_id.id,
                'company_id': self.env.company.id,
            })

            # Crear move.line con el serial
            self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': move.product_id.id,
                'lot_id': new_serial.id,
                'quantity': 1.0,
                'product_uom_id': move.product_id.uom_id.id,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
            })

            _logger.info(
                f"Creado número de serie {serial_name} para producto terminado {move.product_id.name}"
            )

    def _sam_create_lot_for_finished(self, move, qty_to_assign, precision):
        """
        Crea un lote automáticamente para el producto terminado.

        Args:
            move: stock.move - Movimiento de producto terminado
            qty_to_assign: float - Cantidad a asignar
            precision: int - Precisión decimal
        """
        # Crear un nuevo lote
        lot_name = self._sam_generate_lot_name(move.product_id, is_serial=False)

        new_lot = self.env['stock.lot'].create({
            'name': lot_name,
            'product_id': move.product_id.id,
            'company_id': self.env.company.id,
        })

        # Crear move.line con el lote
        self.env['stock.move.line'].create({
            'move_id': move.id,
            'product_id': move.product_id.id,
            'lot_id': new_lot.id,
            'quantity': qty_to_assign,
            'product_uom_id': move.product_id.uom_id.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
        })

        _logger.info(
            f"Creado lote {lot_name} con cantidad {qty_to_assign} "
            f"para producto terminado {move.product_id.name}"
        )

    def _sam_generate_lot_name(self, product, is_serial=False):
        """
        Genera un nombre de lote/serial automáticamente.

        Args:
            product: product.product - Producto
            is_serial: bool - True si es número de serie, False si es lote

        Returns:
            str: Nombre del lote/serial generado
        """
        # Usar secuencia de Odoo para generar número único
        if is_serial:
            seq = self.env['ir.sequence'].next_by_code('stock.lot.serial') or self.env['ir.sequence'].next_by_code('stock.lot.tracking')
        else:
            seq = self.env['ir.sequence'].next_by_code('stock.lot.tracking')

        # Si no existe la secuencia, usar formato manual
        if not seq:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            prefix = 'SN' if is_serial else 'LOT'
            code = product.default_code or 'PROD'
            return f"{prefix}-{code}-{timestamp}"

        # Si existe secuencia, usar formato: CODIGO-SECUENCIA
        code = product.default_code or product.name[:10].upper()
        return f"{code}-{seq}"


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
