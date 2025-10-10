# Módulo w_addenda_liverpool
# windsurf
## Descripción General

El módulo **w_addenda_liverpool** es una extensión para Odoo que permite generar addendas de Liverpool en las facturas electrónicas (CFDI) mexicanas. Está diseñado específicamente para empresas que trabajan con Liverpool como cliente y necesitan incluir información adicional requerida por este cliente en sus comprobantes fiscales digitales.

## Funcionalidad Principal

Este módulo agrega la funcionalidad necesaria para:

- **Generar addendas Liverpool**: Incluye automáticamente la estructura detallista requerida por Liverpool en las facturas CFDI versión 4.0
- **Campos específicos de Liverpool**: Permite capturar información específica requerida por Liverpool como número de orden de compra, folio de entrega, fecha de entrega
- **Integración con el sistema EDI mexicano**: Se integra perfectamente con el sistema de facturación electrónica de Odoo para México

## Características Técnicas

### Versión de Odoo Compatible
- **Odoo 16.0**

### Dependencias
- `base`
- `account`
- `account_accountant`
- `l10n_mx_edi` (Sistema EDI para México)

### Estructura del Módulo

```
w_addenda_liverpool/
├── models/
│   ├── __init__.py
│   ├── inherit_account_edi_format.py    # Manejo del formato EDI
│   ├── inherit_account_move.py          # Campos específicos de factura
│   ├── inherit_res_partner.py           # Campos del cliente
│   └── inherit_res_company.py           # Campos de la compañía
├── views/
│   ├── inherit_account_move_view.xml    # Vistas de factura
│   ├── inherit_res_company_view.xml     # Vistas de compañía
│   └── inherit_res_partner_view.xml     # Vistas de cliente
├── data/
│   └── addenda_liverpool_v40.xml        # Template de la addenda
└── __manifest__.py                      # Configuración del módulo
```

## Instalación y Configuración

### 1. Instalación del Módulo

1. Copie el módulo en el directorio de addons de Odoo
2. Reinicie el servidor de Odoo
3. Vaya a **Aplicaciones** en Odoo
4. Busque "Addenda Liverpool"
5. Haga clic en **Instalar**

### 2. Configuración Inicial

#### Configuración de la Compañía
1. Vaya a **Configuración > Empresas**
2. Seleccione su compañía
3. Complete el campo **Global location number (GLN)** requerido para la addenda

#### Configuración del Cliente (Liverpool)
1. Vaya a **Contactos**
2. Busque o cree el contacto de Liverpool
3. Configure los siguientes campos:
   - **Generar addenda Liverpool**: Marque esta casilla para activar la addenda
   - **Global location number (GLN)**: Número de ubicación global del comprador
   - **Contacto de compras**: Información del contacto de compras
   - **Identificación del proveedor**: Código de identificación asignado por Liverpool

## Uso del Módulo

### Campos Adicionales en Facturas

Cuando el cliente tiene activada la opción "Generar addenda Liverpool", aparecerán automáticamente campos adicionales en las facturas:

#### En la factura (Account Move):
- **Orden de compra Liverpool**: Número de orden de compra proporcionado por Liverpool
- **Folio de entrega**: Número de folio de entrega de mercancía
- **Fecha de entrega**: Fecha en que se asignó el número de hoja de recepción

#### En las líneas de factura:
El módulo calcula automáticamente:
- Precio bruto
- Precio neto
- Cantidad formateada
- Importes brutos y netos por línea

### Generación Automática de Addenda

Cuando se genera el CFDI de una factura para un cliente Liverpool:

1. Se verifica si el cliente requiere addenda Liverpool
2. Se incluye automáticamente la estructura detallista en el complemento del CFDI
3. Se agregan todos los datos específicos requeridos por Liverpool
4. Se calcula y formatea correctamente toda la información monetaria

## Estructura de la Addenda Liverpool

La addenda generada incluye:

### Información del Documento
- Tipo de entidad (INVOICE/CREDIT_NOTE)
- Instrucciones especiales con monto en texto
- Número de orden de compra

### Información de Entrega
- Folio de entrega
- Fecha de referencia de entrega

### Información de las Partes
- **Comprador**: GLN, información de contacto
- **Vendedor**: GLN de la compañía, identificación del proveedor

### Detalle de Artículos
Por cada línea de factura:
- GTIN (código de barras)
- Código de producto del proveedor
- Descripción del artículo
- Cantidad facturada
- Precios (bruto, neto)
- Importes totales por línea

### Totales
- Monto total de la factura
- Descuentos aplicados

## Mantenimiento y Actualizaciones

### Para Futuras Versiones de Odoo

#### 1. Verificación de Compatibilidad
- Revisar cambios en el sistema EDI (`l10n_mx_edi`)
- Verificar estabilidad de métodos `_l10n_mx_edi_cfdi_*`
- Probar generación de CFDI con nuevas versiones

#### 2. Campos y Métodos a Monitorear
- `inherit_account_edi_format._l10n_mx_edi_cfdi_append_addenda()`
- Campos calculados en `inherit_account_move.py`
- Métodos de formateo de moneda y cantidades

#### 3. Actualizaciones de Esquemas
- Monitorear cambios en esquemas CFDI del SAT
- Actualizar estructura detallista si Liverpool modifica sus requerimientos
- Verificar versiones de `documentStructureVersion` en la addenda

### Procedimiento de Actualización

1. **Respaldo**: Crear respaldo completo antes de actualizar
2. **Pruebas**: Probar en ambiente de desarrollo con datos reales
3. **Validación**: Verificar que la addenda se genere correctamente
4. **Monitoreo**: Supervisar logs para detectar errores

### Solución de Problemas Comunes

#### Error: "Addenda no se incluye en CFDI"
**Posibles causas:**
- Cliente no tiene marcada la opción "Generar addenda Liverpool"
- Campos requeridos vacíos (GLN, etc.)
- Error en el template de addenda

**Solución:**
1. Verificar configuración del cliente
2. Completar campos requeridos
3. Revisar logs de Odoo para errores específicos

#### Error: "Campos calculados incorrectos"
**Posibles causas:**
- Problemas de redondeo en cálculos
- Divisas mal configuradas
- Errores en fórmulas de cálculo

**Solución:**
1. Verificar configuración de moneda
2. Revisar fórmulas en `inherit_account_move.py`
3. Verificar precisión decimal

## Soporte Técnico

**Desarrollador Original:** Eddy Luis Pérez Vila (epv@birtum.com)
**Empresa:** Birtum © - http://www.birtum.com/

## Información de Licencia

Este módulo está bajo licencia **AGPL-3** (Affero General Public License v3).

## Historial de Versiones

- **v16.0**: Versión inicial para Odoo 16.0
  - Soporte completo para CFDI 4.0
  - Integración con sistema EDI mexicano
  - Campos específicos de Liverpool
  - Generación automática de addenda detallista
