from odoo import models, fields

class MrpConsumptionWarningLine(models.TransientModel):
    """Extiende mrp.consumption.warning.line para modificar la precisión de los campos flotantes."""
    _inherit = 'mrp.consumption.warning.line'
    _name = 'mrp.consumption.warning.line'  

    product_consumed_qty_uom = fields.Float(digits=(16, 6))
    product_expected_qty_uom = fields.Float(digits=(16, 6))
