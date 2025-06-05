from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def validate_product_cost(self):
        """
        Valida que el costo del producto coincida con el registrado en product.supplierinfo
        """
        for line in self:
            if not line.product_id or not line.order_id.partner_id:
                continue
                
            supplier_info = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('name', '=', line.order_id.partner_id.id)
            ], limit=1)
            
            if supplier_info and supplier_info.price != line.price_unit:
                raise ValidationError(_("Costo no autorizado. El costo debe ser %s según la información del proveedor." % supplier_info.price))
        return True
    
    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        res.validate_product_cost()
        return res
    
    def write(self, vals):
        res = super(PurchaseOrderLine, self).write(vals)
        if 'price_unit' in vals:
            self.validate_product_cost()
        return res