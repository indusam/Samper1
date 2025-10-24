# Copyright 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    """Extend product category to add negative stock control."""

    _inherit = 'product.category'

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        default=False,
        help="Allow negative stock levels for the stockable products "
             "attached to this category. The option doesn't apply to products "
             "attached to sub-categories of this category.",
    )


class ProductTemplate(models.Model):
    """Extend product template to add negative stock control."""

    _inherit = "product.template"

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        default=False,
        help="If this option is not active on this product nor on its "
             "product category and that this product is a stockable product, "
             "then the validation of the related stock moves will be blocked if "
             "the stock level becomes negative with the stock move.",
    )
