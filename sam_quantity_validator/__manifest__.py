{
    'name': 'Quantity Validator',
    'version': '16.0',
    'summary': 'Valida y ajusta cantidades mínimas en todo el sistema',
    'description': """
        Módulo para establecer a cero cantidades menores a 0.0001 en:
        - Lotes (stock.lot)
        - Movimientos de inventario (stock.move)
        - Existencias (stock.quant)
        - Órdenes de producción (mrp.production)
        - Transferencias (stock.picking)
        - Componentes de manufactura
    """,
    'author': 'VBueno - Industrias Alimenticias SAM SA de CV',
    'website': 'https://www.samper1.mx',
    'depends': ['stock', 'mrp'],
    'category': 'Manufacturing',
    'data': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook'
}