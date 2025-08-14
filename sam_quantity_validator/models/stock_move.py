from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _validate_qty(self, qty, field_name=False):
        if 0 < qty < 0.0001:
            _logger.info(
                f"Ajustando {field_name or 'quantity'} de {qty} a 0 en movimiento {self.id}"
            )
            return 0
        return qty

    @api.model
    def create(self, vals):
        qty_fields = ['product_uom_qty', 'quantity_done', 'reserved_availability']
        for field in qty_fields:
            if field in vals:
                vals[field] = self._validate_qty(vals[field], field)
        return super().create(vals)

    def write(self, vals):
        qty_fields = ['product_uom_qty', 'quantity_done', 'reserved_availability']
        for field in qty_fields:
            if field in vals:
                vals[field] = self._validate_qty(vals[field], field)
        return super().write(vals)

    def _action_assign(self):
        """ Validación al reservar stock """
        for move in self:
            if 0 < move.product_uom_qty < 0.0001:
                move.product_uom_qty = 0
        return super()._action_assign()