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

    x_modulo_merma_cocimiento = fields.Integer(string='Módulo Merma Cocimiento',
        help="Módulo de merma en la etapa de cocimiento")
    x_modulo_merma_secado = fields.Integer(string='Módulo Merma Secado',
        help="Módulo de merma en la etapa de secado")
    x_modulo_merma_rebanado = fields.Integer(string='Módulo Merma Rebanado',
        help="Módulo de merma en la etapa de rebanado")
    x_modulo_merma_empaque = fields.Integer(string='Módulo Merma Empaque',
        help="Módulo de merma en la etapa de empaque")
    x_modulo_merma_otros = fields.Integer(string='Módulo Merma Otros',
        help="Módulo de merma en otras etapas del proceso")
