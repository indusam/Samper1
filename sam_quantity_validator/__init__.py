from . import models
from . import hooks

def post_init_hook(cr, registry):
    """Post initialization hook to be called after module installation/update"""
    hooks.post_init_hook(cr, registry)
