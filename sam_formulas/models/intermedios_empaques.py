import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class IntermediosEmpaques(models.Model):
    """
    Modelo para intermedios y empaques en fórmulas.
    """
    _name = 'intermedios.empaques'
    _description = 'Intermedios y empaques'
    
    name = fields.Char(string='Nombre', required=True, readonly=True, copy=False)
    product_id = fields.Many2one('product.product', string='Producto', required=True, ondelete='restrict')
    kgs_unidad = fields.Float(string='Kgs por unidad', required=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals and 'product_id' in vals:
                product = self.env['product.product'].browse(vals['product_id'])
                vals['name'] = product.display_name
        return super().create(vals_list)
        
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.name:
            self.name = self.product_id.display_name
    unidad_pza = fields.Float(string='Unidad por piezas', required=True)
    proceso = fields.Integer(string='Proceso', required=True, default=2)
    lista_materiales = fields.Many2one('mrp.bom', string='Lista de materiales', required=True)

