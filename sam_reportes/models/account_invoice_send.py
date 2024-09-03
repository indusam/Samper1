# -*- coding: utf-8 -*-
##############################################################################
#
#    VBueno
#    Copyright (C) 2021-TODAY Industrias Alimenticias SAM SA de CV
#    Author: VBueno
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from datetime import datetime
from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class AccountInvoiceSend(models.TransientModel):

    _inherit = 'account.invoice.send'

    is_print = fields.Boolean(string="Print", default=False)
