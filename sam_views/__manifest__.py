# -*- coding: utf-8 -*-
{
    'name': 'Samper - Vistas Personalizadas',
    'version': '18.0.1.0.0',
    'category': 'Customizations',
    'summary': 'Personalizaciones de vistas y formularios para Samper',
    'description': """
        Samper - Vistas Personalizadas
        ================================

        Este módulo centraliza todas las personalizaciones de vistas y formularios
        para Industrias Alimenticias SAM SA de CV (Samper).

        Características:
        ----------------
        * Personalizaciones de vistas tree/list
        * Personalizaciones de vistas form
        * Campos adicionales en vistas existentes
        * Mejoras de usabilidad en la interfaz

        Vistas personalizadas:
        ----------------------
        * res.partner: Vista de lista con campos personalizados
        * account.move: Plantilla de factura personalizada con formato Samper
    """,
    'author': 'Samper',
    'website': 'https://www.samper.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock',
        'account',
        'sale',
        'l10n_mx_edi',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/factura_samper.xml',
        'views/stock_picking_form_views.xml',
        'views/seleccion_lotes.xml',
        'views/report_deliveryslip_inherit.xml',
        'views/report_saleorder_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
