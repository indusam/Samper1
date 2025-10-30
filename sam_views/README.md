# Samper - Vistas Personalizadas

Módulo para centralizar las personalizaciones de vistas y formularios para Industrias Alimenticias SAM SA de CV (Samper).

## Versión

- **Odoo**: 18.0
- **Módulo**: 18.0.1.0.0

## Descripción

Este módulo contiene todas las personalizaciones de vistas y formularios utilizadas por Samper, permitiendo una mejor organización y mantenimiento de las customizaciones de interfaz.

## Características

### Vistas Personalizadas

#### Stock Move (stock.move)
- **Vista**: Lista/Tree
- **Personalización**: Agregado campo `x_studio_nombre_comercial` (Nombre Comercial)
- **Ubicación**: Antes del campo "Documento origen" (origin)
- **Atributo**: `optional="show"` - El campo es visible por defecto pero el usuario puede ocultarlo

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar la lista de aplicaciones
3. Buscar "Samper - Vistas Personalizadas"
4. Instalar el módulo

## Dependencias

- `stock`: Módulo de inventario de Odoo

## Estructura del Módulo

```
sam_views/
├── __init__.py
├── __manifest__.py
├── README.md
└── views/
    └── stock_move_views.xml
```

## Uso

Una vez instalado el módulo, las vistas personalizadas se aplicarán automáticamente.

Para la vista de movimientos de inventario:
1. Ir a **Inventario > Reportes > Movimientos de Producto**
2. El campo "Nombre Comercial" aparecerá en la lista antes del campo "Documento origen"

## Notas Técnicas

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
