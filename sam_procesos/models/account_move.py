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
        Los PDFs se obtienen de attachments, excepto si:
        - No existe PDF en attachments, o
        - La fecha de la factura está entre 19/01/2026 y 24/01/2026 (formato incorrecto)
        En esos casos se genera el PDF al vuelo.
        """
        from datetime import date

        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError('Debe seleccionar al menos una factura')

        selected_moves = self.browse(active_ids)
        if not selected_moves:
            raise UserError('No se pudieron cargar las facturas seleccionadas.')

        # Fechas del período con formato incorrecto
        fecha_inicio_incorrecto = date(2026, 1, 19)
        fecha_fin_incorrecto = date(2026, 1, 24)

        # Buscar XMLs en ir.attachment (uno por factura)
        xml_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('name', 'ilike', '.xml')
        ])

        # Construir lista de nombres de PDF esperados basados en los XMLs
        # El PDF tiene el mismo nombre que el XML pero con extensión .pdf
        # Ejemplo: INV-SAM0124086-MX-Invoice-4.0.xml -> INV-SAM0124086-MX-Invoice-4.0.pdf
        xml_to_move = {}  # Mapea nombre base del XML al move_id
        pdf_names_to_search = []
        for xml_att in xml_attachments:
            if xml_att.name.lower().endswith('.xml'):
                pdf_name = xml_att.name[:-4] + '.pdf'
                pdf_names_to_search.append(pdf_name)
                xml_to_move[pdf_name] = xml_att.res_id

        # Buscar PDFs por nombre exacto (pueden estar en mail.message)
        pdf_by_move = {}
        if pdf_names_to_search:
            pdf_attachments = self.env['ir.attachment'].search([
                ('name', 'in', pdf_names_to_search),
                ('mimetype', '=', 'application/pdf')
            ])
            # Mapear PDFs por move_id usando la relación XML->move
            for pdf in pdf_attachments:
                move_id = xml_to_move.get(pdf.name)
                if move_id and move_id not in pdf_by_move:
                    pdf_by_move[move_id] = pdf

        # Determinar qué PDFs usar de attachments y cuáles generar al vuelo
        pdf_attachments_to_use = self.env['ir.attachment']
        moves_to_generate_pdf = self.env['account.move']

        for move in selected_moves:
            move_date = move.invoice_date or move.date
            needs_regeneration = (
                move_date and
                fecha_inicio_incorrecto <= move_date <= fecha_fin_incorrecto
            )

            if needs_regeneration or move.id not in pdf_by_move:
                # Generar al vuelo si está en período incorrecto o no tiene PDF
                moves_to_generate_pdf += move
            else:
                # Usar PDF existente
                pdf_attachments_to_use += pdf_by_move[move.id]

        # Generar PDFs al vuelo solo para los que lo necesitan
        generated_pdfs = {}
        if moves_to_generate_pdf:
            report = self.env.ref('account.account_invoices')
            for move in moves_to_generate_pdf:
                try:
                    pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                        report, [move.id]
                    )
                    generated_pdfs[move.name] = pdf_content
                except Exception:
                    pass  # Si falla la generación, se omite

        if not xml_attachments and not pdf_attachments_to_use and not generated_pdfs:
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

            # Agregar PDFs de attachments existentes
            # Crear mapeo inverso: pdf.id -> move_id
            pdf_to_move_id = {pdf.id: move_id for move_id, pdf in pdf_by_move.items()}
            for pdf in pdf_attachments_to_use:
                move_id = pdf_to_move_id.get(pdf.id)
                if move_id:
                    move = self.browse(move_id)
                    invoice_key = f"{move.name}_pdf"
                    if invoice_key not in used_keys:
                        used_keys.add(invoice_key)
                        # Usar el nombre original del PDF (INV-...)
                        zip_file.writestr(pdf.name, base64.b64decode(pdf.datas))

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
