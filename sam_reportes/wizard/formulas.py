# -*- coding: utf-8 -*-

# formulas.py
# Impresión de la fórmula de un producto..
# VBueno 1707202411:14
# v16
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

    product_tmpl = fields.Many2one('product.template', string="Producto")
    producto = fields.Many2one('mrp.bom', string="Lista de Materiales", domain="[('product_tmpl_id', '=', product_tmpl)]")
    cantidad = fields.Float(string="Cantidad")
    ing_limitante = fields.Many2one('mrp.bom.line',string="Ingrediente limitante")
    cant_limitante = fields.Float(string="Cantidad limitante")
    consolidado = fields.Boolean(string="Fórmula consolidada",  )
    partidas = fields.Integer(string="Partidas")

    # campos para consolidar
    x_secuencia = fields.Char(string="Número")
    ingr = fields.Many2one('product.product', string="Producto")
    cod_prov = fields.Char(string="Código Prov", required=False, )
    cant_tot = fields.Float(string="Cant Total", digits=(12, 4))
    unidad = fields.Char(string="Unidad")
    pct_formula = fields.Float(string="% Fórmula", digits=(6, 4))
    pct_categoria = fields.Float(string="% Grupo", digits=(6, 4))
    pct_merma = fields.Float(string="% Merma", digits=(6, 4))
    x_orden = fields.Char(string="Orden", required=False, )


    @api.onchange('product_tmpl')
    def _onchange_product_tmpl(self):
        # Reset producto when product_tmpl changes
        self.producto = False
        return {'domain': {'producto': [('product_tmpl_id', '=', self.product_tmpl.id)]}}

    # permite seleccionar el ingrediente limitante.
    @api.onchange('producto')
    def onchange_producto(self):
        if self.producto:
            # Reset ing_limitante when producto changes
            self.ing_limitante = False
            self.cant_limitante = 0.0
            
            # Get all BOM lines for the selected BOM
            bom_lines = self.env['mrp.bom.line'].search([('bom_id', '=', self.producto.id)])
            
            # Set domain to only show BOM lines from the selected BOM
            return {'domain': {'ing_limitante': [('id', 'in', bom_lines.ids)]}}
        else:
            self.ing_limitante = False
            self.cant_limitante = 0.0
            return {'domain': {'ing_limitante': [('id', 'in', [])]}}

    def get_orden(self, codigo_producto):
        prefix = codigo_producto[:2]  # Tomar las dos primeras letras
        ordenes = {
            'ca': '1. Cárnicos',
            'ad': '2. Aditivos',
            'in': '3. Intermedios',
            'fb': '5. Fórmulas',
            'fo': '5. Fórmulas'
        }

        return ordenes.get(prefix, '4. Especias')

    def get_codprov(self, producto):
        ccodprov = self.env['product.supplierinfo'].search(
                            [('product_tmpl_id.id', '=', producto)], limit=1
                        ).product_name
        return ccodprov

    def crear_ncomponente(self, ingrediente, secuencia, ncant_limitante):
        ncomponente = self.env['wizard.formulas'].search(
            [('ingr.id', '=', ingrediente.product_id.id),
            ('x_secuencia', '=', secuencia)])

        if not ncomponente:
            codprov = self.get_codprov(ingrediente.product_id.product_tmpl_id.id)
            #norden = self.get_orden(ingrediente.product_id.default_code)
            norden = ingrediente.product_id.x_studio_sub_categoria.name

            self.env['wizard.formulas'].create({
                'x_secuencia': secuencia,
                'ingr': ingrediente.product_id.id,
                'cod_prov': codprov,
                'cant_tot': ncant_limitante,
                'unidad': ingrediente.product_id.uom_id.name,
                'pct_formula': ingrediente.x_porcentaje,
                'pct_categoria': ingrediente.x_porcentaje_categoria,
                'x_orden': norden
            })

        if ncomponente:
            ncant = ncomponente.cant_tot
            nccomp = ncant_limitante
            ncant_tot = ncant + nccomp
            ncomponente.write({'cant_tot': ncant_tot})
            

    def consolida_formula(self, ingredientes, nqty, secuencia):
        for ingrediente in ingredientes:
            ncant_limitante = nqty * (ingrediente.x_porcentaje / 100)
            # verifica que el ingrediente se fabrique.
            if ingrediente.product_id.bom_count > 0:  # tiene subformula
                bom_pf = self.env['mrp.bom'].search([('product_tmpl_id', '=', ingrediente.product_tmpl_id.id)],
                                                    limit=1).id
                subformula = self.env['mrp.bom.line'].search([('bom_id.id', '=', bom_pf)])
                if subformula:
                    self.consolida_formula(subformula, ncant_limitante, secuencia)
                else:
                    self.crear_ncomponente(ingrediente, secuencia, ncant_limitante)
            else:
                self.crear_ncomponente(ingrediente, secuencia, ncant_limitante)

        return

    # imprime formula
    def imprime_formula(self):

        vals=[]
        ingredientes = self.env['mrp.bom.line'].search(
                        [('bom_id.id', '=', self.producto.id)])

        if not self.ing_limitante:

            if self.cant_limitante > 0:
                raise UserError('Falta el ingrediente limitante')

            if self.partidas > 0:
                total_ingredientes = sum(
                    ingrediente.product_qty for ingrediente in ingredientes)
                
                self.cantidad = total_ingredientes * self.partidas


            for ingrediente in ingredientes:

                codprov = self.get_codprov(ingrediente.product_id.product_tmpl_id.id)    

                #norden = self.get_orden(ingrediente.product_id.default_code)
                norden = ingrediente.product_id.x_studio_sub_categoria.name

                vals.append({
                    'componente': ingrediente.product_id.name,
                    'cod_prov': codprov,
                    'cant_comp': ingrediente.product_qty * self.partidas if self.partidas > 0 else self.cantidad * (
                                ingrediente.x_porcentaje / 100),
                    'unidad': ingrediente.product_id.uom_id.name,
                    'pct_formula': ingrediente.x_porcentaje,
                    'pct_categoria': ingrediente.x_porcentaje_categoria,
                    'orden': norden
                })

        if self.ing_limitante:
            self.cantidad = 0
            ncantidad_il = self.ing_limitante.product_qty
            for ingrediente in ingredientes:

                codprov = self.get_codprov(ingrediente.product_id.product_tmpl_id.id)

                norden = self.get_orden(ingrediente.product_id.default_code)

                vals.append({
                        'componente': ingrediente.product_id.name,
                        'cod_prov': codprov,
                        'cant_comp': self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                        'unidad': ingrediente.product_id.uom_id.name,
                        'pct_formula': ingrediente.x_porcentaje,
                        'pct_categoria': ingrediente.x_porcentaje_categoria,
                        'orden': norden
                        })

        # Se consolida la fórmula.
        if self.consolidado:
            vals = []
            nsecuencia = self.env['ir.sequence'].next_by_code('formulas.consolidadas')

            if self.ing_limitante:

                ntotcantidad = 0
                ncantidad_il = self.ing_limitante.product_qty

                for ingrediente in ingredientes:
                    ntotcantidad += self.cant_limitante * (
                                ingrediente.product_qty / ncantidad_il)

                self.cantidad = ntotcantidad

            #consolida la formula
            self.consolida_formula(ingredientes,self.cantidad,nsecuencia)

            #ordena la tabla para la impresión
            bom_consolidada = self.env['wizard.formulas'].search([('x_secuencia','=',nsecuencia)])

            bom_ordenada = sorted(bom_consolidada, key=lambda l: l.cant_tot,
                                  reverse=True)
            bom_ordenada1 = sorted(bom_ordenada, key=lambda l: l.x_orden, reverse=False)

            for ingrediente in bom_ordenada1:
                
                if ingrediente.cant_tot > 0:
                    vals.append({
                        'orden': ingrediente.x_orden,
                        'componente': ingrediente.ingr.name,
                        'cod_prov': ingrediente.cod_prov,
                        'cant_comp': ingrediente.cant_tot,
                        'unidad': ingrediente.ingr.uom_id.name,
                        'pct_formula': (ingrediente.cant_tot / self.cantidad) * 100 ,
                        'pct_categoria': ingrediente.pct_categoria
                    })

        
        data = {'ids': self.ids,
                'model':self._name,
                'vals':vals,
                'producto': self.producto.product_tmpl_id.name + ' - ' + self.producto.code,
                'codigo': self.producto.product_tmpl_id.default_code,
                'cantidad':self.cantidad,
                'ing_limitante':self.ing_limitante,
                'nombre_il':self.ing_limitante.product_tmpl_id.name,
                'cant_limitante':self.cant_limitante
                }

        # Obtener la acción del reporte
        report_action = self.env.ref('sam_reportes.formulas_reporte').report_action(self, data=data)
        
        # Si es una acción de reporte, configurar para cerrar después de la descarga
        if report_action.get('type') == 'ir.actions.report':
            report_action['close_on_report_download'] = True
        
        # Devolver la acción del reporte
        return report_action
