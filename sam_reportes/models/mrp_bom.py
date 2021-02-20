# -*- coding: utf-8 -*-
##############################################################################
#
#    VBueno
#    Copyright (C) 2021-TODAY Industrias Alimenticias SAM SA de CV
#    Author: VBueno
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def get_tipo(self, order):
        tipo = ''
        for line in order.order_line:
            if not tipo:
                tipo = line.product_id.rim_type
        return tipo

    def _get_all_products(self, order):
        prod_obj = self.env['product.product']
        related_products = []

        # To calculate allowed companies
        allowed_company_ids = []
        if self.env.company:
            allowed_company_ids.append(self.env.company.id)
            if self.env.company.closest_organization:
                allowed_company_ids.append(
                    self.env.company.closest_organization.id)
            if self.env.company.CEDIS_organization:
                allowed_company_ids.append(
                    self.env.company.CEDIS_organization.id)
        warehouses = self.env['stock.warehouse'].sudo().search(
            [('company_id', 'in', allowed_company_ids)])

        for line in order.order_line:
            # Calculate total quantity in different warehouse
            qty_available = 0
            for warehouse in warehouses:
                qty = line.product_id.sudo().with_context(to_date=datetime.now(
                ), warehouse=warehouse.id).qty_available
                qty_available += qty

            # Add only main product if product has stock
            # if qty_available > 0:
            related_products.append(line.product_id)
            # Iterate loop through and add sub products based on stock availability
            if line.product_id.rim_type:
                same_rim_type_products = prod_obj.search(
                    [('rim_type', '=', line.product_id.rim_type), ('id', '!=', line.product_id.id)])
                for prod in same_rim_type_products:
                    # Calculate qty for child products
                    qty_available_ch = 0
                    for warehouse in warehouses:
                        qty_ch = prod.sudo().with_context(to_date=datetime.now(
                        ), warehouse=warehouse.id).qty_available
                        qty_available_ch += qty_ch

                    if qty_available_ch > 0 or prod.qty_available > 0:
                        related_products.append(prod)
        return related_products

    def _get_domain_locations(self, company):
        company_id = company.id
        return (
            [('location_id.company_id', '=', company_id),
             ('location_id.usage', 'in', ['internal', 'transit'])],
            ['&',
             ('location_dest_id.company_id', '=', company_id),
             '|',
             ('location_id.company_id', '=', False),
             '&',
             ('location_id.usage', 'in', ['inventory', 'production']),
             ('location_id.company_id', '=', company_id),
             ],
            ['&',
             ('location_id.company_id', '=', company_id),
             '|',
             ('location_dest_id.company_id', '=', False),
             '&',
             ('location_dest_id.usage', 'in', ['inventory', 'production']),
             ('location_dest_id.company_id', '=', company_id),
             ]
        )

    def _compute_quantities(self, product, order, col):
        company = order.company_id
        is_right_comp = False
        if col == 'tnd':
            company = order.company_id
            is_right_comp = True
        elif col == 'prov' and company.closest_organization:
            company = company.closest_organization
            is_right_comp = True
        elif col == 'cedis' and company.CEDIS_organization:
            company = company.CEDIS_organization
            is_right_comp = True
        if is_right_comp:
            domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations(
                company)
            domain_quant = [('product_id', '=', product.id)] + domain_quant_loc
            Quant = self.env['stock.quant']
            quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant.sudo(
            ).read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))
            qty_available = quants_res.get(product.id, [0.0])[0]
            if qty_available > 10:
                qty_available = 10
            return int(qty_available)

    def _get_localizacion(self, product):
        # vbueno: 2308202015:01 obtiene la localizacón de los productos.
        clocalizacion = self.env['x_localizacion_de_productos'].search([('x_Producto.id', '=', product.id),
                                                                        ('x_compania.id', '=', self.env.company.id)
                                                                        ], limit=1).x_name
        return clocalizacion

    def _get_existot(self, product):
        # vbueno: 2701202111:40 obtiene la existencia total (GR) de los productos.
        nexistot = self.env['product.product'].search([('id','=',product.id)],limit=1).qty_available
        nexistot = int(nexistot)
        if nexistot > 10:
            nexistot = 10
        return nexistot

    def _is_promotion_products(self, product):
        promotions = self.env['sale.coupon.program'].search(
            [('program_type', '=', 'promotion_program')])
        prod_obj = self.env['product.product']
        is_promotion = False
        for promotion in promotions:
            if promotion.rule_products_domain:
                domain = safe_eval(promotion.rule_products_domain)
                prod = prod_obj.search(domain).ids
                if prod and product.id in prod:
                    is_promotion = True
        return is_promotion

    def get_attribute_line_ids(self, product):
        attribute_line_ids = {}
        for attribute in product.attribute_line_ids:
            name = attribute.attribute_id.name.lower()
            if name == 'origen':
                values = []
                for value in attribute.value_ids:
                    values.append(value.name)
                attribute_line_ids.update({
                    'origen': ",".join(values)
                })
            elif name == 'cap ca':
                values = []
                for value in attribute.value_ids:
                    values.append(value.name)
                attribute_line_ids.update({
                    'cap ca': ",".join(values)
                })
            elif name == 'indice de carga':
                values = []
                for value in attribute.value_ids:
                    values.append(value.name)
                attribute_line_ids.update({
                    'cap ca': ",".join(values)
                })
            elif name == 'rango de velocidad':
                values = []
                for value in attribute.value_ids:
                    values.append(value.name)
                attribute_line_ids.update({
                    'vel': ",".join(values)
                })
            elif name == 'treadware':
                values = []
                for value in attribute.value_ids:
                    values.append(value.name)
                attribute_line_ids.update({
                    'trea': ",".join(values)
                })
            elif name == 'traccion':
                values = []
                for value in attribute.value_ids:
                    values.append(value.name)
                attribute_line_ids.update({
                    'trac': ",".join(values)
                })
            elif name == 'temperatura':
                values = []
                for value in attribute.value_ids:
                    values.append(value.name)
                attribute_line_ids.update({
                    'temp': ",".join(values)
                })
        return attribute_line_ids

    def _get_display_price(self, product, doc):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = []
        # if no_variant_attributes_price_extra:
        product = product.with_context(
            no_variant_attributes_price_extra=tuple(
                no_variant_attributes_price_extra)
        )

        if doc.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=doc.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=doc.partner_id.id,
                               date=doc.date_order, uom=product.uom_id.id)

        if doc.pricelist_id and not doc.company_id.is_use_avg_cost:
            pricelist_items = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', doc.pricelist_id.id), ('base', '!=', 'list_price')], limit=1)
            if pricelist_items:
                product_context['from_sale_order'] = True
        final_price, rule_id = doc.pricelist_id.with_context(product_context).get_product_price_rule(
            product, self.product_uom_qty or 1.0, doc.partner_id)
        # base_price, currency = self.with_context(product_context)._get_real_price_currency(
        # product, rule_id, self.product_uom_qty, self.product_uom,
        # doc.pricelist_id.id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(
            product, rule_id, 1, product.uom_id, doc.pricelist_id.id)

        if currency != doc.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, doc.pricelist_id.currency_id,
                doc.company_id or self.env.company, doc.date_order or fields.Date.today())

            # negative discounts (= surcharge) are included in the display price

        return max(base_price, final_price)

    def get_price(self, product, doc):
        price_unit = 0.0
        ncantidad = doc.order_line.product_uom_qty
        ninstalacion = doc.x_precio_instalacion

        if not product.uom_id or not product:
            price_unit = 0.0
        if doc.pricelist_id and doc.partner_id:
            product_context = {
                'lang': doc.partner_id.lang,
                'partner': doc.partner_id,
                'date': doc.date_order,
                'pricelist': doc.pricelist_id.id,
                'fiscal_position': self.env.context.get('fiscal_position'),
            }
            if doc.pricelist_id and not doc.company_id.is_use_avg_cost:
                pricelist_items = self.env['product.pricelist.item'].search(
                    [('pricelist_id', '=', doc.pricelist_id.id), ('base', '!=', 'list_price')], limit=1)
                if pricelist_items:
                    product_context['from_sale_order'] = True

            product = product.with_context(product_context)

            price_unit = self._get_display_price(product, doc)

            # vbueno 1409202015:49 Los precios deben ser más IVA
            # vbueno 2111202013:23 Se multiplica el precio por la cantidad de llantas requerida.
            # vbueno 2111202013:27 Se suma al precio de la llanta el de la instalación (x_precio_instalacion)

            compania = self.env.company.id
            n_iva_cia = self.env['account.tax'].search(
                [('company_id', '=', compania),
                 ('name', '=', 'IVA(16%) VENTAS')],
                limit=1).amount

            price_unit = (price_unit + ninstalacion) * (1+(n_iva_cia/100)) * ncantidad

            ctit = 'El precio incluye ' + str(int(ncantidad)) + ' llanta(s)'
            if ninstalacion > 0:
                ctit = ctit + ', instalación, balanceo, válvula'
                if ncantidad == 4:
                    ctit = ctit +' y alineación delantera'

            doc.x_obs1 = ctit

        return price_unit

    def _get_meses_contado(self, doc, product, col):
        price = self.get_price(product, doc)
        if col == 'contado':
            return round(price, 2)
        elif col == 12:
            if doc.company_id.carge_12_mon != 0:
                price += (price * doc.company_id.carge_12_mon) / 100
            return round(price, 2)
        elif col == 6:
            if doc.company_id.carge_6_mon != 0:
                price += (price * doc.company_id.carge_6_mon) / 100
            return round(price, 2)

    # To set product in ascending order by price of the product
    def _get_products_by_order_asc(self, products):
        dict_products = {}
        for product in products:
            dict_products.update({product: self._get_meses_contado(
                self.with_context(lang=self.partner_id.lang), product, 'contado')})
        return sorted(dict_products.items(), key=lambda kv: (kv[1], kv[0]))


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    rim_type = fields.Char("Tipo de llanta", related='product_id.rim_type',
                           store=True)