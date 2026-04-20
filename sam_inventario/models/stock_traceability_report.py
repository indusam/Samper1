# -*- coding: utf-8 -*-
from odoo import api, models


class StockTraceabilityReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    def _get_inventory_quant_notas(self, move_line):
        if not move_line.move_id.is_inventory:
            return False
        internal_loc = (
            move_line.location_dest_id
            if move_line.location_dest_id.usage == 'internal'
            else move_line.location_id
        )
        quant = self.env['stock.quant'].search([
            ('product_id', '=', move_line.product_id.id),
            ('lot_id', '=', move_line.lot_id.id),
            ('location_id', '=', internal_loc.id),
        ], limit=1)
        return quant.x_notas or False

    def _make_dict_move(self, level, parent_id, move_line, unfoldable=False):
        data = super()._make_dict_move(level, parent_id, move_line, unfoldable)
        for d in data:
            d['x_notas'] = self._get_inventory_quant_notas(move_line)
        return data

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = super()._final_vals_to_lines(final_vals, level)
        for line, val in zip(lines, final_vals):
            line['columns'].append(val.get('x_notas', False))
        return lines
