# -*- coding: utf-8 -*-

# formulas.py
# Impresión de la fórmula de un producto..
# VBueno 1707202511:00 
# v16
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
    product_tmpl = fields.Many2one('product.template', string="Producto")
    producto = fields.Many2one('mrp.bom', string="Lista de Materiales", domain="[('product_tmpl_id', '=', product_tmpl)]")
    cantidad = fields.Float(string="Cantidad")
    pct_merma = fields.Float(string="% Merma", digits=(6, 5))
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

    def get_codprov(self, producto_id):
        """Obtiene el código de proveedor para un producto o plantilla de producto"""
        ProductProduct = self.env['product.product']
        ProductTemplate = self.env['product.template']
        
        # Verificar si el ID es de un producto o plantilla
        if ProductProduct.search_count([('id', '=', producto_id)]) > 0:
            # Es un ID de producto
            product = ProductProduct.browse(producto_id)
            supplier_info = self.env['product.supplierinfo'].search([
                '|',
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                '&',
                    ('product_id', '=', product.id),
                    ('product_tmpl_id', '=', product.product_tmpl_id.id)
            ], order='sequence, id', limit=1)
        else:
            # Asumir que es un ID de plantilla de producto
            supplier_info = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', producto_id),
                ('product_id', '=', False)
            ], order='sequence, id', limit=1)
            
        return supplier_info.product_name if supplier_info and supplier_info.product_name else ''

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
                        'costo': self.get_costo_autorizado(ingrediente.product_id) if self.tipo_costo == 'autorizado' else self.get_ultimo_costo(ingrediente.product_id),
                        'costo_usd': self.get_costo_autorizado_usd(ingrediente.product_id) if self.tipo_costo == 'autorizado' else self.get_ultimo_costo_usd(ingrediente.product_id),
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
                        'costo': self.get_costo_autorizado(ingrediente.ingr) if self.tipo_costo == 'autorizado' else self.get_ultimo_costo(ingrediente.ingr),
                        'costo_usd': self.get_costo_autorizado_usd(ingrediente.ingr) if self.tipo_costo == 'autorizado' else self.get_ultimo_costo_usd(ingrediente.ingr),
                    })

        
        # Get the display name of the selected cost type
        cost_type_display = dict(self._fields['tipo_costo'].selection).get(self.tipo_costo)

        tipo_cambio = self.env.company.x_studio_tipo_de_cambio or 1.0

        # Totales de la Tabla 1 (fórmula)
        total_cost_formula = sum(v['costo'] * v['cant_comp'] for v in vals)
        tot_gral_formula = sum(v['cant_comp'] for v in vals)
        masa_formula = self.cantidad if self.cantidad > 0 else tot_gral_formula

        # Merma por módulo, definida en la lista de materiales (models/mermas.py).
        # Módulo 1 = masa del producto (fórmula, sin ítems propios).
        # Módulos 2-4 usan el mismo layout de Intermedios (ítems + merma).
        NOMBRE_MODULO = {2: 'Intermedios', 3: 'Empaques', 4: 'Empaques de rebanados'}
        MODULOS_IMPLEMENTADOS = [1, 2, 3, 4]

        merma_por_modulo = {}
        if self.producto:
            etapas_merma = [
                ('Cocimiento', self.producto.x_pct_merma_cocimiento, self.producto.x_modulo_merma_cocimiento),
                ('Secado', self.producto.x_pct_merma_secado, self.producto.x_modulo_merma_secado),
                ('Rebanado', self.producto.x_pct_merma_rebanado, self.producto.x_modulo_merma_rebanado),
                ('Empaque', self.producto.x_pct_merma_empaque, self.producto.x_modulo_merma_empaque),
                ('Otros', self.producto.x_pct_merma_otros, self.producto.x_modulo_merma_otros),
            ]
            merma_por_modulo = {
                modulo: {'nombre': nombre, 'pct': pct}
                for nombre, pct, modulo in etapas_merma if modulo
            }

        # Intermedios y empaques agrupados por módulo (sólo los módulos con layout implementado)
        intermedios_por_modulo = {}
        if self.producto and self.producto.intermedios_empaques_ids:
            records = self.env['intermedios.empaques'].search([
                ('lista_materiales', '=', self.producto.id)
            ])
            for rec in records:
                if rec.proceso not in NOMBRE_MODULO:
                    continue

                if self.tipo_costo == 'autorizado':
                    costo_usd = self.get_costo_autorizado_usd(rec.product_id)
                else:
                    costo_usd = self.get_ultimo_costo_usd(rec.product_id)

                item_divisor = rec.kgs_unidad if rec.kgs_unidad > 0 else rec.unidad_pza
                item_cant = masa_formula / item_divisor if item_divisor > 0 else 0.0
                item_ratio = (rec.product_id.uom_po_id.ratio if rec.product_id.uom_po_id else 1.0) or 1.0
                item_costo_usd_unit = costo_usd / item_ratio
                item_mxn = item_costo_usd_unit * tipo_cambio
                item_import = item_mxn * item_cant

                intermedios_por_modulo.setdefault(rec.proceso, []).append({
                    'name': rec.product_id.name,
                    'kgs_unidad': rec.kgs_unidad,
                    'unidad_pza': rec.unidad_pza,
                    'product_uom_name': (rec.product_id.uom_po_id.x_studio_unidad or rec.product_id.uom_po_id.name) if rec.product_id.uom_po_id else (rec.product_id.uom_id.name if rec.product_id else ''),
                    'item_cant': item_cant,
                    'item_costo_usd_unit': item_costo_usd_unit,
                    'item_mxn': item_mxn,
                    'item_import': item_import,
                })

        # Cadena módulo por módulo: cada módulo reduce la masa vigente si tiene
        # merma asociada, y esa masa reducida es la base del siguiente módulo.
        bloques_modulo = []
        masa_actual = masa_formula
        total_acumulado = total_cost_formula

        for modulo in MODULOS_IMPLEMENTADOS:
            items = intermedios_por_modulo.get(modulo, [])
            merma_info = merma_por_modulo.get(modulo)

            total_bloque = sum(it['item_import'] for it in items)
            total_acumulado += total_bloque

            bloque = {
                'modulo': modulo,
                'nombre': NOMBRE_MODULO.get(modulo),
                'items': items,
                'total_bloque': total_bloque,
                'masa_base': masa_actual,
                'costo_kg_bloque': (total_bloque / masa_actual) if items and masa_actual > 0 else 0.0,
                'pct_costo_bloque': 0.0,
                'merma': None,
            }

            if merma_info and merma_info['pct'] > 0:
                masa_despues = masa_actual * (1.0 - merma_info['pct'] / 100.0)
                bloque['merma'] = {
                    'nombre': merma_info['nombre'],
                    'pct': merma_info['pct'],
                    'masa_despues': masa_despues,
                    'total_acumulado': total_acumulado,
                    'costo_kg_post_merma': (total_acumulado / masa_despues) if masa_despues > 0 else 0.0,
                }
                masa_actual = masa_despues

            if items or bloque['merma']:
                bloques_modulo.append(bloque)

        cantidad_despues_merma = masa_actual
        combined_total = total_acumulado

        for bloque in bloques_modulo:
            for it in bloque['items']:
                it['pct_costo'] = (it['item_import'] / combined_total) * 100 if combined_total > 0 else 0.0
                it['costo_kg_masa_formula'] = it['item_import'] / masa_formula if masa_formula > 0 else 0.0
            bloque['pct_costo_bloque'] = (bloque['total_bloque'] / combined_total) * 100 if bloque['items'] and combined_total > 0 else 0.0
            if bloque['merma']:
                bloque['merma']['pct_costo'] = (bloque['merma']['total_acumulado'] / combined_total) * 100 if combined_total > 0 else 0.0

        base_final = cantidad_despues_merma if cantidad_despues_merma > 0 else masa_formula
        costo_final_kg = combined_total / base_final if base_final > 0 else 0.0

        data = {
            'ids': self.ids,
            'model': self._name,
            'vals': vals,
            'producto': self.producto.product_tmpl_id.name,
            'codigo': self.producto.product_tmpl_id.default_code,
            'cantidad': self.cantidad,
            'masa_formula': masa_formula,
            'pct_merma': self.pct_merma,
            'cantidad_despues_merma': cantidad_despues_merma,
            'ing_limitante': self.ing_limitante,
            'nombre_il': self.ing_limitante.product_tmpl_id.name if self.ing_limitante else '',
            'cant_limitante': self.cant_limitante,
            'tipo_costo': cost_type_display.lower() if cost_type_display else '',
            'total_cost_formula': total_cost_formula,
            'combined_total': combined_total,
            'costo_final_kg': costo_final_kg,
            'bloques_modulo': bloques_modulo,
            'bom_code': self.producto.code,
        }

        # Obtener la acción del reporte
        report_action = self.env.ref('sam_reportes.formulas_costo_reporte').report_action(self, data=data)
        
        # Si es una acción de reporte, configurar para cerrar después de la descarga
        if report_action.get('type') == 'ir.actions.report':
            report_action['close_on_report_download'] = True
        
        # Devolver la acción del reporte de la 
        return report_action