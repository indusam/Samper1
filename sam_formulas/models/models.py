# -*- coding: utf-8  -*-
# vbueno 2606202510:35

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    """
    Extiende el modelo product.template para agregar campos adicionales relacionados
    con la presentación y variación del producto.
    """
    _inherit = 'product.template'

    x_presentacion = fields.Many2one("uom.uom", string="Presentacion",
        help="Unidad de medida que representa la presentación del producto")
    x_pct_variacion = fields.Float(string='% Variación', digits=(3, 4),
        help="Porcentaje de variación permitido para el producto seleccionado")


class ListaMateriales(models.Model):
    """
    Extiende el modelo mrp.bom.line para agregar campos adicionales relacionados
    con porcentajes, cantidades e información nutricional de los ingredientes.
    """
    _inherit = 'mrp.bom.line'

    # Campos para porcentajes y cantidades
    x_porcentaje = fields.Float(string="%", digits=(3, 4),
        help="Porcentaje del ingrediente en la fórmula")
    x_porcentaje_il = fields.Float(string="% IL", digits=(3, 4),
        help="Porcentaje del ingrediente limitante")
    x_cantidad_il = fields.Float(string="Cantidad Limitante", digits=(12, 4),
        help="Cantidad del ingrediente limitante")
    x_ingrediente_limitante = fields.Boolean(string="IL",
        help="Indica si es un ingrediente limitante")
    x_cantidad_pzas = fields.Float(string="Cantidad x piezas", digits=(12, 4),
        help="Cantidad del ingrediente por pieza")

    # Campos para información nutricional por kilogramo
    x_proteina_kg = fields.Float(string="Proteína kg", digits=(10, 4),
        help="Cantidad de proteína por kilogramo")
    x_grasa_kg = fields.Float(string="Grasa kg", digits=(10, 4),
        help="Cantidad de grasa por kilogramo")
    x_grasa_sat_kg = fields.Float(string="Grasa Sat. kg", digits=(10, 4),
        help="Cantidad de grasa saturada por kilogramo")
    x_humedad_kg = fields.Float(string="Humedad kg", digits=(10, 4),
        help="Cantidad de humedad por kilogramo")
    x_carbs_kg = fields.Float(string="Carbs. kg", digits=(10, 4),
        help="Cantidad de carbohidratos por kilogramo")
    x_azucares_kg = fields.Float(string="Azúcares kg", digits=(10, 4),
        help="Cantidad de azúcares por kilogramo")
    x_sodio_mg = fields.Float(string="Sodio mg/kg", digits=(10, 4),
        help="Cantidad de sodio en miligramos por kilogramo")


