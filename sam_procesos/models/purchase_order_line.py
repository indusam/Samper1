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
            return
            
        supplier_info = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('partner_id', '=', self.order_id.partner_id.id)
        ], limit=1)
        
        if supplier_info and self.price_unit and self.price_unit != supplier_info.price:
            warning = {
                'title': _('Costo no autorizado'),
                'message': _('El costo del producto %s debe ser %s según la información del proveedor.') % (self.product_id.name, supplier_info.price),
            }
            self.price_unit = supplier_info.price
            return {'warning': warning}