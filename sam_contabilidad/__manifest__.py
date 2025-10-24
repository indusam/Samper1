# -*- coding: utf-8 -*-
{
    'name': "sam_contabilidad",

    'summary': """
        Adecuaciones al módulo de contabilidad de Samper""",

    'description': """
        Modificaciones al módulo de contabilidad para Samper.
    """,

    'author': "VBueno",
    'license': 'AGPL-3',
    'website': "https://www.samper.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/18.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/borra_pdf_view.xml',
        'views/account_move_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
