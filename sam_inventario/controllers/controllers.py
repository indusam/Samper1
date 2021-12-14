# -*- coding: utf-8 -*-
# from odoo import http


# class SamFormulas(http.Controller):
#     @http.route('/sam_formulas/sam_formulas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sam_formulas/sam_formulas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sam_formulas.listing', {
#             'root': '/sam_formulas/sam_formulas',
#             'objects': http.request.env['sam_formulas.sam_formulas'].search([]),
#         })

#     @http.route('/sam_formulas/sam_formulas/objects/<model("sam_formulas.sam_formulas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sam_formulas.object', {
#             'object': obj
#         })
