# -*- coding: utf-8 -*-
# from odoo import http


# class SamVentas(http.Controller):
#     @http.route('/sam_ventas/sam_ventas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sam_ventas/sam_ventas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sam_ventas.listing', {
#             'root': '/sam_ventas/sam_ventas',
#             'objects': http.request.env['sam_ventas.sam_ventas'].search([]),
#         })

#     @http.route('/sam_ventas/sam_ventas/objects/<model("sam_ventas.sam_ventas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sam_ventas.object', {
#             'object': obj
#         })
