Cómo funciona el módulo w_addenda_liverpool
El módulo genera automáticamente addendas de Liverpool en facturas electrónicas CFDI 4.0 en Odoo v18. Te explico el flujo completo:
1. Activación automática
Configuración del cliente (inherit_res_partner.py)
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    generate_addenda_liverpool = fields.Boolean('Generate Addenda Liverpool')
    global_localitation_number = fields.Char('GLN')
    person_order_department = fields.Char('Contact Person')
    supplier_identification = fields.Char('Supplier ID')
Qué hace: Agrega campos al contacto de Liverpool para:
Activar la generación de addenda
GLN del comprador
Persona de contacto
Identificación del proveedor
2. Auto-selección de addenda
En la factura (account_move.py:30-37)
@api.depends('partner_id', 'partner_id.generate_addenda_liverpool')
def _compute_require_addenda_liverpool(self):
    for move in self:
        move.require_addenda_liverpool = move.partner_id.generate_addenda_liverpool
        if move.partner_id.generate_addenda_liverpool and not move.l10n_mx_edi_addenda_id:
            liverpool_addenda = self.env.ref('w_addenda_liverpool.addenda_liverpool')
            if liverpool_addenda:
                move.l10n_mx_edi_addenda_id = liverpool_addenda
Qué hace: Cuando creas una factura para un cliente con generate_addenda_liverpool=True:
Auto-marca el campo require_addenda_liverpool
Auto-selecciona la addenda Liverpool en el campo l10n_mx_edi_addenda_id
3. Campos adicionales en la factura
Liverpool específicos (account_move.py:12-23)
purchase_order_liv = fields.Char('Purchase order liverpool')
delivery_folio = fields.Char('Delivery folio')
date_delivery = fields.Date('Date delivery')
Qué hace: Permite capturar datos que Liverpool requiere:
Orden de compra de Liverpool
Folio de entrega
Fecha de entrega
4. Generación del XML
Flujo de generación:
A. Punto de entrada (addenda_liverpool_v40.xml:8)
<field name="arch" type="xml">
    <t t-out="record._l10n_mx_edi_addenda_liverpool()"/>
</field>
Qué hace: Cuando Odoo genera el CFDI, ejecuta este template que llama al método Python.
B. Método puente (account_move.py:39-46)
def _l10n_mx_edi_addenda_liverpool(self):
    from markupsafe import Markup
    self.ensure_one()
    if self.l10n_mx_edi_addenda_id and self.l10n_mx_edi_addenda_id.name == 'Liverpool':
        xml_content = self.l10n_mx_edi_addenda_id._l10n_mx_edi_render_addenda_liverpool(self)
        return Markup(xml_content)
    return Markup('')
Qué hace:
Verifica que la addenda Liverpool esté seleccionada
Llama al método generador del modelo addenda
Envuelve el XML en Markup() para que t-out lo renderice correctamente
C. Generador principal (l10n_mx_edi_addenda.py:9-108)
def _l10n_mx_edi_render_addenda_liverpool(self, move):
    # 1. Filtra líneas con productos
    invoice_lines = move.invoice_line_ids.filtered(
        lambda l: l.product_id and l.display_type in (False, 'product')
    )
    
    # 2. Genera XML de cada línea
    for line in invoice_lines:
        barcode = line.product_id.barcode or '00000000000000'
        code = line.product_id.default_code or str(line.product_id.id)
        name = move.unescape_characters((line.product_id.name)[:35])
        quantity = line.get_quantity()
        price_gross = line.get_price_gross()
        # ... construye XML de lineItem
    
    # 3. Obtiene datos de encabezado
    entity_type = 'INVOICE' if move.move_type in ('out_invoice', 'in_invoice') else 'CREDIT_NOTE'
    amount_text = move._l10n_mx_edi_cfdi_amount_to_text()
    purchase_order = move.purchase_order_liv or 'N/A'
    buyer_gln = move.partner_id.global_localitation_number
    seller_gln = move.company_id.global_localitation_number
    
    # 4. Ensambla addenda completa
    addenda_xml = f'''<detallista:detallista ...>
        <detallista:requestForPaymentIdentification>...</detallista:requestForPaymentIdentification>
        <detallista:buyer>...</detallista:buyer>
        <detallista:seller>...</detallista:seller>
        {line_items_xml}
        <detallista:totalAmount>...</detallista:totalAmount>
    </detallista:detallista>'''
    
    return addenda_xml
Qué hace:
Filtra líneas: Solo productos (no secciones ni notas)
Itera líneas: Genera XML por cada producto
Obtiene datos: De factura, cliente, empresa
Construye XML: Usando f-strings con los datos
5. Métodos helper para cálculos
En las líneas (account_move.py:71-94)
def get_price_gross(self):
    """Precio unitario con impuestos"""
    taxes_line = self.tax_ids.flatten_taxes_hierarchy()
    transferred = taxes_line.filtered(lambda r: r.amount >= 0)
    price_net = self.price_unit * self.quantity
    price_gross = price_net
    if transferred:
        for tax in transferred:
            tasa = abs(tax.amount / 100.0) * 100
            price_gross += (price_net * tasa / 100)
    return "%.2f" % round(price_gross, 2)

def get_price_net(self):
    """Precio unitario sin impuestos"""
    return "%.2f" % round(self.price_unit * self.quantity, 2)

def get_gross_amount(self):
    """Total línea con impuestos"""
    return "%.2f" % round(self.price_total, 2)

def get_net_amount(self):
    """Total línea sin impuestos"""
    return "%.2f" % round(self.price_subtotal, 2)
Qué hace: Calcula los diferentes tipos de precios que Liverpool requiere:
gross = con impuestos
net = sin impuestos
Por unidad vs total de línea
6. Limpieza de caracteres
Método unescape (account_move.py:48-51)
def unescape_characters(self, value):
    """Remove accents and special characters from text."""
    import unidecode
    return unidecode.unidecode(value)
Qué hace: Convierte caracteres especiales:
"Chorizo Jalapeño" → "Chorizo Jalapeno"
"Niño" → "Nino"
Esto previene problemas de encoding en el XML.
7. Resultado final
Cuando timbras una factura para Liverpool, Odoo:
✅ Detecta que el cliente tiene generate_addenda_liverpool=True
✅ Auto-selecciona la addenda Liverpool
✅ Al generar el CFDI 4.0, ejecuta el template
✅ El template llama al método Python
✅ Python genera el XML completo de la addenda
✅ Se inserta dentro de <cfdi:Addenda> en el XML final
✅ Se timbra con el PAC incluyendo la addenda
Estructura de archivos
w_addenda_liverpool/
├── __manifest__.py                     # Definición del módulo
├── models/
│   ├── __init__.py                     # Imports
│   ├── account_move.py                 # Lógica de factura + helpers
│   ├── inherit_res_partner.py          # Campos de cliente
│   ├── inherit_res_company.py          # GLN de empresa
│   └── l10n_mx_edi_addenda.py         # Generador de XML
├── data/
│   └── addenda_liverpool_v40.xml      # Registro de addenda
└── views/
    ├── inherit_account_move_view.xml   # Campos en factura
    ├── inherit_res_partner_view.xml    # Campos en cliente
    └── inherit_res_company_view.xml    # GLN en empresa
Diferencia clave: v16 vs v18
v16: Usaba QWeb templates dentro del XML con t-foreach, t-if, etc. v18: QWeb NO se procesa en el campo arch, por eso:
Generamos todo el XML en Python
Usamos Markup() para marcarlo como seguro
El template solo llama al método Python
Esta es la razón principal de la complejidad de la migración. 🎯
