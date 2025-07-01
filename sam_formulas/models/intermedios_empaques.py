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
    
    name = fields.Char(string='Nombre', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    kgs_unidad = fields.Float(string='Kgs por unidad', required=True)
    unidad_pza = fields.Float(string='Unidad por piezas', required=True)
    proceso = fields.Integer(string='Proceso', required=True, default=2)
    lista_materiales = fields.Many2one('mrp.bom', string='Lista de materiales', required=True)

