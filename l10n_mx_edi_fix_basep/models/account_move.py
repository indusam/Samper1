from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_mx_edi_add_payment_cfdi_values(self, cfdi_values, pay_results):
        """Fix CRP20268: BaseP debe ser igual a la suma de los BaseDR redondeados individualmente.

        Odoo Enterprise acumula raw_base como suma de flotantes de 6 decimales y luego
        redondea la suma total. Esto genera que round(Σ xi, 2) difiera en ±0.01 de
        Σ round(xi, 2), que es lo que el SAT compara contra la suma de BaseDR en el XML.

        Este override recalcula traslado['base'] para cada impuesto del pago sumando
        los BaseDR ya redondeados a 2 decimales (uno por factura relacionada).
        """
        super()._l10n_mx_edi_add_payment_cfdi_values(cfdi_values, pay_results)

        # Si hubo error (ej. RFCs distintos entre facturas), no modificar
        if cfdi_values.get('errors'):
            return

        invoice_values_list = cfdi_values.get('docto_relationado_list', [])

        for traslado in cfdi_values.get('traslados_list', []):
            impuesto = traslado.get('impuesto')
            tipo_factor = traslado.get('tipo_factor')
            tasa = traslado.get('tasa_o_cuota') or 0.0

            rounded_base_sum = 0.0
            for inv_values in invoice_values_list:
                # equivalencia = tipo de cambio factura/pago (None si misma moneda → 1.0)
                inv_rate = inv_values.get('equivalencia') or 1.0
                for inv_tax in inv_values.get('traslados_list', []):
                    if (inv_tax.get('impuesto') == impuesto
                            and inv_tax.get('tipo_factor') == tipo_factor
                            and abs((inv_tax.get('tasa_o_cuota') or 0.0) - tasa) < 1e-6):
                        # BaseDR en el XML = round(base_factura / equivalencia, 2)
                        # Sumar los BaseDR ya redondeados para que BaseP = Σ BaseDR
                        base_dr = round(inv_tax['base'] / inv_rate, 2) if inv_rate else 0.0
                        rounded_base_sum += base_dr

            if rounded_base_sum:
                traslado['base'] = rounded_base_sum
