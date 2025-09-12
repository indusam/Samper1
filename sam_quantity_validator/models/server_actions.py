# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError

class QuantityValidatorAction(models.Model):
    _name = 'quantity.validator.action'
    _description = 'Quantity Validator Server Actions'
    
    name = fields.Char(string='Name', required=True, default='Quantity Validator')

    @api.model
    def _fix_existing_small_quantities(self, model_name, quantity_field='product_qty'):
        """Fix existing records with very small quantities and round to 6 decimal places."""
        try:
            model = self.env[model_name]
            if not model._fields.get(quantity_field):
                return 0, []
                
            domain = [
                '|',
                '&',
                (quantity_field, '!=', 0),
                (quantity_field, '!=', False),
                '&',
                (quantity_field, '<=', 0.000001),
                (quantity_field, '>=', -0.000001)
            ]
            
            records = model.search(domain)
            if not records:
                return 0, []
                
            fixed_count = 0
            error_records = []

            for record in records:
                try:
                    current_value = record[quantity_field] or 0.0
                    rounded_value = round(float(current_value), 6)
                    
                    if abs(rounded_value) < 0.000001:
                        rounded_value = 0.0
                    
                    if abs(current_value - rounded_value) < 0.000001:
                        continue
                        
                    record.write({quantity_field: rounded_value})
                    fixed_count += 1
                        
                except Exception as e:
                    error_records.append((record.id, str(e)))
            
            return fixed_count, error_records
            
        except Exception as e:
            return 0, [(0, str(e))]

    @api.model
    def validate_quantities(self, model_name, qty_fields=None):
        """Validate and adjust quantities for all records of a model."""
        if not qty_fields:
            qty_fields = ['product_qty', 'quantity_done', 'product_uom_qty']
            
        if not isinstance(qty_fields, (list, tuple)):
            qty_fields = [qty_fields]
            
        try:
            model = self.env[model_name]
            
            for qty_field in qty_fields:
                if not model._fields.get(qty_field):
                    continue
                    
                records = model.search([
                    '|',
                    '&',
                    (qty_field, '!=', 0),
                    (qty_field, '!=', False),
                    '&',
                    (qty_field, '<=', 0.000001),
                    (qty_field, '>=', -0.000001)
                ])
                
                for record in records:
                    try:
                        current_value = record[qty_field] or 0.0
                        rounded_value = round(float(current_value), 6)
                        
                        if abs(rounded_value) < 0.000001:
                            rounded_value = 0.0
                        
                        if abs(current_value - rounded_value) > 0.000001:
                            record.write({qty_field: rounded_value})
                            
                    except Exception:
                        continue
                        
        except Exception:
            return False
            
        return True
