# -*- coding: utf-8 -*-
{
    'name': "sam_inventario",

    'summary': """
        Personalización de Odoo para Industrias Alimenticias SAM SA de CV""",

    'description': """
        Gestión de inventario personalizada para Samper.
        Incluye campos adicionales para movimientos de stock, control de merma,
        y captura de peso y cantidad por caja.
    """,

    'author': "vbueno",
    'license': 'AGPL-3',
    'website': "https://www.samper.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/18.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Inventory',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizards/peso_cantidad_caja_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
