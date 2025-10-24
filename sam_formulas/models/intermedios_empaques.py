# -*- coding: utf-8 -*-
"""
Modelo de Intermedios y Empaques para Samper - Actualizado para Odoo v18
"""

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class IntermediosEmpaques(models.Model):
    """
    Modelo para intermedios y empaques en fórmulas.
    Actualizado para Odoo v18.
    """
    _name = 'intermedios.empaques'
    _description = 'Intermedios y empaques en fórmulas'
    
    # Field definitions
    name = fields.Char(
        string='Nombre',
        required=True,
        readonly=True,
        copy=False
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        ondelete='restrict',
        domain="['|', ('categ_id.name', 'ilike', 'EMPAQUE'), ('categ_id.name', 'ilike', 'INTERMEDIOS')]"
    )
    product_uom_name = fields.Char(
        string='Unidad',
        compute='_compute_product_uom_name',
        readonly=True,
        store=True
    )
    kgs_unidad = fields.Float(
        string='Kgs por unidad',
        default=0.0
    )
    unidad_pza = fields.Float(
        string='Unidad por piezas',
        default=0.0
    )
    proceso = fields.Integer(
        string='Proceso',
        required=True,
        default=2
    )
    lista_materiales = fields.Many2one(
        'mrp.bom',
        string='Lista de materiales',
        required=True
    )
    
    # Computed methods
    @api.depends('product_id')
    def _compute_product_uom_name(self):
        """Compute the UoM name based on the selected product."""
        for record in self:
            record.product_uom_name = record.product_id.uom_id.name if record.product_id else ''
    
    # CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set default values."""
        for vals in vals_list:
            if 'product_id' in vals:
                product = self.env['product.product'].browse(vals['product_id'])
                if 'name' not in vals:
                    vals['name'] = product.display_name
                # Ensure computed field is updated
                vals['product_uom_name'] = product.uom_id.name if product.uom_id else ''
        return super().create(vals_list)
    
    # Onchange methods
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Update name when product changes."""
        if self.product_id and not self.name:
            self.name = self.product_id.display_name
    
    @api.onchange('kgs_unidad')
    def _onchange_kgs_unidad(self):
        """Reset unidad_pza when kgs_unidad changes."""
        if self.kgs_unidad and self.kgs_unidad != 0:
            self.unidad_pza = 0.0
    
    @api.onchange('unidad_pza')
    def _onchange_unidad_pza(self):
        """Reset kgs_unidad when unidad_pza changes."""
        if self.unidad_pza and self.unidad_pza != 0:
            self.kgs_unidad = 0.0
    
    # Constraint methods
    @api.constrains('kgs_unidad', 'unidad_pza')
    def _check_required_fields(self):
        """Ensure at least one of kgs_unidad or unidad_pza is set, but not both."""
        for record in self:
            if record.kgs_unidad == 0 and record.unidad_pza == 0:
                raise ValidationError(_("Debe especificar al menos Kgs/Unidad o Unidad/Pieza"))
            if record.kgs_unidad != 0 and record.unidad_pza != 0:
                raise ValidationError(_("Solo puede especificar Kgs/Unidad o Unidad/Pieza, no ambos"))

