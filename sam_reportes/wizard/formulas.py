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

    # campos para consolidar
    x_secuencia = fields.Char(string="Número")
    ingr = fields.Many2one('product.product', string="Producto")
    cod_prov = fields.Char(string="Código Prov", required=False, )
    cant_tot = fields.Float(string="Cant Total", digits=(12, 4))
    unidad = fields.Char(string="Unidad")
    pct_formula = fields.Float(string="% Fórmula", digits=(6, 2))
    pct_categoria = fields.Float(string="% Grupo", digits=(6, 2))
    x_orden = fields.Integer(string="Orden", required=False, )


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

        if not self.consolidado:

            if not self.ing_limitante:
                for ingrediente in ingredientes:
                    codprov = self.env['product.supplierinfo'].search(
                        [('product_tmpl_id.id','=',ingrediente.product_id.product_tmpl_id.id)], limit=1
                    ).product_name

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
                        [('product_tmpl_id.id', '=', ingrediente.product_id.product_tmpl_id.id)], limit=1
                    ).product_name

                    vals.append({
                        'componente': ingrediente.product_id.name,
                        'cod_prov': codprov,
                        'cant_comp': self.cant_limitante * (ingrediente.product_qty / ncantidad_il),
                        'unidad': ingrediente.product_id.uom_id.name,
                        'pct_formula': ingrediente.x_porcentaje,
                        'pct_categoria': ingrediente.x_porcentaje_categoria
                        })

        # Se consolida la fórmula.
        if self.consolidado:
            nsecuencia = self.env['ir.sequence'].next_by_code('formulas.consolidadas')

            for ingrediente in ingredientes:
                # verifica que el ingrediente se fabrique.
                # las rutas pueden incluir comprar, fabricar, vender, etc.
                subf = 0
                rutas = ingrediente.product_tmpl_id.route_ids
                for ruta in rutas:
                    if ruta.id == 5: # 5 == fabricar
                        subf = 1
                        break

                if subf == 1:
                    ncant_limitante = self.cantidad * (ingrediente.x_porcentaje / 100)

                    bom_pf = self.env['mrp.bom'].search([(
                        'product_tmpl_id','=',ingrediente.product_tmpl_id.id)]).id

                    subformula = self.env['mrp.bom.line'].search([
                        ('bom_id.id', '=', bom_pf)])

                    if not subformula:
                        subf = 0

                    for componente in subformula:
                        ncomponente = self.env['wizard.formulas'].search(
                                [('ingr.id','=', componente.product_id.id),
                                 ('x_secuencia','=',nsecuencia)])

                        if not ncomponente:
                            codprov = self.env['product.supplierinfo'].search(
                                [('product_tmpl_id.id', '=',
                                  componente.product_id.product_tmpl_id.id)], limit=1
                            ).product_name

                            norden = 0
                            if 'ca' in componente.product_id.default_code:
                                norden = 1
                            elif 'ad' in componente.product_id.default_code:
                                norden = 2
                            elif 'in' in componente.product_id.default_code:
                                norden = 3
                            else:
                                norden = 4

                            self.env['wizard.formulas'].create({
                                'x_secuencia':nsecuencia,
                                'ingr': componente.product_id.id,
                                'cod_prov': codprov,
                                'cant_tot': ncant_limitante * (componente.x_porcentaje / 100),
                                'unidad': componente.product_id.uom_id.name,
                                'pct_formula': componente.x_porcentaje,
                                'pct_categoria': componente.x_porcentaje_categoria,
                                'x_orden': norden
                            })

                        if ncomponente:
                            ncant = ncomponente.cant_tot
                            ncomponente.write({'cant_tot':(ncant_limitante * (componente.x_porcentaje / 100)) + ncant})

                if subf == 0:
                    ncant_limitante = self.cantidad * (
                                ingrediente.x_porcentaje / 100)

                    ncomponente = self.env['wizard.formulas'].search(
                        [('ingr.id', '=', componente.product_id.id),
                         ('x_secuencia', '=', nsecuencia)])

                    if not ncomponente:
                        codprov = self.env['product.supplierinfo'].search(
                            [('product_tmpl_id.id', '=', ingrediente.product_id.product_tmpl_id.id)], limit=1
                        ).product_name

                        norden = 0
                        if 'ca' in ingrediente.product_id.default_code:
                            norden = 1
                        elif 'ad' in ingrediente.product_id.default_code:
                            norden = 2
                        elif 'in' in ingrediente.product_id.default_code:
                            norden = 3
                        else:
                            norden = 4

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
                        nccomp = ncant_limitante * (componente.x_porcentaje / 100)
                        ncant_tot = ncant + nccomp

                        raise UserError('ncant: '+str(ncant)+'\n'+
                                        'nccomp: '+str(nccomp)+'\n'+
                                        'ncant_tot: '+str(ncant_tot))

                        ncomponente.write({'cant_tot': ncant_tot})

            bom_consolidada = self.env['wizard.formulas'].search([('x_secuencia','=',nsecuencia)])
            bom_ordenada = sorted(bom_consolidada, key=lambda l: (l.x_orden), reverse=False)
            for ingrediente in bom_ordenada:
                if ingrediente.cant_tot > 0:
                    vals.append({
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

        return self.env.ref('sam_reportes.formulas_reporte').report_action(self, data=data)

