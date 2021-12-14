# -*- coding: utf-8 -*-

from odoo import models, fields, api

# muestra la existencia del almacen de origen en los traslados
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_exis_origen = fields.Float(string='Exis')

    @api.onchange('product_id')
    def onchange_x_exis_origen(self):
        if self.product_id:
            nexis = self.env['stock.quant'].search([('product_id.id', '=', self.product_id.id), 
                                                    ('location_id.id', '=', self.location_id.id)],limit=1).on_hand         
            self.x_exis_origen = nexis
