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
        """Descarga los archivos XML y PDF de las facturas seleccionadas.

        Los XMLs se obtienen de ir.attachment (son los CFDI timbrados).
        Los PDFs se generan siempre al vuelo para asegurar el formato correcto.
        """
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError('Debe seleccionar al menos una factura')

        selected_moves = self.browse(active_ids)
        if not selected_moves:
            raise UserError('No se pudieron cargar las facturas seleccionadas.')

        # Buscar XMLs en ir.attachment (uno por factura)
        xml_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('name', 'ilike', '.xml')
        ])

        # Generar TODOS los PDFs al vuelo para asegurar formato correcto
        generated_pdfs = {}
        report = self.env.ref('account.account_invoices')
        for move in selected_moves:
            try:
                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                    report, [move.id]
                )
                generated_pdfs[move.name] = pdf_content
            except Exception:
                pass  # Si falla la generación, se omite

        if not xml_attachments and not generated_pdfs:
            raise UserError(
                f"Facturas seleccionadas: {selected_moves.mapped('name')}\n"
                f"No se encontraron archivos XML y no se pudieron generar PDFs."
            )

        # Limpiar archivos ZIP temporales antiguos (más de 1 hora)
        old_zips = self.env['ir.attachment'].search([
            ('name', '=', 'facturas_xml_pdf.zip'),
            ('res_model', '=', False),
            ('create_date', '<', fields.Datetime.now() - timedelta(hours=1))
        ])
        old_zips.unlink()

        # Crear ZIP
        zip_buffer = io.BytesIO()
        used_keys = set()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Agregar XMLs (evitando duplicados por número de factura)
            for attachment in xml_attachments:
                fname = attachment.name
                invoice_key = None
                for move in selected_moves:
                    if move.name and move.name in fname:
                        invoice_key = f"{move.name}_xml"
                        break
                if not invoice_key:
                    invoice_key = fname

                if invoice_key not in used_keys:
                    used_keys.add(invoice_key)
                    zip_file.writestr(fname, base64.b64decode(attachment.datas))

            # Agregar PDFs generados al vuelo
            for move_name, pdf_content in generated_pdfs.items():
                invoice_key = f"{move_name}_pdf"
                if invoice_key not in used_keys:
                    used_keys.add(invoice_key)
                    zip_file.writestr(f"{move_name}.pdf", pdf_content)

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
