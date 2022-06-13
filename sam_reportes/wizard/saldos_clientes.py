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
        
        saldos_de_clientes = []
        # Obtiene los clientes con saldo.
        clientes = self.env['res.partner'].search([('total_due', '>', 0)])
        
        if not clientes:
            raise UserError('No hay clientes con saldo.')

        # Recorre los clientes.
        for cliente in clientes: 
            # Guarda los valores en vals.
            vals = {
                    'cliente': cliente.name,
                    'nombre_comercial': cliente.x_nombre_comercial,
                    'total_facturado': cliente.total_invoiced, 
                    'total_adeudado': cliente.total_due,
                    'total_vencido': cliente.total_overdue
                     }
            saldos_de_clientes.append(vals)

        #data = {'ids': self.ids,
        #        'model': self._name,
        #        'vals': vals,
        #        'fecha': datetime.date.today(),
        #         'compania': self.env.company.name
        #        }
        #return self.env['report'].get_action(self, 'saldos_clientes.saldos_clientes_report', data=data)
        data = {'data': self.read()[0],
                'saldos': saldos_de_clientes}

        return self.env.ref(
            'sam_reportes.saldos_clientes_reporte').report_action(self, data=data)
