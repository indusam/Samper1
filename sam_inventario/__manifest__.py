# -*- coding: utf-8 -*-
{
    'name': "sam_inventario",

    'summary': """
        Personalización de Odoo para Industrias Alimenticias SAM SA de CV""",

    'description': """
        Campos, vistas, reportes, etc. propios de Samper.
        Adecuaciones al módulo de inventario para Samper.
    """,

    'author': "vbueno",
    'license': 'AGPL-3',
    'website': "http://www.samper.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '15.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizards/peso_cantidad_caja_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
