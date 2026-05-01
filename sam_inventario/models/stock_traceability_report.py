# -*- coding: utf-8 -*-
from odoo import api, models


class StockTraceabilityReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    def _make_dict_move(self, level, parent_id, move_line, unfoldable=False):
        data = super()._make_dict_move(level, parent_id, move_line, unfoldable)
        for d in data:
            d['x_notas'] = move_line.move_id.x_notas or False
        return data

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = super()._final_vals_to_lines(final_vals, level)
        for line, val in zip(lines, final_vals):
            line['columns'].insert(1, val.get('x_notas', False))
        return lines
