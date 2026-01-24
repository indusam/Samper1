# -*- coding: utf-8 -*-
"""
vbueno 1102202510:52
Módulo para la descarga de archivos XML y PDF asociados a facturas en Odoo.

Este módulo extiende el modelo `account.move` para agregar una función que permite
descargar los archivos adjuntos XML y PDF de las facturas seleccionadas.
"""

from datetime import timedelta

from odoo import models, fields
from odoo.exceptions import UserError
import base64
import zipfile
import io


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_download_xml(self):
        """Descarga los archivos XML y PDF de las facturas seleccionadas."""
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError('Debe seleccionar al menos una factura')

        selected_moves = self.browse(active_ids)
        if not selected_moves:
            raise UserError('No se pudieron cargar las facturas seleccionadas.')

        attachments_to_download = self.env['ir.attachment']

        # Buscar XMLs en ir.attachment (uno por factura)
        xml_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('name', 'ilike', '.xml')
        ])
        attachments_to_download += xml_attachments

        # Buscar PDFs: primero en ir.attachment, si no hay para una factura buscar en mail.message
        invoices_with_pdf = set()
        pdf_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('mimetype', '=', 'application/pdf')
        ])

        # Agregar un solo PDF por factura desde ir.attachment
        for pdf in pdf_attachments:
            move_name = self.browse(pdf.res_id).name
            if move_name and move_name not in invoices_with_pdf:
                invoices_with_pdf.add(move_name)
                attachments_to_download += pdf

        # Para facturas sin PDF en ir.attachment, buscar en mail.message
        moves_without_pdf = selected_moves.filtered(lambda m: m.name not in invoices_with_pdf)
        if moves_without_pdf:
            messages = self.env['mail.message'].search([
                ('model', '=', 'account.move'),
                ('res_id', 'in', moves_without_pdf.ids),
            ])
            if messages:
                pdf_from_messages = self.env['ir.attachment'].search([
                    ('res_model', '=', 'mail.message'),
                    ('res_id', 'in', messages.ids),
                    ('mimetype', '=', 'application/pdf')
                ])
                for pdf in pdf_from_messages:
                    # Buscar el número de factura en el nombre del archivo
                    msg = self.env['mail.message'].browse(pdf.res_id)
                    move_name = self.browse(msg.res_id).name if msg.res_id else False
                    if move_name and move_name not in invoices_with_pdf:
                        invoices_with_pdf.add(move_name)
                        attachments_to_download += pdf

        if not attachments_to_download:
            raise UserError(
                f"Facturas seleccionadas: {selected_moves.mapped('name')}\n"
                f"No se encontraron archivos XML o PDF para estas facturas."
            )

        if len(attachments_to_download) == 1:
            attachment = attachments_to_download[0]
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        # Limpiar archivos ZIP temporales antiguos (más de 1 hora)
        old_zips = self.env['ir.attachment'].search([
            ('name', '=', 'facturas_xml_pdf.zip'),
            ('res_model', '=', False),
            ('create_date', '<', fields.Datetime.now() - timedelta(hours=1))
        ])
        old_zips.unlink()

        # Crear ZIP evitando duplicados por número de factura en el nombre
        zip_buffer = io.BytesIO()
        used_invoice_numbers = {}  # {invoice_number: {ext: filename}}
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for attachment in attachments_to_download:
                # Extraer número de factura del nombre del archivo
                fname = attachment.name
                ext = 'xml' if '.xml' in fname.lower() else 'pdf'

                # Buscar si algún número de factura está en el nombre
                invoice_key = None
                for move in selected_moves:
                    if move.name and move.name in fname:
                        invoice_key = f"{move.name}_{ext}"
                        break

                # Si no se encontró número de factura, usar el nombre completo como clave
                if not invoice_key:
                    invoice_key = fname

                if invoice_key not in used_invoice_numbers:
                    used_invoice_numbers[invoice_key] = True
                    zip_file.writestr(fname, base64.b64decode(attachment.datas))

        zip_data = base64.b64encode(zip_buffer.getvalue())
        zip_attachment = self.env['ir.attachment'].create({
            'name': 'facturas_xml_pdf.zip',
            'type': 'binary',
            'datas': zip_data,
            'mimetype': 'application/zip',
            'res_model': False,
            'res_id': False
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{zip_attachment.id}?download=true',
            'target': 'self',
        }
