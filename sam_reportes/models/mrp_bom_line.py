# -*- coding: utf-8 -*-
# Herencia de mrp.bom.line para mostrar el nombre del producto en lugar del nombre de la BOM
# VBueno 2025-01-19

from odoo import models, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    def _compute_display_name(self):
        """Override to display product name instead of BOM name"""
        for line in self:
            line.display_name = line.product_id.display_name
