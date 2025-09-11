from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class QuantityValidatorAction(models.Model):
    _name = 'quantity.validator.action'
    _description = 'Quantity Validator Server Actions'

    @api.model
    def _fix_existing_small_quantities(self, model_name, quantity_field='product_qty'):
        """Fix existing records with very small quantities and round to 4 decimal places."""
        try:
            model = self.env[model_name]
            if not model._fields.get(quantity_field):
                return 0, []
                
            # Buscar registros con cantidades que no estén redondeadas a 4 decimales
            # o que sean muy pequeñas (menores a 0.0001 en valor absoluto)
            domain = [
                '|',
                '&',
                (quantity_field, '!=', 0),
                (quantity_field, '!=', False),
                '&',
                (quantity_field, '<=', 0.0001),
                (quantity_field, '>=', -0.0001)
            ]
            
            records = model.search(domain)
            if not records:
                return 0, []
                
            _logger.info("Found %s records with small or unrounded quantities in %s", len(records), model_name)
            
            # Procesar registros uno por uno para manejar posibles errores de validación
            fixed_count = 0
            error_records = []
            
            for record in records:
                try:
                    # Obtener el valor actual y redondearlo a 4 decimales
                    current_value = record[quantity_field] or 0.0
                    rounded_value = round(float(current_value), 4)
                    
                    # Si el valor redondeado es efectivamente 0, usamos 0.0
                    if abs(rounded_value) < 0.0001:
                        rounded_value = 0.0
                    
                    # Si el valor no ha cambiado, no hacemos nada
                    if abs(current_value - rounded_value) < 0.00001:
                        continue
                        
                    # Crear un diccionario con los valores a actualizar
                    vals = {quantity_field: rounded_value}
                    
                    # Para stock.quant, necesitamos manejar el campo in_date
                    if model_name == 'stock.quant' and hasattr(record, 'in_date'):
                        vals['in_date'] = record.in_date or fields.Datetime.now()
                    
                    # Actualizar el registro
                    record.write(vals)
                    fixed_count += 1
                    
                    _logger.debug(
                        "Updated %s(%s): %s -> %s",
                        model_name,
                        record.id,
                        current_value,
                        rounded_value
                    )
                except Exception as e:
                    error_msg = f"{model_name}({record.id}): {str(e)[:100]}"
                    _logger.warning("Could not update %s: %s", model_name, error_msg)
                    error_records.append(error_msg)
                    continue
            
            return fixed_count, error_records
            
        except Exception as e:
            error_msg = str(e)
            _logger.error("Error processing %s: %s", model_name, error_msg)
            return 0, [f"{model_name}: {error_msg}"]

    @api.model
    def validate_quantities(self):
        """Server action to validate and round quantities across all models to 4 decimal places."""
        _logger.info("Starting quantity validation and rounding process")
        
        # Definir modelos y sus campos de cantidad
        models_config = [
            ('stock.quant', 'quantity'),
            ('stock.move', 'product_uom_qty'),
            ('stock.move.line', 'qty_done'),
            ('mrp.production', 'product_qty'),
            ('stock.lot', 'product_qty'),
            ('stock.picking', None)  # Se maneja a través de stock.move
        ]
        
        fixed_counts = {}
        all_errors = []
        
        # Primero, corregir cantidades pequeñas y redondear a 4 decimales
        for model_name, qty_field in models_config:
            if qty_field:
                count, errors = self._fix_existing_small_quantities(model_name, qty_field)
                if count > 0:
                    fixed_counts[model_name] = count
                if errors:
                    all_errors.extend(errors)
        
        # Luego, ejecutar validaciones específicas del modelo
        for model_name, qty_field in models_config:
            try:
                model = self.env[model_name]
                # Si el modelo tiene un método de validación personalizado, ejecutarlo
                if hasattr(model, '_validate_quantities'):
                    _logger.info("Running validation for model: %s", model_name)
                    model._validate_quantities()
                # Si no tiene un método de validación personalizado pero tiene un campo de cantidad,
                # forzamos el redondeo a 4 decimales
                elif qty_field and model._fields.get(qty_field):
                    _logger.info("Ensuring 4-decimal rounding for %s.%s", model_name, qty_field)
                    # Buscar registros que necesiten redondeo
                    domain = [
                        (qty_field, '!=', False),
                        (qty_field, '!=', 0)
                    ]
                    records = model.search(domain, limit=1000)  # Procesar en lotes para evitar problemas de memoria
                    
                    batch_size = 100
                    for i in range(0, len(records), batch_size):
                        batch = records[i:i + batch_size]
                        for record in batch:
                            try:
                                current_value = record[qty_field] or 0.0
                                rounded_value = round(float(current_value), 4)
                                if abs(current_value - rounded_value) > 0.00001:  # Solo actualizar si hay un cambio significativo
                                    record.write({qty_field: rounded_value})
                                    _logger.debug(
                                        "Rounded %s(%s).%s: %s -> %s",
                                        model_name,
                                        record.id,
                                        qty_field,
                                        current_value,
                                        rounded_value
                                    )
                            except Exception as e:
                                error_msg = f"Error rounding {model_name}({record.id}).{qty_field}: {str(e)[:200]}"
                                _logger.error(error_msg)
                                all_errors.append(error_msg)
                                continue
            except Exception as e:
                error_msg = f"Error processing {model_name}: {str(e)[:200]}"
                _logger.error(error_msg)
                all_errors.append(error_msg)
        
        _logger.info("Quantity validation and rounding process completed")
        
        # Mostrar un resumen de los cambios realizados
        result_msg = ["Validación y redondeo de cantidades completado:"]
        if fixed_counts:
            result_msg.append("\nRegistros corregidos:")
            for model, count in fixed_counts.items():
                result_msg.append(f"- {model}: {count} registros")
        
        if all_errors:
            result_msg.append("\nErrores encontrados:")
            for error in all_errors[:10]:  # Mostrar solo los primeros 10 errores
                result_msg.append(f"- {error}")
            if len(all_errors) > 10:
                result_msg.append(f"- ... y {len(all_errors) - 10} errores más")
        
        if not fixed_counts and not all_errors:
            result_msg.append("No se encontraron cantidades que requirieran corrección.")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Validación de cantidades',
                'message': '\n'.join(result_msg),
                'sticky': True,
                'type': 'info',
            }
        }
