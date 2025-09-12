from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError

class ResConfigSettings(models.TransientModel):
    """Extend res.config.settings to add manufacturing consumption tolerance configuration."""
    _inherit = 'res.config.settings'

    consumption_tolerance = fields.Float(
        string='Tolerancia de Consumo (%)',
        default=0.01,
        digits=(16, 4),  # Store with 4 decimal places
        help='Tolerancia permitida para diferencias de consumo (ej. 0.01 = 1%)',
        config_parameter='mrp.consumption_tolerance',
    )

    @api.constrains('consumption_tolerance')
    def _check_consumption_tolerance(self):
        """Ensure tolerance is a valid percentage between 0 and 1."""
        for record in self:
            if not (0 <= record.consumption_tolerance <= 1):
                raise ValidationError(_(
                    'La tolerancia debe ser un valor entre 0 y 1 (0% a 100%)'
                ))

    def set_values(self):
        """Save the configuration values."""
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_('No tiene permisos para modificar esta configuración.'))
            
        # Validate before saving
        self._check_consumption_tolerance()
        
        # Call parent to save the config_parameter
        res = super().set_values()
        
        # Clear cache to ensure new values are immediately available
        self.env['ir.config_parameter'].clear_caches()
        return res

    @api.model
    def get_values(self):
        """Get the current configuration values."""
        res = super().get_values()
        
        # Get the parameter with proper type conversion and default
        ICP = self.env['ir.config_parameter'].sudo()
        tolerance = float(ICP.get_param('mrp.consumption_tolerance', '0.01'))
        
        # Ensure the value is within valid range
        tolerance = max(0.0, min(1.0, tolerance))
        
        res.update(consumption_tolerance=tolerance)
        return res
        
    def get_consumption_tolerance(self):
        """Helper method to get the current tolerance value."""
        return float(self.env['ir.config_parameter'].sudo().get_param(
            'mrp.consumption_tolerance', '0.01'
        ))