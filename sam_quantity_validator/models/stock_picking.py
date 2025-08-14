from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for move in self.move_ids:
            if 0 < move.quantity_done < 0.0001:
                _logger.info(
                    f"Ajustando cantidad {move.quantity_done} a 0 en transferencia {self.name}"
                )
                move.quantity_done = 0
        return super().button_validate()