from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id', 'price_unit')
    def _onchange_product_id_validate_cost(self):
        """
        Valida que el costo del producto coincida con el registrado en product.supplierinfo
        cuando se cambia el producto o el precio unitario
        """
        if not self.product_id or not self.order_id.partner_id:
            return {'warning': {}}
            
        supplier_info = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('partner_id', '=', self.order_id.partner_id.id)
        ], limit=1)
        
        warning = {}
        
        if not supplier_info:
            # Si el producto no está en la lista de precios, forzamos al usuario a tomar una decisión
            # estableciendo el precio unitario como 0
            warning = {
                'title': _('Producto no encontrado en lista de precios'),
                'message': _('El producto %s no se encuentra en la lista de precios del proveedor %s. Por favor, actualice la lista de precios.') % (self.product_id.name, self.order_id.partner_id.name),
                'type': 'notification',
                'sticky': True
            }
            self.price_unit = 0
            return {'warning': warning}
        
        if supplier_info and (not self.price_unit or self.price_unit != supplier_info.price):
            warning = {
                'title': _('Costo no autorizado'),
                'message': _('El costo del producto %s debe ser %s según la información del proveedor %s.') % (self.product_id.name, supplier_info.price, self.order_id.partner_id.name),
            }
            self.price_unit = supplier_info.price
            
        return {'warning': warning} if warning else {}