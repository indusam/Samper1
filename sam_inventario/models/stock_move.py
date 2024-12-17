# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

# muestra la existencia del almacen de origen en los traslados
from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    x_exis_origen = fields.Float(string='Exis Origen')
    x_merma_pct = fields.Float(string='% Merma', digits=(3, 2))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.location_id:
            stock_quant = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id', '=', self.location_id.id),
                ('quantity','>',0)
            ], limit=1)

            self.x_exis_origen = stock_quant.quantity if stock_quant else 0.0

            # La descripción es obligatoria, se establece un valor por defecto
            self.name = self.name or 'Nuevo'
