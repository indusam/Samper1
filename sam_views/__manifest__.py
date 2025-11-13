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
        * account.move: Corrección de templates de reportes para Odoo 18

        Correcciones de compatibilidad:
        --------------------------------
        * Template de totales de impuestos compatible con Odoo 18
        * Corrección automática de templates creados con Studio que usan 'formatted_amount'
    """,
    'author': 'Samper',
    'website': 'https://www.samper.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock',
        'account',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/account_report_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
