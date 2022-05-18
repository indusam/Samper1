# -*- encoding: utf-8 -*-
#
# Module written to Odoo, Open Source Management Solution
#
# Copyright (c) 2021 Wedoo - http://www.wedoo.tech/
# All Rights Reserved.
#
# Developer(s): Alan Guzmán
#               (age@wedoo.tech)
#               Andy Torres
#               (atu@wedoo.tech)
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
    'name': 'WEDOO | Addendas liverpool',
    'author': 'WEDOO ©',
    'category': 'Account',
    'sequence': 50,
    'summary': "Addenda liverpool",
    'website': 'https://www.wedoo.tech',
    'version': '1.0',
    'description': """
Addendas liverpool
===============================================================
This module adds the liverpool addendum in signed invoices, the following 
features are adds:
- inheritance of the account.move model, required fields are added.
- inheritance of the res.company model, required fields are added.
- inheritance of the res.partner model, required fields are added.
Also a template is added for render the addenda.
    """,
    'depends': [
        'base',
        'account',
        'l10n_mx_edi'
    ],
    'data': [
        'data/inherit_template_cfdiv33.xml',
        'views/inherit_res_partner_view.xml',
        'views/inherit_res_company_view.xml',
        'views/inherit_account_invoice_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
}
