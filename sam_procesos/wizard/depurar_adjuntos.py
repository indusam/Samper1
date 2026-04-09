# -*- coding: utf-8 -*-
"""
Módulo: depurar_adjuntos.py
Descripción:
    Elimina archivos adjuntos (PDF, ZIP, JPG, JPEG, PNG) con fecha anterior
    a una fecha de corte, procesándolos en batches semanales de 7 días e
    informando el progreso de cada batch en pantalla.

Autor: VBueno
Fecha: 09/04/2026
"""

import logging
import os
from datetime import timedelta

from odoo import models, fields
from odoo.tools import config

_logger = logging.getLogger(__name__)

EXTENSIONES = ['.pdf', '.zip', '.jpg', '.jpeg', '.png']


class DepurarAdjuntos(models.TransientModel):
    """
    Wizard para la eliminación por batches semanales de archivos adjuntos
    (PDF, ZIP, JPG, JPEG, PNG) anteriores a una fecha de corte.
    """

    _name = 'depurar_adjuntos.wizard'
    _description = 'Depurar Adjuntos'

    corte = fields.Date(
        string="Fecha de Corte",
        required=True,
        default=lambda self: fields.Date.today()
    )
    progreso = fields.Html(
        string="Progreso",
        readonly=True,
        sanitize=False,
    )

    def _build_ext_domain(self):
        """Construye el dominio OR para todas las extensiones soportadas."""
        condiciones = [('name', 'ilike', ext) for ext in EXTENSIONES]
        dominio = []
        for cond in condiciones[:-1]:
            dominio += ['|', cond]
        dominio.append(condiciones[-1])
        return dominio

    def depurar(self):
        """
        Busca todos los adjuntos con extensiones soportadas anteriores a la
        fecha de corte, los agrupa en batches de 7 días (del archivo más
        antiguo hasta la fecha de corte) y los elimina batch por batch,
        mostrando el progreso en el formulario.
        """
        self.ensure_one()

        dominio_base = [('create_date', '<=', self.corte)]
        dominio_ext = self._build_ext_domain()
        archivos = self.env['ir.attachment'].sudo().search(dominio_base + dominio_ext)

        if not archivos:
            self.write({
                'progreso': (
                    '<p style="color:#e65c00;font-weight:bold;">'
                    'No se encontraron archivos para eliminar.</p>'
                )
            })
            return self._reopen()

        fecha_inicio = min(archivos.mapped('create_date')).date()
        fecha_corte = self.corte

        # Ruta real del filestore: {data_dir}/filestore/{dbname}
        filestore_path = config.filestore(self.env.cr.dbname)

        filas_html = ''
        total_eliminados = 0
        total_desvinculados = 0
        batch_num = 1
        fecha_desde = fecha_inicio

        while fecha_desde <= fecha_corte:
            fecha_hasta = min(fecha_desde + timedelta(days=6), fecha_corte)

            batch = archivos.filtered(
                lambda a, d=fecha_desde, h=fecha_hasta:
                d <= a.create_date.date() <= h
            )

            eliminados = 0
            desvinculados = 0
            for archivo in batch:
                if archivo.store_fname:
                    file_path = os.path.join(filestore_path, archivo.store_fname)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        eliminados += 1
                        _logger.info("Archivo eliminado: %s (%s)", archivo.name, file_path)
                    else:
                        desvinculados += 1
                        _logger.warning("Archivo no encontrado en disco: %s", file_path)
                else:
                    desvinculados += 1
                archivo.sudo().write({'res_id': 0})

            total_eliminados += eliminados
            total_desvinculados += desvinculados

            filas_html += (
                f'<tr>'
                f'<td style="text-align:center">{batch_num}</td>'
                f'<td style="text-align:center">{fecha_desde.strftime("%d/%m/%Y")}</td>'
                f'<td style="text-align:center">{fecha_hasta.strftime("%d/%m/%Y")}</td>'
                f'<td style="text-align:center">{len(batch)}</td>'
                f'<td style="text-align:center">{eliminados}</td>'
                f'<td style="text-align:center">{desvinculados}</td>'
                f'</tr>'
            )
            _logger.info(
                "Batch %d (%s - %s): %d eliminados, %d desvinculados",
                batch_num, fecha_desde, fecha_hasta, eliminados, desvinculados
            )

            batch_num += 1
            fecha_desde = fecha_hasta + timedelta(days=1)

        progreso_html = f"""
        <div style="font-family:monospace;font-size:13px;">
            <table style="width:100%;border-collapse:collapse;margin-bottom:12px;">
                <thead>
                    <tr style="background:#875a7b;color:white;">
                        <th style="padding:6px 10px;">Batch</th>
                        <th style="padding:6px 10px;">Desde</th>
                        <th style="padding:6px 10px;">Hasta</th>
                        <th style="padding:6px 10px;">Encontrados</th>
                        <th style="padding:6px 10px;">Eliminados</th>
                        <th style="padding:6px 10px;">Desvinculados</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
            <p style="font-weight:bold;">
                Total batches procesados: {batch_num - 1} &nbsp;|&nbsp;
                Archivos eliminados del disco: {total_eliminados} &nbsp;|&nbsp;
                Registros desvinculados: {total_desvinculados}
            </p>
        </div>
        """

        self.write({'progreso': progreso_html})
        return self._reopen()

    def _reopen(self):
        """Reabre el mismo wizard para mostrar el progreso."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
