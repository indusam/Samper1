from odoo import models, fields, api
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
            raise UserError('Debe seleccionar al menos una factura.')

        selected_moves = self.browse(active_ids)

        # Verificar que haya facturas seleccionadas
        if not selected_moves:
            raise UserError('No se pudieron cargar las facturas seleccionadas.')

        # Buscar los adjuntos XML asociados a las facturas seleccionadas
        xml_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('mimetype', '=', 'application/xml')  # Corrección para Odoo 16
        ])

        # Buscar los adjuntos PDF asociados a las facturas seleccionadas
        pdf_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('mimetype', '=', 'application/pdf')
        ])

        # Combinar XML y PDF
        attachments = xml_attachments + pdf_attachments

        # Si no hay archivos, mostrar error con detalles
        if not attachments:
            debug_message = f"Facturas seleccionadas: {selected_moves.mapped('name')}\nNo se encontraron archivos XML o PDF para estas facturas."
            raise UserError(debug_message)

        if len(attachments) == 1:
            # Descargar el único archivo encontrado
            attachment = attachments[0]
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        # Si hay múltiples archivos, crear un ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for attachment in attachments:
                zip_file.writestr(attachment.name, base64.b64decode(attachment.datas))

        # Codificar el ZIP en base64
        zip_data = base64.b64encode(zip_buffer.getvalue())

        # Crear un adjunto temporal con el ZIP
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

