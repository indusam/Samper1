# Samper - Vistas Personalizadas

Módulo para centralizar las personalizaciones de vistas y formularios para Industrias Alimenticias SAM SA de CV (Samper).

## Versión

- **Odoo**: 18.0
- **Módulo**: 18.0.1.0.0

## Descripción

Este módulo contiene todas las personalizaciones de vistas y formularios utilizadas por Samper, permitiendo una mejor organización y mantenimiento de las customizaciones de interfaz.

## Características

### Reportes Personalizados

#### Factura SAM (account.move)
- **Reporte**: Factura SAM
- **Descripción**: Plantilla de factura personalizada con el formato corporativo de Samper
- **Características**:
  - Logo de Samper en el encabezado
  - Diseño de dos columnas (empresa/cliente)
  - Título en color bordó (#8B2332)
  - Tabla de productos con columnas adicionales:
    - Código de producto
    - Lotes/NS/NL (dentro de la misma tabla, mostrando cantidad, número y fecha de caducidad)
    - Pzas (piezas)
    - Código de unidad SAT
  - Información fiscal CFDI (para México):
    - Folio Fiscal (UUID)
    - Uso CFDI
    - Forma de Pago
    - Método de Pago
  - Segunda página con información fiscal (para facturas timbradas):
    - Sello digital del emisor
    - Sello digital del SAT
    - Cadena original del complemento
    - Certificados (emisor y SAT)
    - Fecha de certificación
    - Código QR (si está disponible)
    - Leyenda "Este documento es una representación impresa de un CFDI"
- **Ubicación**: Disponible en el botón "Imprimir" de las facturas

### Vistas Personalizadas

#### Partner (res.partner)
- **Vista**: Lista/Tree
- **Personalización**: Campos personalizados para vista de clientes/proveedores
- **Ubicación**: Vista de lista de contactos

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar la lista de aplicaciones
3. Buscar "Samper - Vistas Personalizadas"
4. Instalar el módulo

## Dependencias

- `base`: Módulo base de Odoo
- `stock`: Módulo de inventario de Odoo
- `account`: Módulo de contabilidad de Odoo
- `l10n_mx_edi`: Módulo de facturación electrónica mexicana (CFDI)

## Estructura del Módulo

```
sam_views/
├── __init__.py
├── __manifest__.py
├── README.md
└── views/
    ├── res_partner_views.xml
    └── factura_sam.xml
```

## Uso

### Imprimir Facturas con Formato SAM

1. Ir a **Contabilidad > Clientes > Facturas**
2. Abrir una factura
3. Hacer clic en el botón **Imprimir**
4. Seleccionar **Factura SAM**
5. El PDF se generará con el formato personalizado de Samper

El reporte incluirá automáticamente:
- Logo de la empresa (configurado en Configuración > Empresas)
- Información del cliente y dirección de entrega (si aplica)
- Tabla de productos con códigos, lotes y unidades SAT
- Información fiscal CFDI (si la factura está timbrada)
- Segunda página con sellos digitales y código QR (para facturas timbradas)

### Vistas Personalizadas de Contactos

Las vistas personalizadas de contactos se aplicarán automáticamente al instalar el módulo en:
1. **Contactos > Clientes/Proveedores**
2. Las columnas adicionales estarán disponibles y personalizables

## Notas Técnicas

### Plantilla de Factura SAM

La plantilla de factura utiliza herencia de QWeb con `primary="True"`, creando una versión completamente personalizada basada en `account.report_invoice_document`.

**Estructura del reporte:**
```xml
<record id="report_invoice_sam" model="ir.actions.report">
    <!-- Define el reporte en el menú de impresión -->
</record>

<template id="report_invoice_sam_main">
    <!-- Template principal que itera sobre los documentos -->
</template>

<template id="report_invoice_document_sam" inherit_id="account.report_invoice_document" primary="True">
    <!-- Template personalizado del documento -->
</template>
```

**Campos CFDI utilizados:**
- `l10n_mx_edi_cfdi_uuid`: Folio Fiscal (UUID)
- `l10n_mx_edi_usage`: Uso CFDI
- `l10n_mx_edi_payment_method_id`: Forma de Pago
- `l10n_mx_edi_payment_policy`: Método de Pago
- `product_uom_id.unspsc_code_id.code`: Código de unidad UNSPSC/SAT

**Campos computados personalizados (extraídos del XML del CFDI):**
- `x_cfdi_sello_emisor`: Sello digital del emisor
- `x_cfdi_sello_sat`: Sello digital del SAT
- `x_cfdi_certificado_emisor`: Número de certificado del emisor
- `x_cfdi_certificado_sat`: Número de certificado del SAT
- `x_cfdi_fecha_certificacion`: Fecha de certificación del CFDI

Estos campos se calculan automáticamente al parsear el XML del CFDI adjunto a la factura.

**Requisitos:**
- El módulo de localización mexicana debe estar instalado (`l10n_mx_edi`)
- La empresa debe tener un logo configurado para que aparezca en la factura
- Los productos deben tener códigos UNSPSC configurados para mostrar el código de unidad SAT
- Para la segunda página fiscal, la factura debe estar timbrada (tener UUID)

### Herencia de Vistas

El módulo utiliza herencia de vistas de Odoo para extender las vistas existentes sin modificar el código base.

```xml
<field name="inherit_id" ref="stock.view_move_tree"/>
```

### Atributo optional

El atributo `optional="show"` permite que el usuario pueda:
- Mostrar/ocultar el campo desde las opciones de columna
- Mantener su preferencia entre sesiones

Valores disponibles:
- `optional="show"`: Visible por defecto, ocultable
- `optional="hide"`: Oculto por defecto, mostrable
- Sin atributo: Siempre visible, no ocultable

## Mantenimiento

### Agregar una nueva vista personalizada

1. Crear el archivo XML en `views/`
2. Agregar el archivo al `__manifest__.py` en la sección `data`
3. Actualizar este README con la documentación de la vista

### Convenciones de Nombres

- IDs de vistas: `view_[modelo]_[tipo]_inherit_sam`
- Archivos XML: `[modelo]_views.xml`

## Autor

**Samper**
Industrias Alimenticias SAM SA de CV

## Licencia

LGPL-3
