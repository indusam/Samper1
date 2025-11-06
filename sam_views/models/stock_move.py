# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    x_caducidad_display = fields.Char(
        string='Fecha(s) de Caducidad',
        compute='_compute_caducidad_display',
        store=False,
        help='Muestra las fechas de caducidad de todos los lotes en las líneas de movimiento'
    )

    @api.depends('move_line_ids', 'move_line_ids.x_studio_caducidad')
    def _compute_caducidad_display(self):
        """
        Calcula y concatena todas las fechas de caducidad de las líneas de movimiento.
        Si hay múltiples lotes con fechas, las muestra separadas por comas.
        """
        for move in self:
            fechas = []
            # Recorrer todas las líneas de movimiento
            for line in move.move_line_ids:
                if line.x_studio_caducidad:
                    # Formatear la fecha para mostrarla de forma legible
                    fecha_str = fields.Date.to_string(line.x_studio_caducidad)
                    if fecha_str not in fechas:  # Evitar duplicados
                        fechas.append(fecha_str)

            # Unir todas las fechas con comas
            move.x_caducidad_display = ', '.join(fechas) if fechas else ''
