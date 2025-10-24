"""
vbueno 1102202510:52
Módulo para la descarga de archivos XML y PDF asociados a facturas en Odoo v18.

Este módulo extiende el modelo `account.move` para agregar una función que permite
descargar los archivos adjuntos XML y PDF de las facturas seleccionadas.
"""

# Importaciones necesarias para la funcionalidad del módulo
from odoo import models, api  # Permite definir modelos, campos y métodos en Odoo
from odoo.exceptions import UserError  # Manejo de errores personalizados en Odoo
import base64  # Codificación y decodificación en base64 para archivos
import zipfile  # Manejo de archivos ZIP para comprimir múltiples adjuntos
import io  # Manipulación de datos en memoria, como flujos de bytes

class AccountMove(models.Model):
    """
    Extiende el modelo `account.move` para permitir la descarga de los archivos XML y PDF
    asociados a facturas seleccionadas.
    """
    _inherit = 'account.move'

    def action_download_xml(self):
        """
        Descarga los archivos XML y PDF de las facturas seleccionadas.
        
        Si hay un solo archivo, se descarga directamente. Si hay múltiples archivos,
        se comprimen en un archivo ZIP antes de la descarga.
        
        :raises UserError: Si no se selecciona ninguna factura o si no se encuentran archivos adjuntos.
        :return: Acción de descarga del archivo XML/PDF o del archivo ZIP.
        """
        # Obtener los IDs de las facturas seleccionadas desde el contexto
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError('Debe seleccionar al menos una factura')

        # Buscar los registros de facturas seleccionadas
        selected_moves = self.browse(active_ids)
        if not selected_moves:
            raise UserError('No se pudieron cargar las facturas seleccionadas.')

        # Buscar adjuntos XML asociados a las facturas seleccionadas
        # En Odoo v18, buscamos por extensión de archivo ya que mimetype puede variar
        xml_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('name', 'ilike', '.xml')
        ])

        # Buscar adjuntos PDF asociados a las facturas seleccionadas
        pdf_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', 'in', selected_moves.ids),
            ('name', 'ilike', '.pdf')
        ])

        # Combinar los adjuntos XML y PDF
        attachments = xml_attachments + pdf_attachments

        if not attachments:
            debug_message = f"Facturas seleccionadas: {selected_moves.mapped('name')}\nNo se encontraron archivos XML o PDF para estas facturas."
            raise UserError(debug_message)

        if len(attachments) == 1:
            # Descargar directamente el único archivo encontrado
            attachment = attachments[0]
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        # Si hay múltiples archivos, crear un ZIP en memoria
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for attachment in attachments:
                # En Odoo v18, 'datas' sigue siendo el campo correcto para leer
                zip_file.writestr(attachment.name, base64.b64decode(attachment.datas))

        # Codificar el ZIP en base64
        zip_data = base64.b64encode(zip_buffer.getvalue())

        # Crear un adjunto temporal con el ZIP
        zip_attachment = self.env['ir.attachment'].create({
            'name': 'facturas_xml_pdf.zip',
            'type': 'binary',
            'raw': zip_data,  # En Odoo v18, usar 'raw' en lugar de 'datas' para escritura
            'mimetype': 'application/zip'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{zip_attachment.id}?download=true',
            'target': 'self',
        }
