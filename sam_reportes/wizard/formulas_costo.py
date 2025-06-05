# -*- coding: utf-8 -*-

# formulas.py
# Impresión de la fórmula de un producto..
# VBueno 1605202511:44
# .
# Impresión de la fórmula de un producto con y sin consolidación.
# Si una fórmula tiene un ingrediente fórmula, suma las cantidades de los ingr.
# de ambas fórmulas e imprime el resultado.

import logging
from odoo.tools.float_utils import float_round
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FormulasCosto(models.TransientModel):

    _name = 'wizard.formulas.costo'
    _description = 'Fórmulas con costeo'

    tipo_costo = fields.Selection(
        [('ultimo', 'Último Costo'), ('autorizado', 'Costo Autorizado')],
        string='Tipo de Costo',
        default='ultimo',
        required=True
    )
    producto = fields.Many2one('mrp.bom', string="Producto")
    cantidad = fields.Float(string="Cantidad")
    ing_limitante = fields.Many2one('mrp.bom.line',string="Ingrediente limitante")
    cant_limitante = fields.Float(string="Cantidad limitante")
    consolidado = fields.Boolean(string="Fórmula consolidada",  )
    partidas = fields.Integer(string="Partidas")
    costo_total = fields.Float(string="Costo")

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
    costo = fields.Float(string="Costo")
    costo_usd = fields.Float(string="Costo USD")


    def get_costo_autorizado(self, producto):
        """Obtiene el costo autorizado del producto desde product.supplierinfo"""
        # Buscar primero en la variante del producto (product.product)
        supplier_info = self.env['product.supplierinfo'].search([
            '|',
            ('product_tmpl_id', '=', producto.product_tmpl_id.id),
            '&',
                ('product_id', '=', producto.id),
                ('product_tmpl_id', '=', producto.product_tmpl_id.id)
        ], order='sequence, id', limit=1)
        
        # Si no se encuentra, buscar en la plantilla del producto
        if not supplier_info:
            supplier_info = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', producto.product_tmpl_id.id),
                ('product_id', '=', False)
            ], order='sequence, id', limit=1)
        
        if supplier_info and supplier_info.price > 0:
            # Si el precio está en USD, convertirlo a MXN
            if supplier_info.currency_id and supplier_info.currency_id.name == 'USD':
                tipo_cambio = self.env.company.x_studio_tipo_de_cambio or 1.0
                return supplier_info.price * tipo_cambio
            return supplier_info.price
        return 0.0

    def get_costo_autorizado_usd(self, producto):
        """Obtiene el costo autorizado en USD del producto desde product.supplierinfo"""
        # Buscar primero en la variante del producto (product.product)
        supplier_info = self.env['product.supplierinfo'].search([
            '|',
            ('product_tmpl_id', '=', producto.product_tmpl_id.id),
            '&',
                ('product_id', '=', producto.id),
                ('product_tmpl_id', '=', producto.product_tmpl_id.id)
        ], order='sequence, id', limit=1)
        
        # Si no se encuentra, buscar en la plantilla del producto
        if not supplier_info:
            supplier_info = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', producto.product_tmpl_id.id),
                ('product_id', '=', False)
            ], order='sequence, id', limit=1)
        
        if supplier_info and supplier_info.price > 0:
            if supplier_info.currency_id and supplier_info.currency_id.name == 'USD':
                return supplier_info.price
        return 0.0

    def get_ultimo_costo(self, producto):
        # Buscar la última compra del producto
        ultima_compra = self.env['purchase.order.line'].search([
            ('product_id', '=', producto.id),
            ('state', 'in', ['purchase', 'done'])
        ], order='create_date desc', limit=1)

        if ultima_compra:
            # Obtener el tipo de cambio configurado en la compañía
            tipo_cambio = self.env.company.x_studio_tipo_de_cambio or 1.0
            
            # Si la moneda es USD, convertir a pesos
            if ultima_compra.order_id.currency_id.name == 'USD':
                return ultima_compra.price_unit * tipo_cambio
            else:
                return ultima_compra.price_unit
                
        return producto.standard_price  # Si no hay compras, retorna el costo estándar

    def get_ultimo_costo_usd(self, producto):
        # Buscar la última compra del producto
        ultima_compra = self.env['purchase.order.line'].search([
            ('product_id', '=', producto.id),
            ('state', 'in', ['purchase', 'done'])
        ], order='create_date desc', limit=1)

        if ultima_compra:
            # Si la moneda es USD, retornar el precio en USD
            if ultima_compra.order_id.currency_id.name == 'USD':
                return ultima_compra.price_unit
            else:
                return 0.0  # Si está en pesos, retornar 0
                
        return 0.0  # Si no hay compras, retornar 0


    # permite seleccionar el ingrediente limitante.
    @api.onchange('producto')
    def onchange_producto(self):
        nlista = self.producto.id
        # self.pct_merma = self.producto.product_tmpl_id.x_pct_merma
        for rec in self:
            return {'domain': {'ing_limitante':
                                   [('bom_id', '=', nlista)]}}

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

    def crear_ncomponente_costo(self, ingrediente, secuencia, ncant_limitante):
        ncomponente = self.env['wizard.formulas.costo'].search(
            [('ingr.id', '=', ingrediente.product_id.id),
            ('x_secuencia', '=', secuencia)])

        if not ncomponente:
            codprov = self.get_codprov(ingrediente.product_id.product_tmpl_id.id)
            norden = ingrediente.product_id.x_studio_sub_categoria.name
            
            # Determinar qué costo usar según la selección
            if self.tipo_costo == 'autorizado':
                costo = self.get_costo_autorizado(ingrediente.product_id)
                costo_usd = self.get_costo_autorizado_usd(ingrediente.product_id)
            else:
                costo = self.get_ultimo_costo(ingrediente.product_id)
                costo_usd = self.get_ultimo_costo_usd(ingrediente.product_id)

            self.env['wizard.formulas.costo'].create({
                'x_secuencia': secuencia,
                'ingr': ingrediente.product_id.id,
                'cod_prov': codprov,
                'cant_tot': ncant_limitante,
                'unidad': ingrediente.product_id.uom_id.name,
                'pct_formula': ingrediente.x_porcentaje,
                'pct_categoria': ingrediente.x_porcentaje_categoria,
                'costo': costo,
                'costo_usd': costo_usd,
                'x_orden': norden
            })

        if ncomponente:
            ncant = ncomponente.cant_tot
            nccomp = ncant_limitante
            ncant_tot = ncant + nccomp
            ncomponente.write({'cant_tot': ncant_tot})
            

    def consolida_formula_costo(self, ingredientes, nqty, secuencia):
        for ingrediente in ingredientes:
            ncant_limitante = nqty * (ingrediente.x_porcentaje / 100)
            # verifica que el ingrediente se fabrique.
            if ingrediente.product_id.bom_count > 0:  # tiene subformula
                bom_pf = self.env['mrp.bom'].search([('product_tmpl_id', '=', ingrediente.product_tmpl_id.id)],
                                                    limit=1).id
                subformula = self.env['mrp.bom.line'].search([('bom_id.id', '=', bom_pf)])
                if subformula:
                    self.consolida_formula_costo(subformula, ncant_limitante, secuencia)
                else:
                    self.crear_ncomponente_costo(ingrediente, secuencia, ncant_limitante)
            else:
                self.crear_ncomponente_costo(ingrediente, secuencia, ncant_limitante)

        return

    # imprime formula
    def imprime_formula_costo(self):

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

                # Determinar qué costo usar según la selección
                if self.tipo_costo == 'autorizado':
                    costo = self.get_costo_autorizado(ingrediente.product_id)
                    costo_usd = self.get_costo_autorizado_usd(ingrediente.product_id)
                else:
                    costo = self.get_ultimo_costo(ingrediente.product_id)
                    costo_usd = self.get_ultimo_costo_usd(ingrediente.product_id)

                vals.append({
                    'componente': ingrediente.product_id.name,
                    'cod_prov': codprov,
                    'cant_comp': ingrediente.product_qty * self.partidas if self.partidas > 0 else self.cantidad * (
                                ingrediente.x_porcentaje / 100),
                    'unidad': ingrediente.product_id.uom_id.name,
                    'pct_formula': ingrediente.x_porcentaje,
                    'pct_categoria': ingrediente.x_porcentaje_categoria,
                    'costo': costo,
                    'costo_usd': costo_usd,
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
                        'costo': self.get_ultimo_costo(ingrediente.product_id),
                        'costo_usd': self.get_ultimo_costo_usd(ingrediente.product_id),
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
            self.consolida_formula_costo(ingredientes,self.cantidad,nsecuencia)

            #ordena la tabla para la impresión
            bom_consolidada = self.env['wizard.formulas.costo'].search([('x_secuencia','=',nsecuencia)])

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
                        'pct_categoria': ingrediente.pct_categoria,
                        'costo': self.get_ultimo_costo(ingrediente.ingr),
                        'costo_usd': self.get_ultimo_costo_usd(ingrediente.ingr),
                    })

        
        # Get the display name of the selected cost type
        cost_type_display = dict(self._fields['tipo_costo'].selection).get(self.tipo_costo)
        
        data = {'ids': self.ids,
                'model': self._name,
                'vals': vals,
                'producto': self.producto.product_tmpl_id.name,
                'codigo': self.producto.product_tmpl_id.default_code,
                'cantidad': self.cantidad,
                'ing_limitante': self.ing_limitante,
                'nombre_il': self.ing_limitante.product_tmpl_id.name if self.ing_limitante else '',
                'cant_limitante': self.cant_limitante,
                'tipo_costo': cost_type_display.lower() if cost_type_display else ''
                }

        # Obtener la acción del reporte
        report_action = self.env.ref('sam_reportes.formulas_costo_reporte').report_action(self, data=data)
        
        # Si es una acción de reporte, configurar para cerrar después de la descarga
        if report_action.get('type') == 'ir.actions.report':
            report_action['close_on_report_download'] = True
        
        # Devolver la acción del reporte de la 
        return report_action