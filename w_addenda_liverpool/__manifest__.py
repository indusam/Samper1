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

{
    'name': 'Birtum | Addenda Liverpool',
    'author': 'Birtum ©',
    'category': 'Account',
    'sequence': 50,
    'summary': "Addenda Liverpool",
    'website': 'http://www.birtum.com/',
    'license': 'AGPL-3',
    'version': '16.0',
    'description': """
Addenda Liverpool
===============================================================
This module adds the Liverpool addenda in signed invoices
    """,
    'depends': [
        'base',
        'account',
        'account_accountant',
        'l10n_mx_edi',
        'l10n_mx_edi_40'
    ],
    'data': [
        'data/addenda_liverpool_v40.xml',
        'views/inherit_res_partner_view.xml',
        'views/inherit_res_company_view.xml',
        'views/inherit_account_move_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
}
