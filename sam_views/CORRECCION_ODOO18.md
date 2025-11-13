# Corrección de Template de Facturas para Odoo 18

## Problema

Al imprimir facturas en Odoo 18, se produce el siguiente error:

```
KeyError: 'formatted_amount'
Template: account.document_tax_totals_copy_1
```

Este error ocurre porque el template `account.document_tax_totals_copy_1` fue creado con Odoo Studio usando una estructura que ya no es compatible con Odoo 18.

## Causa

En Odoo 18, la estructura de datos de `tax_totals` cambió:

- **Antes (Odoo 17 y anteriores):** `subtotal['formatted_amount']`
- **Ahora (Odoo 18):** `subtotal['base_amount_currency']` + widget monetary

## Solución Implementada

Este módulo incluye dos mecanismos de corrección:

### 1. Hook Automático (`hooks.py`)

Al actualizar el módulo `sam_views`, el hook `post_init_hook` buscará automáticamente el template `account.document_tax_totals_copy_1` en la base de datos y corregirá las referencias obsoletas:

- Reemplaza `subtotal['formatted_amount']` por `subtotal.get('base_amount_currency', subtotal.get('amount', 0))`
- Actualiza `t-esc` a `t-out`
- Añade `t-options` con el widget monetary

### 2. Template de Reemplazo (`views/account_report_views.xml`)

Se proporciona un template completamente nuevo (`document_tax_totals_sam`) compatible con Odoo 18 que puede usarse como reemplazo manual si el hook automático no funciona.

## Pasos para Aplicar la Corrección

### Opción A: Actualización Automática (Recomendada)

1. **Subir los cambios a Odoo.sh:**
   ```bash
   cd /Users/vbueno/Desarrollos/odoo/samper/samper18/Samper1
   git add sam_views/
   git commit -m "sam_views - corrección de template de totales de impuestos para Odoo 18"
   git push origin master
   ```

2. **Actualizar el módulo en Odoo.sh:**
   - Ir a: Aplicaciones > Buscar "Samper - Vistas Personalizadas"
   - Hacer clic en "Actualizar"
   - El hook se ejecutará automáticamente y corregirá el template

3. **Verificar la corrección:**
   - Ir a una factura
   - Hacer clic en "Imprimir" > "Factura"
   - El PDF debería generarse sin errores

### Opción B: Corrección Manual (Si la Opción A falla)

Si el hook automático no funciona, puedes eliminar el template problemático y dejar que Odoo use el template estándar:

1. **Activar el modo desarrollador:**
   - Ir a: Ajustes > Activar el modo desarrollador

2. **Buscar el template problemático:**
   - Ir a: Ajustes > Técnico > Interfaz de usuario > Vistas
   - Buscar: `account.document_tax_totals_copy_1`
   - Hacer clic en la vista encontrada

3. **Eliminar o desactivar:**
   - Opción 1: Hacer clic en "Acción" > "Eliminar"
   - Opción 2: Desmarcar "Activo" (si existe esa opción)

4. **Verificar:**
   - Intentar imprimir una factura nuevamente

### Opción C: Usar el Template de Reemplazo

Si prefieres usar el template nuevo proporcionado:

1. Seguir los pasos de la Opción B para eliminar el template problemático
2. El template `document_tax_totals_sam` estará disponible en el sistema
3. Configurar el reporte de facturas para usar este template (esto requiere conocimientos técnicos)

## Verificación de la Corrección

Después de aplicar cualquiera de las opciones, verifica que:

1. ✅ Las facturas se imprimen sin errores
2. ✅ Los totales de impuestos se muestran correctamente
3. ✅ El formato de moneda es correcto (ej: "$1,234.56")

## Detalles Técnicos

### Cambios en la Estructura de Datos (Odoo 17 → 18)

**Odoo 17 y anteriores:**
```xml
<span t-esc="subtotal['formatted_amount']"/>
```

**Odoo 18:**
```xml
<span t-out="subtotal['base_amount_currency']"
      t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
```

### Archivos Modificados

- `__init__.py`: Importa el módulo hooks
- `__manifest__.py`: Añade dependencia de 'account' y post_init_hook
- `hooks.py`: Nuevo - Contiene la lógica de corrección automática
- `views/account_report_views.xml`: Nuevo - Template de reemplazo compatible con Odoo 18

## Soporte

Si después de aplicar esta corrección sigues teniendo problemas:

1. Revisa los logs de Odoo.sh para ver si el hook se ejecutó correctamente
2. Verifica que el template de Studio fue efectivamente modificado o eliminado
3. Contacta al equipo de desarrollo para asistencia adicional

## Referencias

- Repositorio de Odoo 18: https://github.com/odoo/odoo/blob/18.0/addons/account/views/report_invoice.xml
- Documentación de QWeb: https://www.odoo.com/documentation/18.0/developer/reference/frontend/qweb.html
