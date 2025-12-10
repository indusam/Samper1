# Asignación Automática de Lotes en Órdenes de Fabricación

## Descripción

Este módulo extiende la funcionalidad de manufactura de Odoo 18 para asignar automáticamente lotes/números de serie ya existentes al producto terminado cuando se marca como hecha una orden de fabricación.

En Odoo 18, el flujo estándar muestra un asistente donde el usuario debe seleccionar o generar manualmente los números de serie para cada producto con tracking. Este módulo automatiza ese proceso, buscando lotes disponibles en stock y asignándolos automáticamente siguiendo una estrategia FIFO.

## Problema que resuelve

### Odoo v16
- La asignación de lotes era más automática
- Los lotes se asignaban sin intervención manual en muchos casos

### Odoo v18
- Se muestra un asistente de "Generar números de serie" / "Importar números de serie"
- El usuario debe seleccionar manualmente los lotes para cada producto
- Proceso más lento y propenso a errores

### Solución
- Asigna automáticamente lotes existentes sin mostrar el asistente
- Usa estrategia FIFO sobre stock.quant disponibles
- Valida que haya suficiente stock antes de completar

## Características

### 1. Asignación Automática de Lotes
- **Tracking por lote**: Permite múltiples unidades por lote
- **Tracking por serial**: Un número de serie único por unidad
- **Estrategia FIFO**: Los lotes más antiguos se usan primero

### 2. Validaciones
- Verifica que haya suficientes lotes disponibles
- Muestra errores claros si falta stock
- Previene duplicación de números de serie

### 3. Configuración por Orden
- Campo `sam_auto_assign_lots` en mrp.production
- Se puede activar/desactivar por orden de fabricación
- Por defecto está activado

## Instalación

```bash
# Actualizar el módulo
odoo-bin -d tu_base_datos -u sam_formulas

# O desde la interfaz: Aplicaciones > sam_formulas > Actualizar
```

## Uso

### 1. Activar Auto-asignación

En el formulario de Orden de Fabricación (mrp.production):
- Buscar el campo "Auto-asignar Lotes" (después del campo Producto)
- Activar el toggle (está activado por defecto)

### 2. Requisitos Previos

Para que funcione correctamente:

#### Opción A: Lotes Pre-existentes (Caso de Prueba)
```python
# Crear lotes antes de producir
lot = env['stock.lot'].create({
    'name': 'LOT-001',
    'product_id': product.id,
    'company_id': env.company.id,
})

# Crear stock con el lote
env['stock.quant'].create({
    'product_id': product.id,
    'location_id': location.id,
    'quantity': 100.0,
    'lot_id': lot.id,
})
```

#### Opción B: Crear Lotes Automáticamente (Producción Real)
**NOTA**: La versión actual busca lotes existentes. Para un entorno de producción real donde no hay stock previo del producto terminado, se recomienda:

1. Modificar `_sam_get_available_lots_for_product()` para crear lotes automáticamente si no existen
2. O usar una ubicación intermedia donde sí existan lotes pre-creados
3. O generar lotes basados en un patrón/secuencia

### 3. Flujo de Trabajo

```
1. Crear Orden de Fabricación
   └─> Campo "Auto-asignar Lotes" = ✓ Activado

2. Confirmar Orden (button_confirm)
   └─> Se crean los movimientos de stock

3. Producir / Marcar como Hecha (button_mark_done)
   ├─> _sam_auto_assign_lots_to_finished_moves()
   │   ├─> Busca movimientos de producto terminado
   │   ├─> Para cada movimiento:
   │   │   ├─> Busca lotes disponibles (FIFO)
   │   │   ├─> Crea stock.move.line con lot_id
   │   │   └─> Valida cantidad suficiente
   │   └─> Si falta stock → UserError
   └─> Super().button_mark_done() → Completa la orden
```

## Estructura de Archivos

