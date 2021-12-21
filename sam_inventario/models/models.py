# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

# muestra la existencia del almacen de origen en los traslados
class StockMove(models.Model):
    _inherit = 'stock.move'

    x_exis_origen = fields.Float(string='Exis Origen')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            nexis = self.env['stock.quant'].search([('product_id.id', '=', self.product_id.id), 
                                                    ('location_id.id', '=', self.location_id.id)],limit=1).quantity

            if nexis > 0:         
                self.x_exis_origen = nexis
            
            self.name = 'Nuevo' # la descripcion es obligatoria
