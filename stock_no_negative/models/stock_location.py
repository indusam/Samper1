# Copyright 2018 Eficent (https://www.eficent.com)
# @author Jordi Ballester <jordi.ballester@eficent.com.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    """Extend stock location to add negative stock control."""

    _inherit = 'stock.location'

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        default=False,
        help="Allow negative stock levels for the stockable products "
             "in this location.",
    )
