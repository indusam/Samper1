# -*- coding: utf-8 -*-

# formulas.py
# Impresión de la fórmula de un producto..
# VBueno 2505202111:46

# Impresión de la fórmula de un producto con y sin consolidación.
# Si una fórmula tiene un ingrediente fórmula, suma las cantidades de los ingr.
# de ambas fórmulas e imprime el resultado.

import logging
from odoo.tools.float_utils import float_round
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Formulas(models.TransientModel):

    _name = 'wizard.formulas'
    _description = 'Fórmulas'

    producto = fields.Many2one('mrp.bom', string="Producto")
    cantidad = fields.Float(string="Cantidad")
    ing_limitante = fields.Many2one('mrp.bom.line',string="Ingrediente limitante")
    cant_limitante = fields.Float(string="Cantidad limitante")
    consolidado = fields.Boolean(string="Fórmula consolidada",  )

    # permite seleccionar el ingrediente limitante.
    @api.onchange('producto')
    def onchange_producto(self):
        nlista = self.producto.id
        self.pct_merma = self.producto.product_tmpl_id.x_pct_merma
        for rec in self:
            return {'domain': {'ing_limitante':
                                   [('bom_id', '=', nlista)]}}


    # imprime formula
    def imprime_formula(self):

        vals=[]
        ingredientes = self.env['mrp.bom.line'].search(
                        [('bom_id.id', '=', self.producto.id)])

        if not self.ing_limitante:
            for ingrediente in ingredientes:
                codprov = self.env['product.supplierinfo'].search(
                    [('product_id.id','=',ingrediente.product_id.id)]
                ).product_code

                vals.append({
                    'componente': ingrediente.product_id.name,
                    'cod_prov': codprov,
                    'cant_comp': self.cantidad * (ingrediente.x_porcentaje / 100),
                    'unidad': ingrediente.product_id.uom_id.name,
                    'pct_formula': ingrediente.x_porcentaje,
                    'pct_categoria': ingrediente.x_porcentaje_categoria
                })

        if self.ing_limitante:
            ncantidad_il = self.ing_limitante.product_qty
            for ingrediente in ingredientes:

                codprov = self.env['product.supplierinfo'].search(
                    [('product_id.id', '=', ingrediente.product_id.id)]
                ).product_code

                vals.append({
                    'componente': ingrediente.product_id.name,
                    'cod_prov': codprov,
                    'cant_comp': self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'unidad': ingrediente.product_id.uom_id.name,
                    'pct_formula': ingrediente.x_porcentaje,
                    'pct_categoria': ingrediente.x_porcentaje_categoria
                    })

        # si se consolida la fórmula busca los ingredientes de los subproductos
        # y los suma a vals[]
        if self.consolidado:
            for ingrediente in ingredientes:
                if ingrediente.product_tmpl_id.route_ids.id == 5:

                    subformula = self.env['mrp.bom.line'].search(
                        [('bom_id.id', '=', ingrediente.product_id.product_tmpl_id.id)])

                    raise UserError(subformula)



        data = {'ids': self.ids,
                'model':self._name,
                'vals':vals,
                'producto':self.producto.product_tmpl_id.name,
                'codigo': self.producto.product_tmpl_id.default_code,
                'cantidad':self.cantidad,
                'ing_limitante':self.ing_limitante,
                'nombre_il':self.ing_limitante.product_tmpl_id.name,
                'cant_limitante':self.cant_limitante
                }

        return self.env.ref('sam_reportes.formulas_reporte').report_action(self, data=data)