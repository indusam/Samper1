# Impresión etiqueta con varios lotes
# VBueno 2109202115:21

# Impresión de etiqueta rectangular con varios lotes.
# Los lotes deben ser de la misma especie.

import logging
from odoo.tools.float_utils import float_round
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class LblVariosLotes(models.TransientModel):

    _name = 'wizard.lbl_varios_lotes'
    _description = 'Etiqueta con varios lotes'

    lote1 = fields.Many2one('stock.production.lot', string="Lote 1")
    lote2 = fields.Many2one('stock.production.lot', string="Lote 2")
    lote3 = fields.Many2one('stock.production.lot', string="Lote 3")
    lote4 = fields.Many2one('stock.production.lot', string="Lote 4")
    lote5 = fields.Many2one('stock.production.lot', string="Lote 5")
    especies = fields.Selection(string="Especie", selection=[('ave', 'AVE'), ('res', 'RES'), ('cerdo', 'CERDO'),
                                                             ('cerdo_res', 'CERDO Y RES')], required=True)
    # permite seleccionar el ingrediente limitante.
    @api.onchange('lote1')
    def onchange_lote1(self):
        if self.especies != self.lote1.product_id.x_cod_especie:
            raise UserError('El lote no pertenece a la especie indicada')

    @api.onchange('lote2')
    def onchange_lote2(self):
        if self.especies != self.lote2.product_id.x_cod_especie:
            raise UserError('El lote no pertenece a la especie indicada')

    @api.onchange('lote3')
    def onchange_lote3(self):
        if self.especies != self.lote3.product_id.x_cod_especie:
            raise UserError('El lote no pertenece a la especie indicada')

    @api.onchange('lote4')
    def onchange_lote4(self):
        if self.especies != self.lote4.product_id.x_cod_especie:
            raise UserError('El lote no pertenece a la especie indicada')

    @api.onchange('lote5')
    def onchange_lote5(self):
        if self.especies != self.lote5.product_id.x_cod_especie:
            raise UserError('El lote no pertenece a la especie indicada')

    def imprimelblvarioslotes(self):
        vals = []

        if self.lote1:
            vals.append({
                'producto': self.lote1.product_id.name,
                'lote': self.lote1.name,
                'elaboracion': self.lote1.create_date,
                'caducidad': self.lote1.life_date,
            })

        if self.lote2:
            vals.append({
                'producto': self.lote2.product_id.name,
                'lote': self.lote2.name,
                'elaboracion': self.lote2.create_date,
                'caducidad': self.lote2.life_date,
                })

        if self.lote3:
            vals.append({
                'producto': self.lote3.product_id.name,
                'lote': self.lote3.name,
                'elaboracion': self.lote3.create_date,
                'caducidad': self.lote3.life_date,
            })

        if self.lote4:
            vals.append({
                'producto': self.lote4.product_id.name,
                'lote': self.lote4.name,
                'elaboracion': self.lote4.create_date,
                'caducidad': self.lote4.life_date,
            })

        if self.lote5:
            vals.append({
                'producto': self.lote5.product_id.name,
                'lote': self.lote5.name,
                'elaboracion': self.lote5.create_date,
                'caducidad': self.lote5.life_date,
            })

        data = {'ids': self.ids,
                'model': self._name,
                'especie': self.especies,
                'vals': vals,
                }

        return self.env.ref('sam_etiquetas.lblvarioslotes_reporte').report_action(self, data=data)