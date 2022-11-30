# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

# muestra la existencia del almacen de origen en los traslados
class StockMove(models.Model):
    _inherit = 'stock.move'

    x_exis_origen = fields.Float(string='Exis Origen')
    x_merma_pct = fields.Float(string='% Merma',
                               digits=(3, 4),
                               compute='calcula_merma')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            nexis = self.env['stock.quant'].search([('product_id.id', '=', self.product_id.id), 
                                                    ('location_id.id', '=', self.location_id.id)],limit=1).quantity

            if nexis > 0:         
                self.x_exis_origen = nexis
            
            self.name = 'Nuevo' # la descripcion es obligatoria


    @api.depends('quantity_done', 'x_exis_origen')
    def calcula_merma(self):
        for reg in self:
            if self.x_exis_origen > 0 and self.quantity_done > 0:
                reg['x_merma_pct'] = 1 - (self.quantity_done / self.x_exis_origen)