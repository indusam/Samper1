# -*- coding: utf-8 -*-
{
    'name': "sam_ventas",

    'summary': """
        Adecuaciones al módulo de ventas de Samper""",

    'description': """
        Modificaciones al módulo de ventas para Samper: vendedores, comisiones, piezas en el inventario, etc.
    """,

    'author': "VBueno",
    'website': "http://www.samper.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
