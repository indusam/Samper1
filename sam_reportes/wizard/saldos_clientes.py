# -*- coding: utf-8 -*-

# saldos_clientes.py
# Reporte salods de clientes.
# VBueno 1101202113:28

import datetime
import logging

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaldosClientes(models.TransientModel):
    _name = 'saldos.clientes.wizard'
    _description = 'Saldos de clientes'

    #dfinal = datetime.date.today()
    #fecha_corte = fields.Date(string="Fecha Corte", default=dfinal)
    
    # Selecciona e imprime los saldos de los clientes.
    def imprime_saldos_clientes(self):
        
        vals = []
        # Obtiene los clientes con saldo.
        clientes = self.env['res.partner'].search([('total_due', '>', 0)])
        
        if not clientes:
            raise UserError('No hay clientes con saldo.')

        # Recorre los clientes.
        if clientes:
            for cliente in clientes: 
                # Guarda los valores en vals.
                if cliente.total_due > 0:
                    vals.append({
                        'cliente': cliente.name,
                        'nombre_comercial': cliente.x_nombre_comercial,
                        'total_facturado': cliente.total_invoiced, 
                        'total_adeudado': cliente.total_due,
                        'total_vencido': cliente.total_overdue})


        data = {'ids': self.ids,
                'model': self._name,
                'vals': vals,
                'fecha': datetime.date.today()
                #'compania': self.env.company.name
                }

        return self.env.ref(
            'sam_reportes.saldos_clientes_reporte').report_action(self, data=data)
