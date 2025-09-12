import logging

_logger = logging.getLogger(__name__)

# Import all models here to make them available when the module is loaded
from . import stock_move
from . import stock_quant
from . import mrp_production
from . import stock_lot
from . import stock_picking
from . import server_actions
_logger.info("\n=== Cargando mrp_consumption_warning_line ===")
from . import mrp_consumption_warning_line
_logger.info("=== mrp_consumption_warning_line cargado correctamente ===\n")
from . import res_config_settings