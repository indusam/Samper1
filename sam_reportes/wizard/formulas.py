# -*- coding: utf-8 -*-

# formulas.py
# Impresión de la fórmula de un producto..
# VBueno 2505202111:46
#
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


    # permite seleccionar el ingrediente limitante.
    @api.onchange('producto')
    def onchange_producto(self):
        nlista = self.producto.id
        # self.pct_merma = self.producto.product_tmpl_id.x_pct_merma
        for rec in self:
            return {'domain': {'ing_limitante':
                                   [('bom_id', '=', nlista)]}}


    # imprime formula
    def imprime_formula(self):

        vals=[]
        ingredientes = self.env['mrp.bom.line'].search(
                        [('bom_id.id', '=', self.producto.id)])

        # no se consolida la fórmula
        #if not self.consolidado:

        if not self.ing_limitante:

            if self.cant_limitante > 0:
                raise UserError('Falta el ingrediente limitante')

            if self.partidas > 0:
                total_ingredientes = sum(
                    ingrediente.product_qty for ingrediente in ingredientes)
                self.cantidad = total_ingredientes * self.partidas

            #else:
            #    total_ingredientes = sum(
            #        ingrediente.product_qty for ingrediente in ingredientes)
            #    self.cantidad = total_ingredientes
            # test

            for ingrediente in ingredientes:
                codprov = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=',
                      ingrediente.product_id.product_tmpl_id.id)], limit=1
                ).product_name

                if 'ca' in ingrediente.product_id.default_code:
                    norden = '1 Cárnicos'
                elif 'ad' in ingrediente.product_id.default_code:
                    norden = '2 Aditivos'
                elif 'in' in ingrediente.product_id.default_code:
                    norden = '3 Intermedios'
                else:
                    norden = '4 '

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
                codprov = self.env['product.supplierinfo'].search(
                        [('product_tmpl_id.id', '=', ingrediente.product_id.product_tmpl_id.id)], limit=1
                        ).product_name

                if 'ca' in ingrediente.product_id.default_code:
                    norden = '1 Cárnicos'
                elif 'ad' in ingrediente.product_id.default_code:
                    norden = '2 Aditivos'
                elif 'in' in ingrediente.product_id.default_code:
                    norden = '3 Intermedios'
                else:
                    norden = '4 '

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


            for ingrediente in ingredientes:
                # verifica que el ingrediente se fabrique.
                if ingrediente.product_id.bom_count > 0: #tiene subformula

                    ncant_limitante = self.cantidad * (ingrediente.x_porcentaje / 100)

                    bom_pf = self.env['mrp.bom'].search([(
                        'product_tmpl_id','=',ingrediente.product_tmpl_id.id)], limit=1).id

                    subformula_n1 = self.env['mrp.bom.line'].search([
                        ('bom_id.id', '=', bom_pf)])

                    for componente_n1 in subformula_n1:

                        ncomponente_n1 = self.env['wizard.formulas'].search(
                                [('ingr.id','=', componente_n1.product_id.id),
                                 ('x_secuencia','=',nsecuencia)])

                        if not ncomponente_n1:
                            codprov = self.env['product.supplierinfo'].search(
                                [('product_tmpl_id.id', '=',
                                  componente_n1.product_id.product_tmpl_id.id)], limit=1
                            ).product_name

                            if 'ca' in componente_n1.product_id.default_code:
                                norden = '1 Cárnicos'
                            elif 'ad' in componente_n1.product_id.default_code:
                                norden = '2 Aditivos'
                            elif 'in' in componente_n1.product_id.default_code:
                                norden = '3 Intermedios'
                            else:
                                norden = '4 '

                            self.env['wizard.formulas'].create({
                                'x_secuencia':nsecuencia,
                                'ingr': componente_n1.product_id.id,
                                'cod_prov': codprov,
                                'cant_tot': ncant_limitante * (componente_n1.x_porcentaje / 100),
                                'unidad': componente_n1.product_id.uom_id.name,
                                'pct_formula': componente_n1.x_porcentaje,
                                'pct_categoria': componente_n1.x_porcentaje_categoria,
                                'x_orden': norden
                            })

                        if ncomponente_n1:
                            ncant = ncomponente_n1.cant_tot
                            ncomponente_n1.write({'cant_tot':(ncant_limitante * (componente_n1.x_porcentaje / 100)) + ncant})

                else:
                    ncant_limitante = self.cantidad * (ingrediente.x_porcentaje / 100)

                    ncomponente = self.env['wizard.formulas'].search(
                        [('ingr.id', '=', ingrediente.product_id.id),
                         ('x_secuencia', '=', nsecuencia)])

                    # raise UserError(ingrediente.product_id.name)

                    if not ncomponente:
                        codprov = self.env['product.supplierinfo'].search(
                            [('product_tmpl_id.id', '=', ingrediente.product_id.product_tmpl_id.id)], limit=1
                        ).product_name

                        if 'ca' in ingrediente.product_id.default_code:
                            norden = '1 Cárnicos'
                        elif 'ad' in ingrediente.product_id.default_code:
                            norden = '2 Aditivos'
                        elif 'in' in ingrediente.product_id.default_code:
                            norden = '3 Intermedios'
                        else:
                            norden = '4 '

                        self.env['wizard.formulas'].create({
                                    'x_secuencia':nsecuencia,
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
                'producto':self.producto.product_tmpl_id.name,
                'codigo': self.producto.product_tmpl_id.default_code,
                'cantidad':self.cantidad,
                'ing_limitante':self.ing_limitante,
                'nombre_il':self.ing_limitante.product_tmpl_id.name,
                'cant_limitante':self.cant_limitante
                }
        self.cantidad = 0
        self.producto = 0
        self.partidas = 0

        return self.env.ref('sam_reportes.formulas_reporte').report_action(self, data=data)

