# -*- coding: utf-8 -*-
##############################################################################
#
#    VBueno
#    Copyright (C) 2021-TODAY Industrias Alimenticias SAM SA de CV.
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
{
    'name': 'Etiquetas SAM',
    'summary': 'Etiquetas para SAMPER',
    'version': '1.0.0.0.0',
    'category': 'MRP',
    'author': 'VBueno',
    'maintainer': 'Industrias Alimenticias SAM SA de CV',
    'website': 'http://www.samper.mx',
    'license': 'AGPL-3',
    'depends': ['base', 'mrp', ],
    'data': [
        'report/lblvarioslotes_pdf.xml',
        'views/lblvarioslotes_reporte.xml',
    ],
}
