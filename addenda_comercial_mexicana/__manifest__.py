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
    'name': 'Birtum | Mexican Commercial Addenda',
    'author': 'Birtum',
    'category': 'Extra Tools',
    'sequence': 50,
    'summary': "Birtum | Mexican Commercial Addenda",
    'website': 'https://www.birtum.com',
    'version': '18.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
Birtum | Mexican Commercial Addenda
==================================
This module generate Mexican Commercial Addenda

License
=======

GNU General Public License as published by the Free Software Foundation, version 3
<https://www.gnu.org/licenses/gpl-3.0.en.html>


Authors
=======

* Eddy Luis Pérez Vila (epv@birtum.com)
        """,
    'depends': [
        'base',
        'account',
        'l10n_mx_edi'
    ],
    'data': [
        'data/addenda.xml',
        'views/inherit_res_company_views.xml',
        'views/inherit_account_invoice_views.xml',
        'views/inherit_res_partner_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False
}