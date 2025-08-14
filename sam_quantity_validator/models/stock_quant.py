from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _validate_qty(self, qty):
        if abs(qty) < 0.0001:
            _logger.info(
                f"Ajustando cantidad {qty} a 0 en existencia {self.id}"
            )
            return 0
        return qty

    @api.model
    def create(self, vals):
        if 'quantity' in vals:
            vals['quantity'] = self._validate_qty(vals['quantity'])
        return super().create(vals)

    def write(self, vals):
        if 'quantity' in vals:
            vals['quantity'] = self._validate_qty(vals['quantity'])
        return super().write(vals)