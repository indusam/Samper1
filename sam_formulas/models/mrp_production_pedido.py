# -*- coding: utf-8 -*-
"""
Relación entre órdenes de fabricación y líneas de pedido a producción.

Vincula mrp.production con el modelo de detalle de Studio
'x_calculo_de_minimos_y_line_b519a' (líneas del Cálculo de mínimos y máximos),
para indicar a qué línea de pedido corresponde cada orden de fabricación.

Se apunta al detalle y no a la cabecera ('x_calculo_de_minimos_y') porque el
indicador de entregado ('x_entregado') y el producto ('x_product_id') viven en
la línea, lo que permite filtrar por ambos sin recorrer el one2many.

El domain NO se define aquí sino en la vista (mrp_production_pedido_views.xml),
porque depende de 'product_id' del registro en edición: un domain de campo que
cita 'product_id' obliga a que ese campo esté presente en TODA vista editable
donde aparezca este campo, o la validación de vistas falla al actualizar
(odoo/addons/base/models/ir_ui_view.py, _validate_domain_identifiers).

Autor: VBueno
Fecha: 2026-11-19
Versión: Odoo 18.0
"""

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    x_ped_produccion_id = fields.Many2one(
        comodel_name='x_calculo_de_minimos_y_line_b519a',
        string='Pedido a producción',
        index=True,
        ondelete='set null',
        help='Línea del pedido a producción (Cálculo de mínimos y máximos) '
             'que cubre esta orden de fabricación. Sólo se ofrecen las líneas '
             'confirmadas, no entregadas y del mismo producto que la orden.',
    )
