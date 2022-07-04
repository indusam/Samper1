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

    dfecha = datetime.date.today()
    fecha = fields.Date(string="Fecha", default=dfecha)
    
    # Selecciona e imprime los saldos de los clientes.
    def imprime_saldos_clientes(self):
        
        # domain = [('total_due', '>', 0)]
        saldos = self.env['res.partner'].search([('credit', '>', 0)])

        clientes = []
        for cliente in saldos:
            vals = {
                'name': cliente.name,
                'x_nombre_comercial': cliente.x_nombre_comercial,
                'total_invoiced': cliente.total_invoiced,
                'total_due': cliente.total_due,
                'total_overdue': cliente.total_overdue
            } 

            clientes.append(vals)

        data = {'form_data': self.read()[0],
                'fecha': self.fecha,
                'clientes': clientes}
   
        return self.env.ref('sam_reportes.saldos_clientes_reporte').report_action(self, data=data)



        # saldos = []
        # # Obtiene los clientes con saldo.
        # clientes = self.env['res.partner'].search([('total_due', '>', 0)])
        
        # if not clientes:
        #     raise UserError('No hay clientes con saldo.')

        # # Recorre los clientes.
        # for cliente in clientes: 
        #     # Guarda los valores en vals.
        #     vals = {
        #             'cliente': cliente.name,
        #             'nombre_comercial': cliente.x_nombre_comercial,
        #             'total_facturado': cliente.total_invoiced, 
        #             'total_adeudado': cliente.total_due,
        #             'total_vencido': cliente.total_overdue
        #              }
            
        #     saldos.append(vals)

        

        # data = {'ids': self.ids,
        #         'model': self._name,
        #         'vals': vals,
        #         'fecha': datetime.date.today(),
        #         'compania': self.env.company.name
        #         }

        # # return self.env['report'].get_action(self, 'saldos_clientes.saldos_clientes_report', data=data)
   