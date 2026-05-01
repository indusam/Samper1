# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WizardEditarNotasMove(models.TransientModel):
    _name = 'wizard.editar.notas.move'
    _description = 'Editar Notas del Movimiento'

    move_id = fields.Many2one('stock.move', required=True)
    x_notas = fields.Char(string='Notas')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_id = self.env.context.get('active_id')
        if move_id:
            move = self.env['stock.move'].browse(move_id)
            res['move_id'] = move_id
            res['x_notas'] = move.x_notas
        return res

    def action_guardar(self):
        self.ensure_one()
        self.move_id.sudo().write({'x_notas': self.x_notas})
        return {'type': 'ir.actions.act_window_close'}
