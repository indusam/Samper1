# -*- coding: utf-8 -*-

# formula_base_carnicos.py
# Impresión de la fórmula de un producto basado en la salmuera  
# VBueno 1808202213_37

# Impresión de la fórmula de un producto con y sin consolidación.
# Los cárnicos son ingredientes limitantes.
# Si una fórmula tiene un ingrediente fórmula, suma las cantidades de los ingr.
# de ambas fórmulas e imprime el resultado.

import logging
from odoo.tools.float_utils import float_round
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FormulaBaseSalmuera(models.TransientModel):

    _name = 'wizard.formula.base.salmuera'
    _description = 'Fórmula base salmuera'

    product_tmpl = fields.Many2one('product.template', string="Producto")
    producto = fields.Many2one('mrp.bom', string="Lista de Materiales", domain="[('product_tmpl_id', '=', product_tmpl)]")
    cantidad = fields.Float(string="Total Salmuera")
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
    pct_merma = fields.Float(string="% Merma", digits=(6, 2))
    x_orden = fields.Char(string="Orden", required=False, )


    @api.onchange('product_tmpl')
    def _onchange_product_tmpl(self):
        # Reset producto when product_tmpl changes
        self.producto = False
        return {'domain': {'producto': [('product_tmpl_id', '=', self.product_tmpl.id)]}}

    # permite seleccionar el ingrediente limitante.
    @api.onchange('producto')
    def onchange_producto(self):
        nlista = self.producto.id
        return {'domain': {'ing_limitante': [('bom_id', '=', nlista)]}}

    # imprime formula
    def imprime_formula_base_salmuera(self):
        if not self.producto:
            raise UserError('Debe seleccionar una lista de materiales')
            
        # calcula el total de salmuera de la formula
        total_salmuera = 0
        ingredientes = self.env['mrp.bom.line'].search([('bom_id', '=', self.producto.id)])
        for ingrediente in ingredientes:
            if not 'CÁRNICOS' in ingrediente.product_id.categ_id.name:
                total_salmuera += ingrediente.product_qty

        if total_salmuera == 0:
            raise UserError('No hay ingredientes cárnicos en la fórmula')
        

        # calcula el porcentaje del grupo de salmuera en la formula.
        for ingrediente in ingredientes:
            if not 'CÁRNICOS' in ingrediente.product_id.categ_id.name:
                ingrediente.write({'x_porcentaje_categoria':(ingrediente.product_qty / total_salmuera) * 100})
                    

        # recorre los ingredientes de la fórmula, el primer ingrediente cárnicos es el ingrediente limitante.
        for ingrediente in ingredientes:
            if not 'CÁRNICOS' in ingrediente.product_id.categ_id.name:
                self.ing_limitante = ingrediente
                self.cant_limitante = self.cantidad * ingrediente.x_porcentaje_categoria / 100
                break

        # Guarda los datos de la fórmula en el modelo transient.               
        vals=[]        
        if not self.consolidado:

            if self.ing_limitante:
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
                        norden = '4'

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
            nsecuencia = self.env['ir.sequence'].next_by_code('formulas.consolidadas')

            # obtiene el total de la cantidad de la fórmula con los ingredientes carnicos.
            total_cantidad = 0
            ncantidad_il = self.ing_limitante.product_qty
            for ingrediente in ingredientes:
                total_cantidad += self.cant_limitante * (ingrediente.product_qty / ncantidad_il)


            for ingrediente in ingredientes:
                # verifica que el ingrediente se fabrique.
                # las rutas pueden incluir comprar, fabricar, vender, etc.
                subf = 0
                if ingrediente.product_id.bom_count > 0:
                    subf = 1

                if subf == 1:
                    ncant_limitante = total_cantidad * (ingrediente.x_porcentaje / 100)

                    bom_pf = self.env['mrp.bom'].search([(
                        'product_tmpl_id','=',ingrediente.product_tmpl_id.id)], limit=1).id

                    subformula = self.env['mrp.bom.line'].search([
                        ('bom_id.id', '=', bom_pf)])

                    if not subformula:
                        subf = 0

                    for componente in subformula:
                        ncomponente = self.env['wizard.formula.base.salmuera'].search(
                                [('ingr.id','=', componente.product_id.id),
                                 ('x_secuencia','=',nsecuencia)])

                        if not ncomponente:
                            codprov = self.env['product.supplierinfo'].search(
                                [('product_tmpl_id.id', '=',
                                  componente.product_id.product_tmpl_id.id)], limit=1
                            ).product_name

                            if 'ca' in ingrediente.product_id.default_code:
                                norden = '1 Cárnicos'
                            elif 'ad' in ingrediente.product_id.default_code:
                                norden = '2 Aditivos'
                            elif 'in' in ingrediente.product_id.default_code:
                                norden = '3 Intermedios'
                            else:
                                norden = '4'

                            self.env['wizard.formula.base.salmuera'].create({
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
                    ncant_limitante = total_cantidad * (ingrediente.x_porcentaje / 100)

                    ncomponente = self.env['wizard.formula.base.salmuera'].search(
                        [('ingr.id', '=', ingrediente.product_id.id),
                         ('x_secuencia', '=', nsecuencia)])

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
                            norden = '4'

                        self.env['wizard.formula.base.salmuera'].create({
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

            bom_consolidada = self.env['wizard.formula.base.salmuera'].search([('x_secuencia','=',nsecuencia)])
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
                'cant_limitante':self.cantidad
                }

        # Obtener la acción del reporte
        report_action = self.env.ref('sam_reportes.formula_base_salmuera_reporte').report_action(self, data=data)
        
        # Si es una acción de reporte, configurar para cerrar después de la descarga
        if report_action.get('type') == 'ir.actions.report':
            report_action['close_on_report_download'] = True
        
        # Devolver la acción del reporte
        return report_action

