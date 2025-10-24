# -*- coding: utf-8 -*-
{
    'name': "sam_formulas",

    'summary': """
        Personalización de Odoo para Industrias Alimenticias SAM SA de CV""",

    'description': """
        Gestión de fórmulas, listas de materiales, intermedios y empaques.
        Campos personalizados para productos, información nutricional y control de producción.
    """,

    'author': "vbueno",
    'license': 'AGPL-3',
    'website': "https://www.samper.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/18.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
