{
    'name': 'Validador de Cantidades',
    'version': '16.0.1.0.0',
    'summary': 'Valida y ajusta cantidades en todo el sistema',
    'description': """
        Módulo para establecer cantidades menores a 0.0001 a cero en:
        - Lotes (stock.lot)
        - Movimientos de inventario (stock.move)
        - Existencias (stock.quant)
        - Órdenes de fabricación (mrp.production)
        - Transferencias (stock.picking)
        - Componentes de manufactura
    """,
    'author': 'VBueno - Industrias Alimenticias SAM SA de CV',
    'website': 'https://www.samper1.mx',
    'depends': ['stock', 'mrp'],
    'category': 'Manufactura/Inventario',
    'data': [
        # 'security/ir.model.access.csv',  # Comentado temporalmente
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook'
}
