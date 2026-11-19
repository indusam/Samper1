# -*- coding: utf-8 -*-
"""
Relación entre órdenes de fabricación y pedidos a producción.

Vincula mrp.production con el modelo de Studio 'x_calculo_de_minimos_y'
(Cálculo de mínimos / pedidos a producción) para poder indicar a qué
número de pedido corresponde cada orden de fabricación.

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
        domain="[('x_entregado', '=', False)]",
        index=True,
        ondelete='set null',
        help='Número de pedido a producción (Cálculo de mínimos) al que '
             'corresponde esta orden de fabricación. Sólo se listan los '
             'pedidos que aún no han sido entregados.',
    )
