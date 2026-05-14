# -*- coding: utf-8 -*-
{
    'name': 'Fix Emails Partners',
    'version': '18.0.1.0.0',
    'summary': 'Acción de servidor para actualizar emails de res.partner',
    'author': 'RIMSSAS',
    'category': 'Technical',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/server_action.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
