# -*- encoding: utf-8 -*-
#
# Module written to Odoo, Open Source Management Solution
#
# Copyright (c) 2022 Birtum - http://www.birtum.com/
# All Rights Reserved.
#
# Developer(s): Eddy Luis Pérez Vila
#               (epv@birtum.com)
########################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    global_localitation_number_cm = fields.Char(
        string='Global localitation number(GLN/CM)',
        help='Specifies the global location number (GLN) of the buyer CM.',
        copy=False,
        size=13
    )
    generate_mexican_commercial_addenda = fields.Boolean(
        string='Generate Mexican Commercial Addenda',
        compute='_compute_is_mexican_commercial_addenda',
        help='Check this field if require generate Mexican Commercial Addenda')


    @api.depends('l10n_mx_edi_addenda', 'commercial_partner_id.l10n_mx_edi_addenda')
    def _compute_is_mexican_commercial_addenda(self):
        for rec in self:
            addenda = (rec.l10n_mx_edi_addenda or
                    rec.commercial_partner_id.l10n_mx_edi_addenda)
            if addenda.id == self.env.ref(
                'addenda_comercial_mexicana.mexican_commercial_addenda').id:
                rec.generate_mexican_commercial_addenda = True
            else:
                rec.generate_mexican_commercial_addenda = False
