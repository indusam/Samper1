# Copyright 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import config, float_compare


class StockQuant(models.Model):
    """Extend stock quant to add negative stock validation."""

    _inherit = 'stock.quant'

    @api.constrains('product_id', 'quantity')
    def check_negative_qty(self):
        """
        Validate that stock quantity doesn't become negative.

        Checks if negative stock is allowed based on:
        - Product configuration
        - Product category configuration
        - Location configuration

        Raises ValidationError if negative stock is not allowed.
        """
        # Use fixed precision for product quantities (standard in Odoo 18)
        # Previously used deprecated decimal.precision model (removed in v16+)
        precision = 4
        check_negative_qty = (
            (config['test_enable'] and
             self.env.context.get('test_stock_no_negative')) or
            not config['test_enable']
        )
        if not check_negative_qty:
            return

        for quant in self:
            # Check if negative stock is disallowed by product or category
            disallowed_by_product = (
                not quant.product_id.allow_negative_stock and
                not quant.product_id.categ_id.allow_negative_stock
            )
            # Check if negative stock is disallowed by location
            disallowed_by_location = not quant.location_id.allow_negative_stock

            # Validate conditions for blocking negative stock
            if (
                float_compare(
                    quant.quantity, 0, precision_digits=precision
                ) == -1 and
                quant.product_id.type == 'product' and
                quant.location_id.usage in ['internal', 'transit'] and
                disallowed_by_product and
                disallowed_by_location
            ):
                msg_add = ''
                if quant.lot_id:
                    msg_add = _(" lot '%s'") % quant.lot_id.display_name
                raise ValidationError(
                    _(
                        "You cannot validate this stock operation because the "
                        "stock level of the product '%s'%s would become negative "
                        "(%s) on the stock location '%s' and negative stock is "
                        "not allowed for this product and/or location."
                    ) % (
                        quant.product_id.name,
                        msg_add,
                        quant.quantity,
                        quant.location_id.complete_name,
                    )
                )
