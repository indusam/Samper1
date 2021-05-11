# -*- coding: utf-8 -*-

# tabla_nutrimental.py
# Impresión de la tabla nutrimental de un producto.
# VBueno 1603202112:12

# En product.product (y/o product.template) están los porcentajes de proteínas,
# grasa, grasa saturada, humedad, carbohidratos, azúcares y sodio para hacer el
# cálculo en base a cantidad del producto y/o cantidad de ingrediente limitante
# que se capture en el wizard.

import logging
from odoo.tools.float_utils import float_round
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class TablaNutrimental(models.TransientModel):

    _name = 'wizard.tabla.nutrimental'
    _description = 'Tabla Nutrimental'

    producto = fields.Many2one('mrp.bom', string="Producto")
    cantidad = fields.Float(string="Cantidad")
    ing_limitante = fields.Many2one('mrp.bom.line',string="Ingrediente limitante")
    cant_limitante = fields.Float(string="Cantidad limitante")


    # permite seleccionar el ingrediente limitante.
    @api.onchange('producto')
    def onchange_producto(self):
        nlista = self.producto.id
        for rec in self:
            return {'domain': {'ing_limitante':
                                   [('bom_id', '=', nlista)]}}

    # imprime la tabla nutrimental.
    def imprime_tabla_nutrimental(self):

        vals=[]
        ingredientes = self.env['mrp.bom.line'].search(
                        [('bom_id.id', '=', self.producto.id)])

        if not self.ing_limitante:
            for ingrediente in ingredientes:
                vals.append({
                    'componente': ingrediente.product_id.name,
                    'cant_comp': self.cantidad * (ingrediente.x_porcentaje / 100),
                    'pct_proteina': ingrediente.product_id.x_pct_proteinas,
                    'pct_grasas_tot': ingrediente.product_id.x_pct_grasas_totales,
                    'pct_grasas_sat': ingrediente.product_id.x_pct_grasas_saturadas,
                    'pct_grasas_trans': ingrediente.product_id.x_mgkg_grasas_trans,
                    'pct_humedad': ingrediente.product_id.x_pct_humedad,
                    'pct_carbs': ingrediente.product_id.x_pct_hidratos_de_carbono,
                    'pct_azucares': ingrediente.product_id.x_pct_azucares,
                    'mg_sodio': ingrediente.product_id.x_mg_sodio,
                    'proteina_kg': (ingrediente.product_id.x_pct_proteinas / 100) * (self.cantidad * (ingrediente.x_porcentaje / 100)),
                    'grasa_kg': (ingrediente.product_id.x_pct_grasas_totales / 100) * (self.cantidad * (ingrediente.x_porcentaje / 100)),
                    'grasa_sat_kg': (ingrediente.product_id.x_pct_grasas_saturadas / 100) * (self.cantidad * (ingrediente.x_porcentaje / 100)),
                    'grasa_trans_kg':ingrediente.product_id.x_mgkg_grasas_trans * 10 * (self.cantidad * (ingrediente.x_porcentaje / 100)),
                    'humedad_kg': (ingrediente.product_id.x_pct_humedad / 100) * (self.cantidad * (ingrediente.x_porcentaje / 100)),
                    'carbs_kg': (ingrediente.product_id.x_pct_hidratos_de_carbono / 100) * (self.cantidad * (ingrediente.x_porcentaje / 100)),
                    'azucares_kg': (ingrediente.product_id.x_pct_azucares / 100) * (self.cantidad * (ingrediente.x_porcentaje / 100)),
                    'sodio_mg': ingrediente.product_id.x_mg_sodio * 10 * (self.cantidad * (ingrediente.x_porcentaje / 100))

                })

        if self.ing_limitante:
            ncantidad_il = self.ing_limitante.product_qty
            for ingrediente in ingredientes:
                vals.append({
                    'componente': ingrediente.product_id.name,
                    'cant_comp': self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'pct_proteina': ingrediente.product_id.x_pct_proteinas,
                    'pct_grasas_tot': ingrediente.product_id.x_pct_grasas_totales,
                    'pct_grasas_sat': ingrediente.product_id.x_pct_grasas_saturadas,
                    'pct_grasas_trans': ingrediente.product_id.x_mgkg_grasas_trans,
                    'pct_humedad': ingrediente.product_id.x_pct_humedad,
                    'pct_carbs': ingrediente.product_id.x_pct_hidratos_de_carbono,
                    'pct_azucares': ingrediente.product_id.x_pct_azucares,
                    'mg_sodio': ingrediente.product_id.x_mg_sodio,
                    'proteina_kg': (ingrediente.product_id.x_pct_proteinas / 100) * self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'grasa_kg': (ingrediente.product_id.x_pct_grasas_totales / 100) * self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'grasa_sat_kg': (ingrediente.product_id.x_pct_grasas_saturadas / 100) * self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'grasa_trans_kg': ingrediente.product_id.x_mgkg_grasas_trans * 10 * self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'humedad_kg': (ingrediente.product_id.x_pct_humedad / 100) * self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'carbs_kg': (ingrediente.product_id.x_pct_hidratos_de_carbono / 100) * self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'azucares_kg': (ingrediente.product_id.x_pct_azucares / 100) * self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                    'sodio_mg': ingrediente.product_id.x_mg_sodio * 10 * self.cant_limitante * (ingrediente.product_qty / ncantidad_il)
                })


        data = {'ids': self.ids,
                'model':self._name,
                'vals':vals,
                'producto':self.producto.product_tmpl_id.name,
                'codigo': self.producto.product_tmpl_id.default_code,
                'cantidad':self.cantidad,
                'ing_limitante':self.ing_limitante,
                'nombre_il':self.ing_limitante.product_tmpl_id.name,
                'cant_limitante':self.cant_limitante,
                'pct_merma':self.producto.product_id.x_pct_merma
                }

        if self.producto.product_id.x_pct_merma >= 0:
            raise UserError('producto: '+self.producto.product_id.default_code+'\n'+ 'merma: '+str(self.producto.product_id.x_pct_merma))

        return self.env.ref('sam_reportes.tabla_nutrimental_reporte').report_action(self, data=data)