class ListaMaterialesHeader(models.Model):
    """
    Extiende el modelo mrp.bom (Lista de Materiales) para agregar campos adicionales
    relacionados con cantidades, piezas e ingredientes limitantes.
    """
    _inherit = 'mrp.bom'

    product_qty = fields.Float(string="Cantidad", digits=(12, 4),
        help="Cantidad total del producto en la lista de materiales")
    x_piezas = fields.Integer(string='Piezas:',
        help="Número de piezas a producir")
    x_cantidad_pzas = fields.Float(string='Cantidad x piezas', digits=(12, 4),
        help="Cantidad calculada por número de piezas")
    x_cantidad_il = fields.Float(string="Cantidad Limitante", digits=(12, 4),
        help="Cantidad del ingrediente limitante en la fórmula")
    x_ingrediente_limitante = fields.Many2one("mrp.bom.line",
                                              string="Ingrediente limitante",
                                              help="Ingrediente que limita la producción de la fórmula")    
    x_qty_of_product = fields.Float(string="Cantidad", 
                                    digits=(12,4), 
                                    compute='_compute_x_percentage_of_product',
                                    help="Cantidad calculada del producto")
    x_percentage_of_product = fields.Float(
        string='% de la fórmula',
        digits = (3,4),
        compute='_compute_x_percentage_of_product',
        help="Porcentaje que representa el producto en la fórmula"
    )


    @api.depends('bom_line_ids.x_porcentaje', 'bom_line_ids.product_id', 'bom_line_ids.product_qty')
    def _compute_x_percentage_of_product(self):
        """
        Calcula el porcentaje y la cantidad del producto en la lista de materiales.

        Este método se ejecuta cuando cambian los campos x_porcentaje, product_id o product_qty
        de las líneas de la lista de materiales (bom_line_ids).

        Busca el producto actual en el contexto y encuentra su línea correspondiente en la lista
        de materiales para obtener su porcentaje y cantidad. Estos valores se asignan a los campos
        calculados x_percentage_of_product y x_qty_of_product.

        Dependencias:
            - bom_line_ids.x_porcentaje: Porcentaje del ingrediente en la fórmula
            - bom_line_ids.product_id: ID del producto en la línea
            - bom_line_ids.product_qty: Cantidad del producto en la línea

        Returns:
            None - Actualiza los campos calculados directamente
        """
        for bom in self:
            # Intentar obtener el product_id desde el contexto
            product_id = self.env.context.get('default_product_id') or self.env.context.get('active_id') or self.env.context.get('product_id')
            percentage = 0.0  # Valor predeterminado
            qty = 0.0

            if product_id:
                # Buscamos la línea que coincide con el product_id
                found_percentage = False
                for line in bom.bom_line_ids:
                    if line.product_id.product_tmpl_id.id == product_id:
                        percentage = line.x_porcentaje
                        qty = line.product_qty
                        found_percentage = True
                        break  # Salimos del bucle una vez que encontramos el porcentaje
            
            # Asignar el porcentaje al campo calculado
            bom.write({'x_percentage_of_product': percentage,
                        'x_qty_of_product': qty})


    @api.onchange('x_cantidad_il')
    def onchange_x_cantidad_il(self):
        """
        Establece un dominio para el campo 'x_ingrediente_limitante' basado en la 
        plantilla de producto actual. 

        Cuando cambia 'x_cantidad_il', filtra los ingredientes limitantes para 
        que solo muestre aquellos relacionados con la plantilla del producto actual.
        """
        nlista = self.product_tmpl_id.id
        for rec in self:
            return {'domain': {'x_ingrediente_limitante':
                                   [('parent_product_tmpl_id', '=', nlista)]}}

    @api.onchange('x_piezas')
    def onchange_x_piezas(self):
        """
        Calcula y actualiza la cantidad por piezas ('x_cantidad_pzas') 
        cuando cambia el número de piezas ('x_piezas').

        Si 'x_piezas' es mayor a 0, busca la presentación del producto y su 
        factor de conversión inverso ('factor_inv') para determinar la cantidad 
        total correspondiente en función del número de piezas.
        """
        if self.x_piezas > 0:
            for rec in self:
                # Obtiene la presentación del producto actual
                npresentacion = rec.env['product.template'].search(
                    [('id', '=', rec.product_tmpl_id.id)],
                    limit=1).x_presentacion.id
                
                # Obtiene el factor de conversión inverso de la unidad de medida
                nfactor = rec.env['uom.uom'].search(
                    [('id', '=', npresentacion)], limit=1).factor_inv

                # Calcula la cantidad total basada en el número de piezas
                ncantidad = nfactor * self.x_piezas

                # Asigna el valor calculado al campo 'x_cantidad_pzas'
                rec.x_cantidad_pzas = ncantidad

    @api.onchange('x_cantidad_pzas')
    def onchange_product_qty(self):
        """
        Calcula y actualiza la cantidad por piezas de cada ingrediente en la lista de materiales
        cuando cambia la cantidad total de piezas.

        Para cada línea en la lista de materiales (bom_line_ids):
        - Calcula la cantidad del ingrediente multiplicando la cantidad total de piezas
          por el porcentaje del ingrediente
        - Actualiza el campo x_cantidad_pzas del ingrediente con la cantidad calculada
        """
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
