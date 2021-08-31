# -*- coding: utf-8 -*-

from odoo import models, fields, api, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('partner_id')
    def cliente_bloqueado(self):
        if self.partner_id.x_studio_cliente_bloqueado:
            raise UserError('¡CLIENTE BLOQUEADO!')