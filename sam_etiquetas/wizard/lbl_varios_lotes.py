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
    # especie = fields.Selection(string="Especie", selection=[('ave', 'AVE'), ('res', 'RES'),('cerdo', 'CERDO'),
    #                                                         ('cerdo_res', 'CERDO Y RES')], required=True, )

    cantidad = fields.Integer(string="Cantidad")

    # producto = fields.Many2one('mrp.bom', string="Producto")
    # cantidad = fields.Float(string="Cantidad")
    # ing_limitante = fields.Many2one('mrp.bom.line',string="Ingrediente limitante")
    # cant_limitante = fields.Float(string="Cantidad limitante")
    # consolidado = fields.Boolean(string="Fórmula consolidada",  )

    # permite seleccionar el ingrediente limitante.
    @api.onchange('lote1')
    def onchange_lote1(self):
        if self.especie != self.lote1.product_id.x_cod_especie:
            raise UserError('El lote no pertenece a la especie indicada')

    def imprimelblvarioslotes(self):
        vals = []

        if self.lote1:
            vals.append({
                'producto': self.lote1.product_id.name,
                'lote': self.lote1.name,
                'elaboracion': self.lote1.create_date,
                'caducidad': self.lote1.life_date
                })

        data = {'ids': self.ids,
                'model': self._name,
                'vals': vals,
                'lote1': self.lote1,
                'lote2': self.lote2,
                'lote3': self.lote3,
                'lote4': self.lote4,
                'lote5': self.lote5
                }

        return self.env.ref('sam_etiquetas.lblvarioslotes_reporte').report_action(self, data=data)