# ?? 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Stock Disallow Negative',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'license': 'AGPL-3',
    'summary': 'Disallow negative stock levels by default',
    'description': """
Stock Disallow Negative
========================
By default, Odoo allows negative stock. This module allows you to disallow
negative stock levels by default, with granular control:
- By product (in product form)
- By product category (in category configuration)
- By location (in location configuration)
    """,
    'author': 'Akretion, Odoo Community Association (OCA), Samper',
    'website': 'https://www.samper.mx',
    'depends': ['stock'],
    'data': [
        'views/product_product_views.xml',
        'views/stock_location_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