```
sam_formulas/
├── models/
│   ├── __init__.py                      # Imports actualizados
│   ├── mrp_production_auto_lot.py       # Lógica principal ⭐
│   └── ...otros modelos existentes
├── views/
│   ├── mrp_production_auto_lot_views.xml # Vista con campo toggle ⭐
│   └── ...otras vistas existentes
├── tests/
│   ├── __init__.py                      # ⭐ Nuevo
│   └── test_mrp_auto_lot_assignment.py  # Pruebas unitarias ⭐
├── __manifest__.py                      # Actualizado con nuevas vistas
└── README_AUTO_LOT.md                   # Este archivo ⭐
```

## Métodos Principales

### mrp.production

#### `button_mark_done()`
Método principal que se ejecuta al marcar la orden como hecha.
- Llama a `_sam_auto_assign_lots_to_finished_moves()` si está activado
- Luego ejecuta `super()` para mantener lógica estándar

#### `_sam_auto_assign_lots_to_finished_moves()`
Coordina la asignación automática de lotes.
- Identifica movimientos de producto terminado con tracking
- Llama a `_sam_assign_lots_to_move()` para cada uno

#### `_sam_assign_lots_to_move(move)`
Asigna lotes a un movimiento específico.
- Calcula cantidad pendiente de asignar
- Busca lotes disponibles con `_sam_get_available_lots_for_product()`
- Delega a `_sam_assign_serial_numbers()` o `_sam_assign_lot_numbers()`

#### `_sam_get_available_lots_for_product(product, location, qty_needed)`
Busca lotes disponibles en stock.quant.
- Filtra por producto y ubicación
- Calcula cantidad disponible (quantity - reserved_quantity)
- Ordena por FIFO (create_date ascendente)

#### `_sam_assign_serial_numbers(move, available_lots, qty, precision)`
Asigna números de serie únicos.
- Un lote diferente por cada unidad
- Crea move.line con `move._update_reserved_quantity()`

#### `_sam_assign_lot_numbers(move, available_lots, qty, precision)`
Asigna lotes permitiendo múltiples unidades.
- Puede usar el mismo lote para varias unidades
- Crea move.line con `move._update_reserved_quantity()`

## Ejemplo de Uso en Código

```python
# Crear producto con tracking
product = env['product.product'].create({
    'name': 'Producto con Lotes',
    'type': 'product',
    'tracking': 'lot',
})

# Crear lotes
lot1 = env['stock.lot'].create({
    'name': 'LOT-001',
    'product_id': product.id,
})

# Agregar stock con lote
env['stock.quant'].create({
    'product_id': product.id,
    'location_id': env.ref('stock.stock_location_stock').id,
    'quantity': 100.0,
    'lot_id': lot1.id,
})

# Crear BOM
bom = env['mrp.bom'].create({
    'product_id': product.id,
    'product_tmpl_id': product.product_tmpl_id.id,
    'product_qty': 1.0,
})

# Crear orden de fabricación
mo = env['mrp.production'].create({
    'product_id': product.id,
    'product_qty': 10.0,
    'bom_id': bom.id,
    'sam_auto_assign_lots': True,  # Activar auto-asignación
})

# Confirmar
mo.action_confirm()

# Marcar como hecha → Auto-asigna lotes
mo.button_mark_done()

# Verificar lotes asignados
move_lines = mo.move_finished_ids.mapped('move_line_ids')
for line in move_lines:
    print(f"Lote: {line.lot_id.name}, Cantidad: {line.quantity}")
```

## Manejo de Errores

### Error: No hay lotes disponibles
```
No se encontraron lotes disponibles para el producto 'XXXX' en la ubicación 'YYYY'.

Para que el sistema pueda asignar automáticamente, debe haber stock con lotes
disponibles en la ubicación de destino.

Cantidad requerida: 100.0 Units
```

**Solución**: Crear lotes en la ubicación de destino o modificar el código para crear lotes automáticamente.

### Error: No hay suficientes números de serie
```
No hay suficientes números de serie disponibles para el producto 'XXXX'.

Requeridos: 50
Disponibles: 10

Por favor, cree o importe los números de serie necesarios antes de finalizar la orden.
```

**Solución**: Crear más números de serie en stock.lot.

