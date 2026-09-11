from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_mx_edi_add_payment_cfdi_values(self, cfdi_values, pay_results):
        """Fix CRP20268 y consistencia de Totales — traslados y retenciones.

        Odoo acumula raw_base / raw_importe como suma de flotantes de 6 decimales
        y luego redondea la suma total. Esto genera que round(Σ xi, 2) difiera en
        ±0.01 de Σ round(xi, 2). Este override recalcula BaseP, ImporteP (traslados
        y retenciones) y los campos TotalTraslados*/TotalRetenciones* del nodo
        <pago20:Totales> sumando los valores ya redondeados por documento.

        La fórmula correcta según el SAT es:
            BaseP  = Σ round(BaseDR_i  / EquivalenciaDR_i, 2)
            ImporteP = Σ round(ImporteDR_i / EquivalenciaDR_i, 2)
        donde BaseDR_i / ImporteDR_i son los valores que aparecen en el XML
        (ya redondeados a 2 decimales por el template).
        """
        super()._l10n_mx_edi_add_payment_cfdi_values(cfdi_values, pay_results)

        # Si hubo error (ej. RFCs distintos entre facturas), no modificar
        if cfdi_values.get('errors'):
            return

        invoice_values_list = cfdi_values.get('docto_relationado_list', [])

        def recalc_totals(list_key, is_retencion=False):
            for group in cfdi_values.get(list_key, []):
                impuesto = group.get('impuesto')
                tipo_factor = group.get('tipo_factor')
                tasa = group.get('tasa_o_cuota') or 0.0

                rounded_base = 0.0
                rounded_importe = 0.0
                for inv in invoice_values_list:
                    # equivalencia = None cuando misma moneda → se usa 1.0
                    inv_rate = inv.get('equivalencia') or 1.0
                    for inv_tax in inv.get(list_key, []):
                        if (inv_tax.get('impuesto') == impuesto
                                and inv_tax.get('tipo_factor') == tipo_factor
                                and abs((inv_tax.get('tasa_o_cuota') or 0.0) - tasa) < 1e-6):
                            # Usar .get() para evitar KeyError en retenciones sin base
                            # BaseDR/ImporteDR xml = round(valor_odoo, 2)
                            base_dr = round(inv_tax.get('base', 0.0), 2)
                            importe_dr = round(inv_tax.get('importe', 0.0), 2)
                            # Contribución al total en moneda del pago (÷ equivalencia)
                            rounded_base += round(base_dr / inv_rate, 2)
                            rounded_importe += round(importe_dr / inv_rate, 2)

                if not rounded_base and not rounded_importe:
                    continue

                # Corregir BaseP (solo traslados; retenciones no tienen BaseP en el SAT)
                if not is_retencion:
                    group['base'] = rounded_base

                # Corregir ImporteP (aplica a traslados y retenciones)
                group['importe'] = rounded_importe

                # Sincronizar campos de <pago20:Totales>
                if not is_retencion and impuesto == '002':
                    if tipo_factor == 'Tasa':
                        if abs(tasa) < 1e-6:
                            if cfdi_values.get('total_traslados_base_iva0') is not None:
                                cfdi_values['total_traslados_base_iva0'] = rounded_base
                            if cfdi_values.get('total_traslados_impuesto_iva0') is not None:
                                cfdi_values['total_traslados_impuesto_iva0'] = rounded_importe
                        elif abs(tasa - 0.08) < 1e-6:
                            if cfdi_values.get('total_traslados_base_iva8') is not None:
                                cfdi_values['total_traslados_base_iva8'] = rounded_base
                            if cfdi_values.get('total_traslados_impuesto_iva8') is not None:
                                cfdi_values['total_traslados_impuesto_iva8'] = rounded_importe
                        elif abs(tasa - 0.16) < 1e-6:
                            if cfdi_values.get('total_traslados_base_iva16') is not None:
                                cfdi_values['total_traslados_base_iva16'] = rounded_base
                            if cfdi_values.get('total_traslados_impuesto_iva16') is not None:
                                cfdi_values['total_traslados_impuesto_iva16'] = rounded_importe
                    elif tipo_factor == 'Exento':
                        if cfdi_values.get('total_traslados_base_iva_exento') is not None:
                            cfdi_values['total_traslados_base_iva_exento'] = rounded_base
                elif is_retencion:
                    if impuesto == '001':
                        if cfdi_values.get('total_retenciones_isr') is not None:
                            cfdi_values['total_retenciones_isr'] = rounded_importe
                    elif impuesto == '002':
                        if cfdi_values.get('total_retenciones_iva') is not None:
                            cfdi_values['total_retenciones_iva'] = rounded_importe
                    elif impuesto == '003':
                        if cfdi_values.get('total_retenciones_ieps') is not None:
                            cfdi_values['total_retenciones_ieps'] = rounded_importe

        recalc_totals('traslados_list', is_retencion=False)
        recalc_totals('retenciones_list', is_retencion=True)