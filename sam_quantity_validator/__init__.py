# -*- coding: utf-8 -*-
"""
Validador de Cantidades para Samper
vbueno 0610202518:13
Actualizado para Odoo v18
"""

from . import models
from . import hooks

def post_init_hook(cr, registry):
    """
    Post initialization hook to be called after module installation/update.

    Args:
        cr: Database cursor
        registry: Odoo registry object
    """
    hooks.post_init_hook(cr, registry)
