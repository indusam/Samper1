# -*- coding: utf-8 -*-
{
    'name': 'Samper - Procesos',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Módulo para procesos personalizados de Samper',
    'description': """
        Módulo que incluye validaciones personalizadas para procesos de compras.

        Características:
        - Validación automática de costos contra lista de precios del proveedor
        - Alertas cuando un producto no está en la lista de precios
        - Actualización automática de precios según información del proveedor
    """,
    'author': 'Samper',
    'website': 'https://www.samper.mx',
    'depends': ['purchase'],
    'data': [
        # Aquí se agregarán los archivos XML de vistas si son necesarios
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
