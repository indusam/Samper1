# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_presentacion = fields.Many2one("uom.uom", string="Presentacion")
    x_pct_variacion = fields.Float(string='% Variación', digits=(3, 4))
    x_cod_alergenos = fields.Selection([
        ('no_contiene', 'No contiene'),
        ('leche_soya', 'Puede contener LECHE y SOYA'),
        ('leche', 'Contiene LECHE'),
        ('soya', 'Contiene SOYA'),
        ('leche_y_soya', 'Contiene LECHE y SOYA'),
    ], string='Alergenos')


class ListaMateriales(models.Model):
    _inherit = 'mrp.bom.line'

    x_porcentaje = fields.Float(string="%", digits=(3, 4))
    x_porcentaje_il = fields.Float(string="% IL", digits=(3, 4))
    x_cantidad_il = fields.Float(string="Cantidad Limitante", digits=(12, 4))
    x_ingrediente_limitante = fields.Boolean(string="IL")
    x_cantidad_pzas = fields.Float(string="Cantidad x piezas", digits=(12, 4))
    # información nutrimental vbueno 1512202012:50
    x_proteina_kg = fields.Float(string="Proteína kg", digits=(10, 4))
    x_grasa_kg = fields.Float(string="Grasa kg", digits=(10, 4))
    x_grasa_sat_kg = fields.Float(string="Grasa Sat. kg", digits=(10, 4))
    x_humedad_kg = fields.Float(string="Humedad kg", digits=(10, 4))
    x_carbs_kg = fields.Float(string="Carbs. kg", digits=(10, 4))
    x_azucares_kg = fields.Float(string="Azúcares kg", digits=(10, 4))
    x_sodio_mg = fields.Float(string="Sodio mg/kg", digits=(10, 4))


class ListaMaterialesHeader(models.Model):
    _inherit = 'mrp.bom'

    product_qty = fields.Float(string="Cantidad", digits=(12, 4))
    x_piezas = fields.Integer(string='Piezas:')
    x_cantidad_pzas = fields.Float(string='Cantidad x piezas', digits=(12, 4))
    x_cantidad_il = fields.Float(string="Cantidad Limitante", digits=(12, 4))
    x_ingrediente_limitante = fields.Many2one("mrp.bom.line",
                                              string="Ingrediente limitante")

    @api.onchange('x_cantidad_il')
    def onchange_x_cantidad_il(self):
        nlista = self.product_tmpl_id.id
        for rec in self:
            return {'domain': {'x_ingrediente_limitante':
                                   [('parent_product_tmpl_id', '=', nlista)]}}

    @api.onchange('x_piezas')
    def onchange_x_piezas(self):
        if self.x_piezas > 0:
            for rec in self:
                npresentacion = rec.env['product.template'].search(
                    [('id', '=', rec.product_tmpl_id.id)],
                    limit=1).x_presentacion.id
                nfactor = rec.env['uom.uom'].search(
                    [('id', '=', npresentacion)], limit=1).factor_inv

                ncantidad = nfactor * self.x_piezas

                rec.x_cantidad_pzas = ncantidad

    @api.onchange('x_cantidad_pzas')
    def onchange_product_qty(self):
        for item in self.bom_line_ids:
            ncant_ingr = self.x_cantidad_pzas * (item.x_porcentaje / 100)
            item.x_cantidad_pzas = ncant_ingr

    @api.onchange('x_ingrediente_limitante')
    def onchange_x_ingrediente_limitante(self):

        # Busca el ingrediente limitante
        ningrediente = self.x_ingrediente_limitante.id
        ncantidad_il = 0
        nlista = self.env['mrp.bom.line'].search(
            [('parent_product_tmpl_id', '=', self.product_tmpl_id.id)])
        for item in nlista:
            if item.id == ningrediente:
                ncantidad_il = item.product_qty
                item.x_ingrediente_limitante = True
            else:
                item.x_ingrediente_limitante = False

        # Si la cantidad limitante = 0, borra las cantidades y porcentajes
        # limitantes de la fórmula, de lo contrario hace los cálculos
        if self.x_cantidad_il == 0:
            self.x_ingrediente_limitante = False
            for item in self.bom_line_ids:
                item.x_porcentaje_il = 0
                item.x_cantidad_il = 0
                item.x_ingrediente_limitante = False
        else:
            # si hay ingrediente limitante hace los cálculos.
            if ningrediente != 0:
                # Calcula el total de las cantidades de los ingredientes
                # de la fórmula
                ntotal = 0
                for item in self.bom_line_ids:
                    ntotal = ntotal + item.product_qty

                # Calcula las cantidades en base al ingrediente limitante
                for item in self.bom_line_ids:
                    item.x_cantidad_il = (self.x_cantidad_il * item.product_qty) / ncantidad_il

                # Calcula el total de la cantidades con los ingredientes
                # limitantes
                ntotal = 0
                for item in self.bom_line_ids:
                    ntotal = ntotal + item.x_cantidad_il

                # Calcula el porcentaje de los ingredientes.
                for item in self.bom_line_ids:
                    if ntotal > 0:
                        item.x_porcentaje_il = (item.x_cantidad_il / ntotal) * 100
                    else:
                        item.x_porcentaje_il = 0

                # vbueno 1512202013:18
                # Calcula la información nutrimental en base a la cantidad limitante
                for item in self.bom_line_ids:
                    x_proteina_kg = (item.product_id.x_pct_proteinas / 100) * item.x_cantidad_il
                    x_grasa_kg = (item.product_id.x_pct_grasas_totales / 100) * item.x_cantidad_il
                    x_grasa_sat_kg = (item.product_id.x_pct_grasas_saturadas / 100) * item.x_cantidad_il
                    x_humedad_kg = (item.product_id.x_pct_humedad / 100) * item.x_cantidad_il
                    x_carbs_kg = (item.product_id.x_pct_hidratos_de_carbono / 100) * item.x_cantidad_il
                    x_azucares_kg = (item.product_id.x_pct_azucares / 100) * item.x_cantidad_il
                    x_sodio_mg = item.product_id.x_mg_sodio * item.x_cantidad_il

            else:
                # si no hay ingrediente limitante, limpia las cantidades
                # y porcentajes limitantes de la fórmula
                for item in self.bom_line_ids:
                    item.x_porcentaje_il = 0
                    item.x_cantidad_il = 0
                    item.x_ingrediente_limitante = False

                self.x_cantidad_il = 0
                # vbueno 1512202013:18
                # Calcula la información nutrimental en base a la cantidad a producir.
                for item in self.bom_line_ids:
                    x_proteina_kg = (item.product_id.x_pct_proteinas / 100) * item.product_qty
                    x_grasa_kg = (item.product_id.x_pct_grasas_totales / 100) * item.product_qty
                    x_grasa_sat_kg = (item.product_id.x_pct_grasas_saturadas / 100) * item.product_qty
                    x_humedad_kg = (item.product_id.x_pct_humedad / 100) * item.product_qty
                    x_carbs_kg = (item.product_id.x_pct_hidratos_de_carbono / 100) * item.product_qty
                    x_azucares_kg = (item.product_id.x_pct_azucares / 100) * item.product_qty
                    x_sodio_mg = item.product_id.x_mg_sodio * item.product_qty

class ReporteInventario(models.Model):
    _inherit = 'stock.quant'
    inventory_quantity = fields.Float(string="Cantidad Disponible",
                                      digits=(12, 4))
