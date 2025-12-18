# -*- coding: utf-8 -*-
from odoo import models, api


class IrActionsActWindow(models.Model):
    _inherit = 'ir.actions.act_window'

    @api.model
    def _get_action_context(self, action):
        """
        Fix para Odoo 18: Convertir default_res_id a default_res_ids
        cuando se ejecuta la acción de envío de recibos de pago.
        """
        context = super()._get_action_context(action)

        # Si hay default_res_id en el contexto, convertirlo a default_res_ids
        if 'default_res_id' in context:
            res_id = context.pop('default_res_id')
            if res_id:
                context['default_res_ids'] = [res_id]

        return context
