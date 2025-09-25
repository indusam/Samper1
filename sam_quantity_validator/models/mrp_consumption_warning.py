from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MrpConsumptionWarning(models.TransientModel):
    _inherit = 'mrp.consumption.warning'
    
    def action_confirm(self):
        """Override to skip the warning if all lines are within tolerance."""
        Config = self.env['res.config.settings']
        tolerance = Config.get_consumption_tolerance()
        
        # Check if all lines are within tolerance
        all_within_tolerance = True
        for line in self.mrp_consumption_warning_line_ids:
            consumed = line.product_consumed_qty_uom or 0.0
            expected = line.product_expected_qty_uom or 0.0
            diff = abs(consumed - expected)
            allowed_diff = expected * tolerance
            
            if diff > allowed_diff:
                all_within_tolerance = False
                break
        
        # If all lines are within tolerance, skip the warning
        if all_within_tolerance:
            _logger.info("All consumption differences are within tolerance (%.2f%%), skipping warning", tolerance * 100)
            # Get the production order from the first line
            if self.mrp_consumption_warning_line_ids and len(self.mrp_consumption_warning_line_ids) > 0:
                production = self.mrp_consumption_warning_line_ids[0].production_id
                if production:
                    return production.with_context(skip_consumption=True).button_mark_done()
        
        # Otherwise, show the warning as usual
        return super().action_confirm()
