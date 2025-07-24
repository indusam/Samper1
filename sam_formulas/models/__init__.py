# -*- coding: utf-8 -*-
# Importar los modelos individuales
# vbueno 2606202510:44

# Importar los modelos en el orden correcto
# Note: We don't import 'models' here as it would cause circular imports
from . import intermedios_empaques
from . import mrp_bom

# This ensures all models are properly registered
from .models import *
