# -*- coding: utf-8 -*-
{
    'name': 'Validador de Cantidades',
    'version': '18.0.1.0.0',
    'summary': 'Valida y ajusta cantidades en todo el sistema',
    'description': """
        Módulo para validar y establecer cantidades menores a 0.0001 a cero.

        Características:
        - Validación automática en lotes (stock.lot)
        - Validación en movimientos de inventario (stock.move)
        - Validación en existencias (stock.quant)
        - Validación en órdenes de fabricación (mrp.production)
        - Validación en transferencias (stock.picking)
        - Corrección masiva de datos existentes al instalar
        - Logging detallado de ajustes realizados
    """,
    'author': 'VBueno - Industrias Alimenticias SAM SA de CV',
    'website': 'https://www.samper.mx',
    'depends': ['stock', 'mrp'],
    'category': 'Manufacturing/Manufacturing',
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'post_init_hook': 'post_init_hook'
}
