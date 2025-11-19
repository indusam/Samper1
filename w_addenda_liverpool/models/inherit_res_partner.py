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

    global_localitation_number = fields.Char(
        string='Global localitation number(GLN)',
        help='Specifies the global location number (GLN) of the buyer.',
        copy=False
    )
    person_order_department = fields.Char(
        string='Purchase contact',
        help='specify purchase contact information',
        copy=False
    )
    supplier_identification = fields.Char(
        string='Supplier identification',
        help='Specify the code to identify what type of secondary '
             'identification is assigned to the provider'
    )
    generate_addenda_liverpool = fields.Boolean(
        string='Generate addenda Liverpool',
        help='Check this field if require generate addenda Liverpool')
