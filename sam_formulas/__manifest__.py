# -*- coding: utf-8 -*-
{
    'name': "sam_formulas",

    'summary': """
        Módulo para la gestión de fórmulas, intermedios y empaques en Samper.
    """,

    'description': """
        Módulo personalizado para la gestión de:
        - Fórmulas de producción
        - Productos intermedios
        - Empaques
        - Relación entre productos y sus componentes
    """,

    'author': "vbueno",
    'license': 'AGPL-3',
    'website': "http://www.samper.mx",

    # Categoría del módulo
    'category': 'Manufacturing/Manufacturing',
    'version': '16.0.1.0.0',

    # Módulos necesarios para que este funcione correctamente
    'depends': [
        'base',
        'mrp',
        'product',
    ],

    # Archivos de datos que se cargarán al instalar/actualizar el módulo
    'data': [
        # Seguridad y permisos
        'security/ir.model.access.csv',
        
        # Vistas
        'views/mrp_bom_views.xml',
        
        # Datos
        # 'data/data.xml',
    ],
    
    # Aplicación (no es un módulo técnico)
    'application': False,
    'installable': True,
    'auto_install': False,
}
