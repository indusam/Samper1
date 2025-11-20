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
from odoo import models, fields


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    # Flag to mark views as EDI Addenda templates
    # If l10n_mx_edi doesn't define it, we create it here
    l10n_mx_edi_addenda_flag = fields.Boolean(
        string='Is EDI Addenda',
        help='Mark this view as an EDI addenda template for Mexican invoices'
    )
