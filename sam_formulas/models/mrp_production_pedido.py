# -*- coding: utf-8 -*-
"""
Relación entre órdenes de fabricación y pedidos a producción.

Vincula mrp.production con el modelo de Studio 'x_calculo_de_minimos_y'
(Cálculo de mínimos y máximos) para poder indicar a qué número de pedido
corresponde cada orden de fabricación.

Nota: no se aplica ningún domain al campo. El indicador de entregado
('x_entregado') vive en el modelo de detalle 'x_calculo_de_minimos_y_line_519a',
no en la cabecera, por lo que filtrar por él exigiría recorrer el one2many.
Los pedidos archivados sí quedan excluidos automáticamente, porque Odoo
reconoce 'x_active' como campo de archivado y aplica active_test en toda
búsqueda (odoo/models.py: _active_name).

Autor: VBueno
Fecha: 2026-11-19
Versión: Odoo 18.0
"""

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    x_pedido_produccion_id = fields.Many2one(
        comodel_name='x_calculo_de_minimos_y',
        string='Pedido a producción',
        index=True,
        ondelete='set null',
        help='Número de pedido a producción (Cálculo de mínimos y máximos) '
             'al que corresponde esta orden de fabricación.',
    )
