def pre_init_hook(cr):
    """Pre-init hook to avoid circular imports."""
    pass

def post_init_hook(cr, registry):
    """Post-init hook to import models after registry is ready."""
    from . import models

# This is the standard Odoo way to import models
# The actual imports will be done when the registry is built