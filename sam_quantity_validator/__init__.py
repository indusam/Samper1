from . import models

def pre_init_hook(cr):
    """Pre-init hook for module installation."""
    pass

def post_init_hook(cr, registry):
    """Post-init hook for module installation.
    
    Args:
        cr: database cursor
        registry: Odoo model registry
    """
    pass
# The actual imports will be done when the registry is built