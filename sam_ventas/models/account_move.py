# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_tax', 'amount_total', 'partner_id')
    def calcula_comision(self):
        nimporte = self.amount_total - self.amount_tax
        n_pct_comision = self.env['res.partner'].search([('id', '=', self.partner_id.id)], limit=1).x_pct_comision
        self.x_comision = nimporte * (n_pct_comision / 100)

    x_comision = fields.Float(string='Comisión',
                             required=False,
                             compute='calcula_comision')
    x_vendedor = fields.Many2one("res.partner", string="Vendedor")
