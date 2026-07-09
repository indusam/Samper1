# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('is_company', 'zip', 'country_id', 'vat')
    def _check_required_fields_company(self):
        for partner in self:
            if not partner.is_company:
                continue
            missing = []
            if not partner.zip:
                missing.append(_('Código Postal'))
            if not partner.country_id:
                missing.append(_('País'))
            if not partner.vat:
                missing.append(_('RFC/NIF'))
            if missing:
                raise ValidationError(
                    _('Los siguientes campos son obligatorios para contactos de tipo Empresa: %s')
                    % ', '.join(missing)
                )
