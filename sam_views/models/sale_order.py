# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float(digits=(12, 2))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_date_due = fields.Date(
        string='Fecha de vencimiento',
        compute='_compute_x_date_due',
    )

    @api.depends('date_order', 'payment_term_id', 'payment_term_id.line_ids.nb_days')
    def _compute_x_date_due(self):
        for order in self:
            if order.date_order and order.payment_term_id and order.payment_term_id.line_ids:
                max_days = max(order.payment_term_id.line_ids.mapped('nb_days'))
                order.x_date_due = order.date_order.date() + relativedelta(days=max_days)
            else:
                order.x_date_due = order.date_order.date() if order.date_order else False
