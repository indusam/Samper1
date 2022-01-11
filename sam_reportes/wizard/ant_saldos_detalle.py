# -*- coding: utf-8 -*-

# ant_saldos_detalle.py
# Reporte de detalle de antiguedad de saldos de clientes.
# VBueno 0911202115:37

import datetime
import logging

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AntiguedadSaldosDetalle(models.TransientModel):
    _name = 'ant.saldos.detalle.wizard'
    _description = 'Antiguedad de saldos detalle'

    dfinal = datetime.date.today()
    fecha_corte = fields.Date(string="Fecha Corte", default=dfinal)
    
    # Calcula e imprime la antiguedad de saldos de clientes.
    def imprime_antiguedad_saldos_detalle(self):
        
        vals = []
        # Obtiene las facturas con saldo.
        facturas = self.env['account.move'].search([('l10n_mx_edi_pac_status', '=', 'signed'), 
                    ('type', '=', 'out_invoice'), ('amount_residual','>',0),
                     ('invoice_date', '<=', self.fecha_corte)])
    

        # Recorre las facturas.
        
        if facturas:
            # Ordena facturas por cliente.
            facturas = facturas.sorted(key=lambda r: r.partner_id.name)
            for factura in facturas:
                n30d = n60d = n90d = nmas90 = no_vencido = 0

                # Calcula los días de vencimiento.
                ndias = (self.fecha_corte - factura.x_fecha_vencimiento).days
                
                # Si ndias > 0 la factura está vencida.
                if ndias > 0:
                    if ndias <= 30:
                        n30d = factura.amount_residual
                        
                    elif ndias > 30 and ndias <= 60:
                        n60d = factura.amount_residual
                       
                    elif ndias > 60 and ndias <= 90:
                        n90d = factura.amount_residual
                        
                    else:
                        nmas90 = factura.amount_residual
                else:
                    no_vencido = factura.amount_residual

                # Guarda los valores en vals.
                vals.append({
                    'empresa': factura.partner_id.name,
                    'factura': factura.name,
                    'fecha': factura.invoice_date, 
                    'ntotal': factura.amount_total,
                    'ndeuda': factura.amount_residual, 
                    'n30d': n30d, 
                    'n60d': n60d, 
                    'n90d': n90d, 
                    'nmas90': nmas90, 
                    'no_vencido': no_vencido})


        data = {'ids': self.ids,
                'model': self._name,
                'vals': vals,
                'fecha': datetime.date.today(),
                'corte': self.fecha_corte,
                'compania': self.env.company.name,
                }

        return self.env.ref(
            'sam_reportes.ant_saldos_detalle_reporte').report_action(self, data=data)
