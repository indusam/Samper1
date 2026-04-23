# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_GIBBERISH_PATTERNS = [
    'asdf', 'qwer', 'zxcv', 'hjkl', 'uiop', 'bnm',
    'aaaa', 'bbbb', 'cccc', 'dddd', 'ffff', 'gggg',
    'hhhh', 'jjjj', 'kkkk', 'llll', 'ssss', 'tttt',
    '1234', '5678', 'abcd', 'wxyz',
]
_VOWELS = set('aeiouáéíóúüAEIOUÁÉÍÓÚÜ')


def _validar_texto_significativo(text):
    text = (text or '').strip()
    if not text:
        raise ValidationError(_("El campo Notas es requerido al aplicar un ajuste de inventario."))

    if len(text) < 5:
        raise ValidationError(_(
            "Las notas deben contener al menos 5 caracteres significativos."
        ))

    text_lower = text.lower()
    for pattern in _GIBBERISH_PATTERNS:
        if pattern in text_lower:
            raise ValidationError(_(
                "El campo Notas contiene caracteres sin sentido. "
                "Por favor ingrese información significativa."
            ))

    if re.search(r'(.)\1{3,}', text):
        raise ValidationError(_(
            "El campo Notas contiene caracteres repetidos sin sentido. "
            "Por favor ingrese información significativa."
        ))

    # 4+ consonantes seguidas indican texto sin sentido (ej. "jdhsg")
    if re.search(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{4,}', text):
        raise ValidationError(_(
            "El campo Notas contiene caracteres sin sentido. "
            "Por favor ingrese información significativa."
        ))

    # Proporción de vocales sobre letras totales debe ser al menos 30%
    letters = re.findall(r'[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]', text)
    if letters:
        vowel_ratio = sum(1 for c in letters if c in _VOWELS) / len(letters)
        if vowel_ratio < 0.30:
            raise ValidationError(_(
                "El campo Notas parece contener texto sin sentido. "
                "Por favor ingrese información significativa."
            ))


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    x_notas = fields.Text(string='Notas')

    @api.model
    def _get_inventory_fields_write(self):
        return super()._get_inventory_fields_write() + ['x_notas']

    def action_apply_inventory(self):
        for rec in self:
            _validar_texto_significativo(rec.x_notas)
        return super().action_apply_inventory()

    def action_apply_all(self):
        for rec in self:
            _validar_texto_significativo(rec.x_notas)
        return super().action_apply_all()
