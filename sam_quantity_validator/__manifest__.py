{
    'name': 'Quantity Validator',
    'version': '16.0.1.0.0',
    'summary': 'Validate and adjust quantities throughout the system',
    'description': """
        Module to set quantities below 0.0001 to zero in:
        - Lots (stock.lot)
        - Inventory moves (stock.move)
        - Stock quants (stock.quant)
        - Manufacturing orders (mrp.production)
        - Transfers (stock.picking)
        - Manufacturing components
    """,
    'author': 'VBueno - Industrias Alimenticias SAM SA de CV',
    'website': 'https://www.samper1.mx',
    'depends': ['stock', 'mrp'],
    'category': 'Manufacturing',
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_consumption_warning_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook'
}