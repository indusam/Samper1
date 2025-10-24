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
    'category': 'Accounting/Localizations/EDI',
    'sequence': 50,
    'summary': "Addenda Liverpool for Mexican CFDI 4.0",
    'website': 'https://www.birtum.com/',
    'license': 'AGPL-3',
    'version': '18.0.1.0.0',
    'description': """
Addenda Liverpool
===============================================================
This module adds the Liverpool addenda (detallista) to Mexican CFDI 4.0 invoices.

Features:
- Automatic addenda generation for Liverpool customer invoices
- Support for CFDI 4.0 format
- Configurable per partner
- GLN (Global Location Number) support
- Purchase order and delivery folio tracking
    """,
    'depends': [
        'base',
        'account',
        'l10n_mx_edi',
    ],
    'data': [
        # Addenda is now generated programmatically in v18
        # 'data/addenda_liverpool_v40.xml',  # Removed - not needed in v18
        'views/inherit_res_partner_view.xml',
        'views/inherit_res_company_view.xml',
        'views/inherit_account_move_view.xml',
    ],
    'demo': [],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
