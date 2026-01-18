# -*- coding: utf-8 -*-
from odoo import models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def default_get(self, fields_list):
        """
        Parche para Odoo 18: Convertir default_res_id a default_res_ids
        ANTES de que se ejecute la validación en el método padre.
        """
        # Si el contexto tiene default_res_id, convertirlo a default_res_ids
        if 'default_res_id' in self.env.context:
            res_id = self.env.context['default_res_id']
            # Crear nuevo contexto sin default_res_id y con default_res_ids
            new_context = dict(self.env.context)
            new_context.pop('default_res_id')
            if res_id:
                new_context['default_res_ids'] = [res_id]
            # Cambiar al nuevo contexto antes de llamar al super
            self = self.with_context(new_context)

        return super().default_get(fields_list)
