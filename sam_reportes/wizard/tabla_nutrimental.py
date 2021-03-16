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

    producto = fields.Many2one('product.product', string="Producto")
    cantidad = fields.Float(string="Cantidad")
    ing_limitante = fields.Many2one('mrp.bom.line',string="Ingrediente limitante")
    cant_limitante = fields.Float(string="Cantidad Limitante")
    proteina_kg = fields.Float(string="Proteína kg")
    grasa_kg = fields.Float(string="Grasa kg")
    grasa_sat_kg = fields.Float(string="Grasa sat kg")
    humedad_kg = fields.Float(string="Humedad kg")
    carbs_kg = fields.Float(string="Carbs kg")
    azucares_kg = fields.Float(string="Azúcares kg")
    sodio_mg = fields.Float(string="Sodio mg/kg")
    # product_ref = fields.Char(
    #    related="product_id.default_code", string="Referencia Interna")


    # imprime la tabla nutrimental.
    def imprime_tabla_nutrimental(self):
        raise UserError("Imprimiendo...")


#        vals=[]
#        ingredientes =  self.env['mrp.bom.line'].search([('bom_id.id','=',self.producto)])


#        for producto in productos:
#            ventas = self.env['account.move.line'].search([('date','>=',self.fecha_inicial),
#                                                           ('date','<=',self.fecha_final),
#                                                           ('product_id','=',producto.id)],limit=1).id

#            if not ventas:
#                vals.append({
#                    'prod':producto.id,
#                    'nombre':producto.name,
#                    'referencia':producto.product_tmpl_id.default_code,
#                    'exis':producto.product_tmpl_id.qty_available,
#                    'costo':producto.product_tmpl_id.standard_price,
#                    'valor':producto.product_tmpl_id.qty_available * producto.product_tmpl_id.standard_price
#                })


#        data = {'ids': self.ids,
#                'model':self._name,
#                'vals':vals,
#                'inicio':self.fecha_inicial,
#                'final':self.fecha_final,
#                'marca':self.marca
#                }

#        return self.env.ref('gr_prod_sin_ventas.prod_sin_ventas_reporte').report_action(self, data=data)