# -*- coding: utf-8 -*-
{
    'name': 'Stock - Ignorar Rutas Automáticas',
    'summary': 'Permite que ciertos tipos de operación ignoren las rutas automáticas configuradas en productos',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'author': 'Samper',
    'website': 'https://www.samper.mx',
    'license': 'LGPL-3',
    'depends': ['stock', 'base_automation'],
    'data': [
        'views/stock_picking_type_views.xml',
        'data/automated_actions.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
