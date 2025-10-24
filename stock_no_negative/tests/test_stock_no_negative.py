# Copyright 2015-2016 Akretion (http://www.akretion.com) - Alexis de Lattre
# Copyright 2016 Eficent (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services (<http://www.serpentcs.com>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockNoNegative(TransactionCase):
    """Test cases for stock_no_negative module."""

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        """Set up test data for all tests."""
        super().setUpClass()
        cls.product_model = cls.env['product.product']
        cls.product_ctg_model = cls.env['product.category']
        cls.picking_type_id = cls.env.ref('stock.picking_type_out')
        cls.location_id = cls.env.ref('stock.stock_location_stock')
        cls.location_dest_id = cls.env.ref('stock.stock_location_customers')

    def setUp(self):
        """Set up test data for each individual test."""
        super().setUp()
        # Create product category
        self.product_ctg = self._create_product_category()
        # Create a Product
        self.product = self._create_product('test_product1')
        self._create_picking()

    def _create_product_category(self):
        """Create test product category with negative stock disabled."""
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'allow_negative_stock': False,
        })
        return product_ctg

    def _create_product(self, name):
        """Create test product with negative stock disabled."""
        product = self.product_model.create({
            'name': name,
            'categ_id': self.product_ctg.id,
            'type': 'product',
            'allow_negative_stock': False,
        })
        return product

    def _create_picking(self):
        """Create test stock picking with 100 units."""
        self.stock_picking = self.env['stock.picking'].with_context(
            test_stock_no_negative=True,
        ).create({
            'picking_type_id': self.picking_type_id.id,
            'move_type': 'direct',
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
        })

        self.stock_move = self.env['stock.move'].create({
            'name': 'Test Move',
            'product_id': self.product.id,
            'product_uom_qty': 100.0,
            'product_uom': self.product.uom_id.id,
            'picking_id': self.stock_picking.id,
            'state': 'draft',
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'quantity_done': 100.0,
        })

    def test_check_constrains(self):
        """
        Test that constraint is raised when validating a stock operation.

        Validates that a ValidationError is raised when trying to validate
        a stock operation that would make the stock level negative when
        negative stock is not allowed.
        """
        self.stock_picking.action_confirm()
        with self.assertRaises(ValidationError):
            self.stock_picking.button_validate()

    def test_true_allow_negative_stock_product(self):
        """
        Test that negative stock is allowed when enabled on product.

        Validates that when allow_negative_stock is enabled on the product,
        the stock operation can be validated even if it results in negative
        stock levels.
        """
        self.product.allow_negative_stock = True
        self.stock_picking.action_confirm()
        self.stock_picking.button_validate()
        quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product.id),
            ('location_id', '=', self.location_id.id),
        ])
        self.assertEqual(quant.quantity, -100)

    def test_true_allow_negative_stock_location(self):
        """
        Test that negative stock is allowed when enabled on location.

        Validates that when allow_negative_stock is enabled on the location,
        the stock operation can be validated even if it results in negative
        stock levels, regardless of product settings.
        """
        self.product.allow_negative_stock = False
        self.location_id.allow_negative_stock = True
        self.stock_picking.action_confirm()
        self.stock_picking.button_validate()
        quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product.id),
            ('location_id', '=', self.location_id.id),
        ])
        self.assertEqual(quant.quantity, -100)
