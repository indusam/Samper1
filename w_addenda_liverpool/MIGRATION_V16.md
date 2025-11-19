# Migración del módulo w_addenda_liverpool a Odoo v16

## Resumen de cambios realizados

Este documento detalla todos los cambios realizados para migrar el módulo `w_addenda_liverpool` desde Odoo v15 a Odoo v16.

## Cambios realizados

### 1. Actualización del archivo `__manifest__.py`

#### Dependencias
- **Eliminado**: `account_accountant` (no es un módulo estándar en Odoo v16)
- **Mantenido**: `base`, `account`, `l10n_mx_edi`

#### Claves del manifiesto
- **Eliminado**: `'qweb': []` (deprecado en v16)
- **Agregado**: `'assets': {}` (nueva estructura para assets en v16)

### 2. Actualización de vistas XML

#### `views/inherit_account_move_view.xml`
- **Cambio**: Reemplazado el atributo `attrs` por `invisible` con sintaxis de dominio Python
- **Antes**: `attrs="{'invisible': ['|', ('require_addenda_liverpool', '=', False), ('move_type', '=', 'entry')]}"`
- **Después**: `invisible="require_addenda_liverpool == False or move_type == 'entry'"`

#### `views/inherit_res_partner_view.xml`
- **Cambio**: Reemplazado el atributo `attrs` por `invisible` en todos los campos
- **Antes**: `attrs="{'invisible': [('generate_addenda_liverpool', '=', False)]}"`
- **Después**: `invisible="generate_addenda_liverpool == False"`

### 3. Actualización del template de addenda

#### `data/addenda_liverpool_v40.xml`
- **Cambio**: Actualizado el método para obtener el monto en texto
- **Antes**: `record._l10n_mx_edi_cfdi_amount_to_text()`
- **Después**: `record.l10n_mx_edi_amount_to_text`
- **Razón**: En Odoo v16, este es un campo computado en lugar de un método

### 4. Limpieza de código en modelos Python

#### `models/inherit_account_move.py`
- **Eliminado**: Imports no utilizados (`os`, `tempfile`, `uuid`, `lxml.etree`, `datetime`)
- **Eliminado**: Código comentado del método `read()`
- **Mantenido**: Imports necesarios (`models`, `fields`, `api`, `logging`, `unidecode`)

#### `models/inherit_account_move.py` - AccountMoveLine
- **Actualizado**: Método `get_price_gross()` para compatibilidad con v16
- **Agregado**: Verificación de existencia del método `flatten_taxes_hierarchy()`
- **Razón**: Compatibilidad con posibles cambios en la API de impuestos

#### `models/inherit_account_edi_format.py`
- **Eliminado**: Archivo completo (solo contenía código comentado y no estaba importado)

### 5. Estructura de archivos mantenida

Los siguientes archivos no requirieron cambios:
- `models/inherit_res_partner.py`
- `models/inherit_res_company.py`
- `views/inherit_res_company_view.xml`

## Cambios principales de Odoo v15 a v16 aplicados

1. **Sintaxis de atributos en vistas XML**: El atributo `attrs` fue deprecado en favor de atributos individuales (`invisible`, `readonly`, `required`) con sintaxis de dominio Python.

2. **Estructura de assets**: La clave `qweb` fue reemplazada por `assets` en el manifiesto.

3. **API de localización mexicana**: Algunos métodos fueron convertidos a campos computados.

4. **Limpieza de dependencias**: Eliminación de módulos no estándar que pueden no estar disponibles.

## Pruebas recomendadas

Después de la migración, se recomienda probar:

1. **Instalación del módulo**: Verificar que el módulo se instala sin errores
2. **Configuración de cliente**: Activar la addenda Liverpool en un cliente
3. **Generación de factura**: Crear y timbrar una factura con addenda Liverpool
4. **Validación XML**: Verificar que el XML generado contiene correctamente la addenda
5. **Campos visibles**: Confirmar que los campos se muestran/ocultan correctamente según la configuración

## Notas adicionales

- El módulo mantiene compatibilidad con CFDI 4.0
- La estructura de la addenda Liverpool (detallista) no fue modificada
- Todos los campos personalizados se mantuvieron sin cambios
- La lógica de negocio permanece intacta

## Compatibilidad

- **Versión de Odoo**: 16.0
- **Localización**: México (l10n_mx_edi)
- **CFDI**: Versión 4.0
