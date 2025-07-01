# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    intermedios_empaques_ids = fields.One2many(
        'intermedios.empaques', 
        'lista_materiales', 
        string='Intermedios y Empaques',
        help='Lista de intermedios y empaques asociados a esta lista de materiales')
    
    intermedios_empaques_count = fields.Integer(
        'Número de Intermedios/Empaques', 
        compute='_compute_intermedios_empaques_count',
        store=True)
    
    @api.depends('intermedios_empaques_ids')
    def _compute_intermedios_empaques_count(self):
        for bom in self:
            bom.intermedios_empaques_count = len(bom.intermedios_empaques_ids)
