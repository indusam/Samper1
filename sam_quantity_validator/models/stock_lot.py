from odoo import models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockLot(models.Model):
    _inherit = 'stock.lot'

    def _validate_quantity(self, qty, model_name=False, record_id=False):
        """ Método centralizado para validación """
        if 0 < qty < 0.0001:
            _logger.info(
                f"Ajustando cantidad {qty} a 0 en {model_name or 'stock.lot'} (ID: {record_id or self.id})"
            )
            return 0
        return qty

    @api.model
    def create(self, vals):
        if 'product_qty' in vals:
            vals['product_qty'] = self._validate_quantity(
                vals['product_qty'],
                'stock.lot.create'
            )
        return super().create(vals)

    def write(self, vals):
        if 'product_qty' in vals:
            vals['product_qty'] = self._validate_quantity(
                vals['product_qty'],
                'stock.lot.write',
                self.id
            )
        return super().write(vals)

    def _compute_quantities(self):
        super()._compute_quantities()
        for lot in self:
            if 0 < lot.product_qty < 0.0001:
                lot.product_qty = 0