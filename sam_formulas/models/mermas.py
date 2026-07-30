# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class MermasBom(models.Model):
    """
    Extiende el modelo mrp.bom para agregar los porcentajes de merma
    por etapa del proceso de producción.
    """
    _inherit = 'mrp.bom'

    x_pct_merma_cocimiento = fields.Float(string='% Merma Cocimiento', digits=(6, 4),
        help="Porcentaje de merma en la etapa de cocimiento")
    x_pct_merma_secado = fields.Float(string='% Merma Secado', digits=(6, 4),
        help="Porcentaje de merma en la etapa de secado")
    x_pct_merma_rebanado = fields.Float(string='% Merma Rebanado', digits=(6, 4),
        help="Porcentaje de merma en la etapa de rebanado")
    x_pct_merma_empaque = fields.Float(string='% Merma Empaque', digits=(6, 4),
        help="Porcentaje de merma en la etapa de empaque")
    x_pct_merma_otros = fields.Float(string='% Merma Otros', digits=(6, 4),
        help="Porcentaje de merma en otras etapas del proceso")
