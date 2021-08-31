# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def cliente_bloqueado(self):
        if self.partner_id.x_studio_cliente_bloqueado:
            raise UserError('CLIENTE BLOQUEADO: ', self.partner_id.x_studio_cliente_bloqueado.x_studio_motivo_de_bloqueo)



