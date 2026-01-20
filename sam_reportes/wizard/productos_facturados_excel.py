# -*- coding: utf-8 -*-

# productos_facturados_excel.py
# Reporte de productos facturados en Excel agrupados por categoría de cliente y cliente.
# VBueno 2025-12-18

import base64
import io
import logging

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("xlsxwriter no está instalado. El reporte Excel no funcionará.")
    xlsxwriter = None


class ProductosFacturadosExcel(models.TransientModel):
    _name = 'productos.facturados.excel.wizard'
    _description = 'Productos facturados en Excel'

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

    def genera_excel(self):
        """Genera el reporte Excel de productos facturados."""

        if not xlsxwriter:
            raise UserError('La librería xlsxwriter no está instalada.')

        # Validar que fecha_fin >= fecha_inicio
        if self.fecha_fin < self.fecha_inicio:
            raise UserError('La fecha fin debe ser mayor o igual a la fecha inicio.')

        # Buscar líneas de factura de clientes publicadas con folio fiscal
        domain = [
            ('move_id.move_type', '=', 'out_invoice'),  # Facturas de cliente
            ('move_id.state', '=', 'posted'),  # Publicadas
            ('move_id.l10n_mx_edi_cfdi_uuid', '!=', False),  # Con folio fiscal
            ('move_id.invoice_date', '>=', self.fecha_inicio),
            ('move_id.invoice_date', '<=', self.fecha_fin),
            ('product_id', '!=', False),  # Solo líneas con producto
        ]

        lineas = self.env['account.move.line'].search(domain)

        if not lineas:
            raise UserError('No se encontraron facturas en el rango de fechas seleccionado.')

        # Agrupar datos por categoría de cliente y cliente
        categorias_data = {}

        for linea in lineas:
            partner = linea.move_id.partner_id

            # Obtener categoría del cliente con complete_name (puede tener múltiples, tomamos la primera)
            categoria_complete = partner.category_id[0].complete_name if partner.category_id else 'Clientes sin categoría'

            # Obtener nombre comercial del cliente
            nombre_comercial = partner.x_nombre_comercial or partner.name or 'Sin nombre'

            # Importe (price_subtotal es el importe sin impuestos)
            importe = linea.price_subtotal or 0.0

            # Inicializar categoría si no existe
            if categoria_complete not in categorias_data:
                categorias_data[categoria_complete] = {
                    'clientes': {},
                    'total_categoria': 0.0
                }

            # Inicializar cliente si no existe
            if nombre_comercial not in categorias_data[categoria_complete]['clientes']:
                categorias_data[categoria_complete]['clientes'][nombre_comercial] = 0.0

            # Acumular importe
            categorias_data[categoria_complete]['clientes'][nombre_comercial] += importe
            categorias_data[categoria_complete]['total_categoria'] += importe

        # Ordenar categorías por total descendente (mejor categoría primero)
        categorias_ordenadas = sorted(
            categorias_data.items(),
            key=lambda x: x[1]['total_categoria'],
            reverse=True
        )

        # Crear archivo Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Ventas por Categoría')

        # Formatos
        formato_titulo = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white'
        })
        formato_encabezado = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E2F3',
            'border': 1
        })
        formato_cliente = workbook.add_format({
            'font_size': 10,
            'border': 1
        })
        formato_importe = workbook.add_format({
            'font_size': 10,
            'num_format': '#,##0.00',
            'border': 1,
            'align': 'right'
        })
        formato_total_general = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'num_format': '#,##0.00',
            'bg_color': '#2F5496',
            'font_color': 'white',
            'border': 1,
            'align': 'right'
        })

        # Configurar anchos de columna
        worksheet.set_column('A:A', 40)  # Categoría
        worksheet.set_column('B:B', 40)  # Cliente
        worksheet.set_column('C:C', 18)  # Importe

        # Título
        worksheet.merge_range('A1:C1', 'VENTAS POR CATEGORÍA DE CLIENTE', formato_titulo)
        worksheet.write('A2', f'Período: {self.fecha_inicio.strftime("%d/%m/%Y")} - {self.fecha_fin.strftime("%d/%m/%Y")}')

        # Encabezados
        row = 3
        worksheet.write(row, 0, 'Categoría', formato_encabezado)
        worksheet.write(row, 1, 'Cliente', formato_encabezado)
        worksheet.write(row, 2, 'Importe Total', formato_encabezado)

        row += 1
        total_general = 0.0

        # Escribir datos
        for categoria_nombre, datos in categorias_ordenadas:
            # Ordenar clientes por importe descendente (mejor cliente primero)
            clientes_ordenados = sorted(
                datos['clientes'].items(),
                key=lambda x: x[1],
                reverse=True
            )

            # Escribir clientes con su categoría
            for nombre_cliente, importe in clientes_ordenados:
                worksheet.write(row, 0, categoria_nombre, formato_cliente)
                worksheet.write(row, 1, nombre_cliente, formato_cliente)
                worksheet.write(row, 2, importe, formato_importe)
                row += 1

            total_general += datos['total_categoria']

        # Total general
        row += 1
        worksheet.merge_range(row, 0, row, 1, 'TOTAL GENERAL', formato_total_general)
        worksheet.write(row, 2, total_general, formato_total_general)

        workbook.close()
        output.seek(0)

        # Crear attachment para descarga
        filename = f'productos_facturados_{self.fecha_inicio.strftime("%Y%m%d")}_{self.fecha_fin.strftime("%Y%m%d")}.xlsx'

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        # Retornar acción de descarga
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
