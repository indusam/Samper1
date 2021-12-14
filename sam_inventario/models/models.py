# -*- coding: utf-8 -*-

from odoo import models, fields, api

# muestra la existencia del almacen de origen en los traslados
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_exis_origen = fields.Float(string='Exis Origen')

    @api.onchange('move_line_ids_without_package')
    def onchange_move_line_ids_without_package(self):
        if self.move_line_ids_without_package:
            nexis = self.env['stock.quant'].search([('product_id.id', '=', self.move_line_ids_without_package.id), 
                                                    ('location_id.id', '=', self.location_id.id)],limit=1).on_hand         
            self.x_exis_origen = nexis
