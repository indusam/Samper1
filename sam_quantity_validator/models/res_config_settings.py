from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    consumption_tolerance = fields.Float(
        string='Tolerancia de Consumo (%)',
        default=0.01,
        help='Tolerancia permitida para diferencias de consumo'
    )

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param(
            'mrp.consumption_tolerance', 
            self.consumption_tolerance
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        tolerance = float(self.env['ir.config_parameter'].get_param(
            'mrp.consumption_tolerance', 0.01
        ))
        res.update(consumption_tolerance=tolerance)
        return res