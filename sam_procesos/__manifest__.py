# -*- coding: utf-8 -*-
{
    'name': 'SAM Procesos',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Procesos y herramientas personalizadas para Samper',
    'description': """
        Módulo que incluye procesos personalizados para Samper:
        - Descarga de archivos XML y PDF de facturas
        - Borrado de archivos PDF antiguos
        - Validación de costos en órdenes de compra
    """,
    'author': 'VBueno',
    'website': 'https://www.samper.mx',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'wizard/borra_pdf_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
