# -*- coding: utf-8 -*-
"""
vbueno 1102202510:52
Módulo para la descarga de archivos XML y PDF asociados a facturas en Odoo.

Este módulo extiende el modelo `account.move` para agregar una función que permite
descargar los archivos adjuntos XML y PDF de las facturas seleccionadas.
"""

from odoo import models
from odoo.exceptions import UserError
import base64
import zipfile
import io


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_download_xml(self):
        """
        Descarga los archivos XML y PDF de las facturas seleccionadas.

        Si hay un solo archivo, se descarga directamente. Si hay múltiples archivos,
        se comprimen en un archivo ZIP antes de la descarga.
        """
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError('Debe seleccionar al menos una factura')

        selected_moves = self.browse(active_ids)
        if not selected_moves:
            raise UserError('No se pudieron cargar las facturas seleccionadas.')

        # Buscar adjuntos directamente asociados a las facturas (XML del CFDI)
        direct_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
        ])

        # Buscar adjuntos en los mensajes del chatter (PDFs)
        # Los PDFs se adjuntan a mail.message, no directamente a account.move
        messages = self.env['mail.message'].search([
            ('model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
        ])
        message_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'mail.message'),
            ('res_id', 'in', messages.ids),
        ]) if messages else self.env['ir.attachment']

        # Combinar todos los adjuntos
        all_attachments = direct_attachments | message_attachments

        if not all_attachments:
            raise UserError(
                f"Facturas seleccionadas: {selected_moves.mapped('name')}\n"
                f"No se encontraron adjuntos para estas facturas."
            )

        # Filtrar XML y PDF
        attachments = all_attachments.filtered(
            lambda a: a.name.lower().endswith('.xml') or
                      a.name.lower().endswith('.pdf') or
                      a.mimetype == 'application/pdf'
        )

        if not attachments:
            raise UserError(
                f"Facturas seleccionadas: {selected_moves.mapped('name')}\n"
                f"No se encontraron archivos XML o PDF para estas facturas."
            )

        if len(attachments) == 1:
            attachment = attachments[0]
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        # Si hay múltiples archivos, crear un ZIP
        zip_buffer = io.BytesIO()
        used_names = set()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for attachment in attachments:
                # Evitar nombres duplicados en el ZIP
                filename = attachment.name
                if filename in used_names:
                    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
                    filename = f"{name}_{attachment.id}.{ext}" if ext else f"{name}_{attachment.id}"
                used_names.add(filename)
                zip_file.writestr(filename, base64.b64decode(attachment.datas))

        zip_buffer.seek(0)
        zip_data = base64.b64encode(zip_buffer.getvalue())

        zip_attachment = self.env['ir.attachment'].create({
            'name': 'facturas_xml_pdf.zip',
            'type': 'binary',
            'datas': zip_data,
            'mimetype': 'application/zip'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{zip_attachment.id}?download=true',
            'target': 'self',
        }
