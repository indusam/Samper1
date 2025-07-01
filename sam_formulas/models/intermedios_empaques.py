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
    product_uom_name = fields.Char(string='Unidad', compute='_compute_product_uom_name', readonly=True, store=True)
    kgs_unidad = fields.Float(string='Kgs por unidad', required=True)
    
    @api.depends('product_id')
    def _compute_product_uom_name(self):
        for record in self:
            record.product_uom_name = record.product_id.uom_id.name if record.product_id else ''
    
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
            
    @api.onchange('kgs_unidad')
    def _onchange_kgs_unidad(self):
        if self.kgs_unidad and self.kgs_unidad != 0:
            self.unidad_pza = 0
            
    @api.onchange('unidad_pza')
    def _onchange_unidad_pza(self):
        if self.unidad_pza and self.unidad_pza != 0:
            self.kgs_unidad = 0
            
    @api.constrains('kgs_unidad', 'unidad_pza')
    def _check_required_fields(self):
        for record in self:
            if record.kgs_unidad == 0 and record.unidad_pza == 0:
                raise ValidationError(_("Debe especificar al menos Kgs/Unidad o Unidad/Pieza"))
            if record.kgs_unidad != 0 and record.unidad_pza != 0:
                raise ValidationError(_("Solo puede especificar Kgs/Unidad o Unidad/Pieza, no ambos"))
                
    unidad_pza = fields.Float(string='Unidad por piezas', default=0)
    proceso = fields.Integer(string='Proceso', required=True, default=2)
    lista_materiales = fields.Many2one('mrp.bom', string='Lista de materiales', required=True)

