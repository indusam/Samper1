# -*- encoding: utf-8 -*-
from odoo import models


class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _render(self, template, values=None, **options):
        if values is not None and 'record' not in values:
            record = self.env.context.get('l10n_mx_edi_cfdi_record')
            if record:
                values = dict(values)
                values['record'] = record
        return super()._render(template, values, **options)
