# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_presentacion = fields.Many2one("uom.uom", string="Presentacion")
    x_pct_variacion = fields.Float(string='% Variación', digits=(3,4))

class ListaMateriales(models.Model):
    _inherit = 'mrp.bom.line'

    x_porcentaje = fields.Float(string="%", digits=(3, 4))
    x_porcentaje_il = fields.Float(string="% IL", digits=(3, 4))
    x_cantidad_il = fields.Float(string="Cantidad Limitante", digits=(12, 4))
    x_ingrediente_limitante = fields.Boolean(string="IL")


class ListaMaterialesHeader(models.Model):
    _inherit = 'mrp.bom'

    product_qty = fields.Float(string="Cantidad", digits=(12, 4))
    x_cantidad_il = fields.Float(string="Cantidad Limitante", digits=(12, 4))
    x_ingrediente_limitante = fields.Many2one("mrp.bom.line",
                                             string="Ingrediente limitante")
    x_piezas = fields.Integer(string='Piezas:')

    @api.onchange('x_cantidad_il')
    def onchange_x_cantidad_il(self):
        for rec in self:
            return {'domain': {'x_ingrediente_limitante':
                                   [('bom_id', '=', rec.product_tmpl_id.id)]}}

    @api.onchange('x_piezas')
    def onchange_x_piezas(self):
        if self.x_piezas > 0:
            for rec in self:

                ncantoriginal = rec.product_qty
                npresentacion = rec.env['product.product'].search(
                    [('id', '=', rec.product_id.id)],
                    limit=1).x_presentacion.id

                raise Warning(npresentacion)
"""
                 
                npresentacion = rec.env['product.product'].search(
                    [('id', '=', rec.product_id.id)], limit=1).x_presentacion.id
                nfactor = rec.env['uom.uom'].search(
                    [('id', '=', npresentacion)], limit=1).factor_inv
                ncantidad = ncantoriginal * nfactor

                rec.product_qty = ncantidad
"""

class ReporteInventario(models.Model):
    _inherit = 'stock.quant'
    inventory_quantity = fields.Float(string="Cantidad Disponible",
                                      digits=(12, 4))

# class sam_formulas(models.Model):
#     _name = 'sam_formulas.sam_formulas'
#     _description = 'sam_formulas.sam_formulas'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
