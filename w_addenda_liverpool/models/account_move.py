# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_order_liv = fields.Char(
        string='Purchase order liverpool',
        copy=False
    )
    delivery_folio = fields.Char(
        string='Delivery folio',
        copy=False
    )
    date_delivery = fields.Date(
        string='Date delivery',
        copy=False
    )
    show_addenda_liverpool = fields.Boolean(
        string="Show Addenda Liverpool",
        related='partner_id.generate_addenda_liverpool',
    )
    require_addenda_liverpool = fields.Boolean(
        string="Use Addenda Liverpool",
        compute='_compute_require_addenda_liverpool',
        store=True,
    )

    @api.depends('purchase_order_liv', 'delivery_folio', 'date_delivery')
    def _compute_require_addenda_liverpool(self):
        for move in self:
            move.require_addenda_liverpool = bool(
                move.purchase_order_liv or move.delivery_folio or move.date_delivery
            )

    @api.onchange('purchase_order_liv', 'delivery_folio', 'date_delivery')
    def _onchange_addenda_liverpool_fields(self):
        """Auto-assign Liverpool addenda when any addenda field has data."""
        liverpool_addenda = self.env.ref('w_addenda_liverpool.addenda_liverpool', raise_if_not_found=False)
        if not liverpool_addenda:
            return
        has_data = self.purchase_order_liv or self.delivery_folio or self.date_delivery
        if has_data and not self.l10n_mx_edi_addenda_id:
            self.l10n_mx_edi_addenda_id = liverpool_addenda
        elif not has_data and self.l10n_mx_edi_addenda_id == liverpool_addenda:
            self.l10n_mx_edi_addenda_id = False

    def _l10n_mx_edi_addenda_liverpool(self):
        """Generate Liverpool addenda by calling the addenda model method."""
        from markupsafe import Markup
        self.ensure_one()
        if self.l10n_mx_edi_addenda_id and self.l10n_mx_edi_addenda_id.name == 'Liverpool':
            xml_content = self.l10n_mx_edi_addenda_id._l10n_mx_edi_render_addenda_liverpool(self)
            return Markup(xml_content)
        return Markup('')

    def unescape_characters(self, value):
        """Remove accents and special characters from text."""
        import unidecode
        return unidecode.unidecode(value)

    def get_total_amount(self):
        """Get total amount formatted for addenda."""
        return "%.2f" % round(self.amount_untaxed, 2)

    def _l10n_mx_edi_cfdi_amount_to_text(self):
        """Convert the invoice amount to text in Spanish."""
        self.ensure_one()
        if hasattr(super(AccountMove, self), '_l10n_mx_edi_cfdi_amount_to_text'):
            return super()._l10n_mx_edi_cfdi_amount_to_text()
        try:
            from odoo.addons.l10n_mx_edi.models.account_edi_format import CURRENCY_CODE_TO_NAME
            amount_text = self.currency_id.with_context(lang='es_MX').amount_to_text(self.amount_total)
            return amount_text.upper()
        except:
            return ""


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_price_gross(self):
        taxes_line = self.tax_ids
        if hasattr(taxes_line, 'flatten_taxes_hierarchy'):
            taxes_line = taxes_line.flatten_taxes_hierarchy()
        transferred = taxes_line.filtered(lambda r: r.amount >= 0)
        price_net = self.price_unit * self.quantity
        price_gross = price_net
        if transferred:
            for tax in transferred:
                tasa = abs(tax.amount if tax.amount_type == 'fixed' else (tax.amount / 100.0)) * 100
                price_gross += (price_net * tasa / 100)
        return "%.2f" % round(price_gross, 2)

    def get_price_net(self):
        return "%.2f" % round(self.price_unit * self.quantity, 2)

    def get_gross_amount(self):
        return "%.2f" % round(self.price_total, 2)

    def get_net_amount(self):
        return "%.2f" % round(self.price_subtotal, 2)

    def get_quantity(self):
        return "%.2f" % round(self.quantity, 2)