### Error: Cantidad insuficiente
```
No hay suficiente cantidad disponible en lotes para el producto 'XXXX'.

Requerido: 100.0 Units
Asignado: 75.0 Units
Faltante: 25.0 Units

Por favor, verifique que haya suficiente stock con lotes en la ubicación de destino.
```

**Solución**: Aumentar cantidad en quants existentes o crear más lotes.

## Pruebas

Ejecutar pruebas unitarias:

```bash
odoo-bin -d test_database --test-enable --stop-after-init \
    --test-tags /sam_formulas
```

### Casos de Prueba Incluidos

1. **test_auto_assign_lots_enabled**: Verifica asignación con opción activada
2. **test_auto_assign_lots_disabled**: Verifica flujo estándar con opción desactivada
3. **test_serial_tracking**: Prueba asignación de números de serie únicos
4. **test_insufficient_lots**: Verifica manejo de error por falta de stock

## Consideraciones para Producción

### Limitación Actual
El módulo busca lotes **existentes** en stock.quant. En un entorno de producción real, normalmente NO hay stock previo del producto terminado en la ubicación de destino antes de fabricar.

### Opciones de Adaptación

#### 1. Crear Lotes Automáticamente
Modificar `_sam_get_available_lots_for_product()`:

```python
def _sam_get_available_lots_for_product(self, product, location, qty_needed):
    # Primero buscar lotes existentes
    available_lots = super()._sam_get_available_lots_for_product(product, location, qty_needed)

    # Si no hay suficientes, crear nuevos
    if not available_lots or sum(l['qty_available'] for l in available_lots) < qty_needed:
        # Crear lote nuevo con patrón
        new_lot = self.env['stock.lot'].create({
            'name': self._generate_lot_name(product),
            'product_id': product.id,
            'company_id': self.env.company.id,
        })
        available_lots.append({'lot': new_lot, 'qty_available': qty_needed})

    return available_lots
```

#### 2. Usar Secuencia para Lotes
```python
def _generate_lot_name(self, product):
    """Genera nombre de lote basado en secuencia."""
    seq = self.env['ir.sequence'].next_by_code('stock.lot.serial') or 'LOT'
    return f"{product.default_code or 'PROD'}-{seq}"
```

#### 3. Pre-crear Lotes en Proceso
Crear un paso previo que genere los lotes antes de marcar como hecha:

```python
def action_prepare_lots(self):
    """Preparar lotes antes de finalizar producción."""
    for move in self.move_finished_ids:
        if move.product_id.tracking != 'none':
            # Crear lotes necesarios
            ...
```

## Compatibilidad

- **Odoo Version**: 18.0 (Community/Enterprise)
- **Módulos Requeridos**: base, mrp, stock
- **Python**: 3.10+

## Autor

- **Nombre**: VBueno
- **Fecha**: 2025-12-10
- **Licencia**: AGPL-3
- **Empresa**: Industrias Alimenticias SAM SA de CV

## Notas Técnicas

### ¿Por qué no usar override de _action_generate_serial_numbers()?
En Odoo 18, el asistente de números de serie se maneja de manera diferente que en v16. El método `button_mark_done` es el punto de entrada correcto para interceptar antes de que se abra el asistente.

### ¿Por qué llamar al super() después?
Para mantener toda la lógica estándar de Odoo (validaciones, actualizaciones de estado, triggers, etc.). Solo agregamos la asignación de lotes antes, pero dejamos que Odoo complete el resto del proceso.

### ¿Cómo se evita el asistente de lotes?
Al crear las stock.move.line con lot_id antes de llamar al super(), Odoo detecta que los movimientos ya tienen asignaciones completas y no muestra el asistente.

## Roadmap / Mejoras Futuras

- [ ] Configuración global de estrategia (FIFO, LIFO, FEFO)
- [ ] Creación automática de lotes si no existen
- [ ] Soporte para lotes en componentes (no solo producto terminado)
- [ ] Interfaz gráfica para ver lotes asignados antes de confirmar
- [ ] Logs de auditoría de asignaciones automáticas
- [ ] Configuración por tipo de operación o warehouse
