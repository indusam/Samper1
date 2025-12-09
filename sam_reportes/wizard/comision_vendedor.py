# -*- coding: utf-8 -*-

# comision_vendedor.py
# Reporte de comisiones por vendedor.
# VBueno 2025-12-05

import datetime
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ComisionVendedor(models.TransientModel):
    _name = 'comision.vendedor.wizard'
    _description = 'Comisiones por vendedor'

    vendedor_id = fields.Many2one(
        'res.partner',
        string='Vendedor',
        required=True,
        domain=[('function', '=', 'vendedor sam')]
    )
    fecha_inicio = fields.Date(
        string='Fecha Inicio',
        required=True,
        default=fields.Date.context_today
    )
    fecha_fin = fields.Date(
        string='Fecha Fin',
        required=True,
        default=fields.Date.context_today
    )

    def imprime_comision_vendedor(self):
        """Genera el reporte de comisiones por vendedor."""

        # Validar que fecha_fin >= fecha_inicio
        if self.fecha_fin < self.fecha_inicio:
            raise UserError('La fecha fin debe ser mayor o igual a la fecha inicio.')

        # Buscar órdenes de venta facturadas en el rango de fechas
        # donde el partner_id tiene asignado este vendedor
        domain = [
            ('invoice_status', '=', 'invoiced'),
            ('create_date', '>=', self.fecha_inicio),
            ('create_date', '<=', self.fecha_fin),
            ('partner_id.x_studio_vendedor_sam', '=', self.vendedor_id.id)
        ]

        ordenes = self.env['sale.order'].search(domain, order='partner_id, create_date')

        if not ordenes:
            raise UserError('No se encontraron órdenes de venta facturadas para el vendedor y rango de fechas seleccionados.')

        # Agrupar datos por cliente
        clientes_data = {}
        total_general_ventas = 0.0
        total_general_comisiones = 0.0

        for orden in ordenes:
            partner_id = orden.partner_id.id
            partner_name = orden.partner_id.name
            comision_pct = orden.partner_id.x_studio_comisin_ or 0.0

            if partner_id not in clientes_data:
                clientes_data[partner_id] = {
                    'partner_name': partner_name,
                    'comision_pct': comision_pct,
                    'ordenes': [],
                    'total_ventas': 0.0,
                    'total_comision': 0.0
                }

            # Obtener facturas relacionadas
            facturas = ', '.join(orden.invoice_ids.mapped('name'))

            # Calcular comisión
            monto_comision = (comision_pct / 100.0) * orden.amount_untaxed

            # Agregar orden a los datos del cliente
            clientes_data[partner_id]['ordenes'].append({
                'create_date': orden.create_date,
                'name': orden.name,
                'invoice_ids': facturas,
                'amount_untaxed': orden.amount_untaxed,
                'comision_pct': comision_pct,
                'monto_comision': monto_comision
            })

            # Acumular totales por cliente
            clientes_data[partner_id]['total_ventas'] += orden.amount_untaxed
            clientes_data[partner_id]['total_comision'] += monto_comision

            # Acumular totales generales
            total_general_ventas += orden.amount_untaxed
            total_general_comisiones += monto_comision

        # Convertir diccionario a lista ordenada
        clientes_list = []
        for partner_id in sorted(clientes_data.keys(), key=lambda k: clientes_data[k]['partner_name']):
            clientes_list.append(clientes_data[partner_id])

        data = {
            'form_data': self.read()[0],
            'vendedor_nombre': self.vendedor_id.name,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'clientes': clientes_list,
            'total_general_ventas': total_general_ventas,
            'total_general_comisiones': total_general_comisiones
        }

        return self.env.ref('sam_reportes.comision_vendedor_reporte').report_action(self, data=data)
