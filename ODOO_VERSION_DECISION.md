# Decisión de Versión de Odoo - Samper

**Fecha de Decisión:** Noviembre 6, 2025
**Decisión:** Permanecer en Odoo 18.0
**Próxima Revisión:** Abril 2026

---

## 📊 Resumen Ejecutivo

**QUEDARSE EN ODOO 18.0** hasta al menos Q2 2026.

---

## 🎯 Decisión

### ✅ Versión Actual: Odoo 18.0
- **Estado:** Producción estable
- **Soporte hasta:** Octubre 2027
- **Todos los módulos:** 100% compatibles y funcionando

### ❌ Migración a Odoo 19: NO RECOMENDADA (todavía)

---

## 🚫 Bloqueador Crítico

**Módulo `stock_no_negative` (OCA) NO disponible para Odoo 19**

- **Estado actual:** Disponible solo hasta v18.0
- **Última versión:** 18.0.1.0.2.6 (junio 2025)
- **Versión 19.0:** No existe (noviembre 2025)
- **Criticidad:** ALTA - Módulo esencial para control de inventario

**Sin este módulo:**
- ❌ No se puede prevenir stock negativo
- ❌ Riesgo de inconsistencias en inventario
- ❌ Problemas operacionales en producción

---

## 📅 Timeline de Migración

### Fase 1: Monitoreo (Nov 2025 - Mar 2026)
**Acciones:**
- 🔍 Monitorear OCA para lanzamiento de stock_no_negative v19
- 📊 Evaluar estabilidad de Odoo 19 en la comunidad
- 📝 Documentar reportes de early adopters

**Frecuencia de revisión:** Mensual

**Recursos a monitorear:**
- https://github.com/OCA/stock-logistics-workflow
- https://apps.odoo.com/apps/modules/browse?search=stock_no_negative
- Odoo Community Forums

---

### Fase 2: Re-evaluación (Abr 2026 - Sep 2026)
**Criterios para considerar migración:**
- ✅ stock_no_negative v19.0 disponible y probado
- ✅ Odoo 19 con 6+ meses en producción
- ✅ Reportes positivos de la comunidad
- ✅ OCA ha migrado módulos críticos
- ✅ Sin breaking changes no documentados

**Acción:** Decisión GO/NO-GO para migración

---

### Fase 3: Preparación (Oct 2026 - Mar 2027)
**Si decisión es GO:**
- 📋 Planificación detallada de migración
- 🧪 Setup ambiente de pruebas Odoo 19
- 👥 Capacitación del equipo
- 📦 Actualización de todos los módulos

**Ventana de migración recomendada:** Q4 2026 o Q1 2027

---

### Fase 4: Límite (2027)
**Deadline absoluto:** Octubre 2027
- Fin de soporte oficial de Odoo 18
- Migración debe completarse antes de esta fecha

---

## ⚖️ Análisis Costo-Beneficio

### Beneficios de Quedarse en v18
| Beneficio | Impacto |
|-----------|---------|
| ✅ Estabilidad probada | Alto |
| ✅ Todos los módulos disponibles | Crítico |
| ✅ Sin esfuerzo de migración | Medio |
| ✅ Equipo familiarizado | Medio |
| ✅ 2 años de soporte restante | Alto |

### Riesgos de Migrar a v19 Ahora
| Riesgo | Probabilidad | Impacto |
|--------|--------------|---------|
| ❌ Módulo crítico no disponible | 100% | Crítico |
| ❌ Bugs no descubiertos | Alta | Alto |
| ❌ Problemas en producción | Media | Alto |
| ❌ Tiempo de downtime | Alta | Medio |
| ❌ Curva de aprendizaje | Media | Bajo |

**Conclusión:** Riesgos superan significativamente los beneficios de migración temprana.

---

## 🔬 Compatibilidad de Módulos Samper con v19

**Análisis realizado:** Noviembre 2025

| Módulo | APIs Deprecadas | Esfuerzo Migración | Bloqueadores |
|--------|-----------------|-------------------|--------------|
| sam_formulas | ✅ Ninguna | Bajo | Ninguno |
| sam_inventario | ✅ Ninguna | Bajo | Ninguno |
| sam_reportes | ✅ Ninguna | Bajo | Ninguno |
| sam_contabilidad | ✅ Ninguna | Bajo | Ninguno |
| sam_procesos | ✅ Ninguna | Bajo | Ninguno |
| sam_views | ✅ Ninguna | Bajo | Ninguno |
| sam_quantity_validator | ✅ Ninguna | Bajo | Ninguno |
| w_addenda_liverpool | ✅ Ninguna | Bajo | Ninguno |
| addenda_comercial_mexicana | ✅ Ninguna | Bajo | Ninguno |
| **stock_no_negative** | ✅ Ninguna | N/A | **❌ No existe v19** |

**Resumen:**
- 9 de 10 módulos listos para v19
- 1 módulo BLOQUEADOR (stock_no_negative)
- Esfuerzo de migración estimado: 1-2 semanas (cuando esté disponible)

---

## 📋 Checklist de Monitoreo Trimestral

Revisar cada 3 meses (Enero, Abril, Julio, Octubre):

### 1. Disponibilidad de Módulos OCA
- [ ] Verificar rama `19.0` en https://github.com/OCA/stock-logistics-workflow
- [ ] Confirmar existencia de `stock_no_negative` en versión 19.0
- [ ] Revisar changelog y release notes del módulo
- [ ] Verificar issues y bugs reportados

### 2. Madurez de Odoo 19
- [ ] Revisar release notes de Odoo 19.0.x (bugfix releases)
- [ ] Buscar reportes de producción en foros
- [ ] Evaluar cantidad de bugs críticos reportados
- [ ] Confirmar estabilidad de módulos core (stock, mrp, account)

### 3. Comunidad y Ecosistema
- [ ] Revisar experiencias de early adopters
- [ ] Verificar migración de partners importantes
- [ ] Evaluar disponibilidad de otros módulos OCA necesarios
- [ ] Confirmar soporte de integraciones de terceros

### 4. Timing Interno
- [ ] Evaluar carga de trabajo del equipo
- [ ] Verificar ventanas de mantenimiento disponibles
- [ ] Confirmar presupuesto para migración
- [ ] Validar capacidad de testing

---

## 🎓 Breaking Changes de Odoo 19 (Referencia)

**Para cuando llegue el momento de migrar:**

### Métodos Deprecados
```python
# ❌ Deprecado / Removido
model.name_get()           # Usar: model.display_name
model.read_group()         # Usar: model._read_group()
model.fields_get_keys()    # Removido
model.get_xml_id()         # Deprecado
model._mapped_cache()      # Removido
```

### Atributos Removidos
```python
# ❌ Removido
class MyModel(models.Model):
    _sequence = 'my_seq'           # PostgreSQL maneja secuencias

field = fields.Char(
    column_format='...',           # Removido
    deprecated=True                # Removido
)

# ❌ Límites en relaciones
relation_ids = fields.One2many(..., limit=10)  # Atributo removido
```

### Controllers
```python
# ❌ Cambio requerido
@http.route('/api', type='json')      # Antes
@http.route('/api', type='jsonrpc')   # Ahora
```

**✅ BUENA NOTICIA:** Ningún módulo de Samper usa estos APIs deprecados.

---

## 📞 Contactos

**Responsable técnico:** vbueno
**Última actualización:** Noviembre 6, 2025
**Próxima revisión:** Abril 2026

---

## 📚 Referencias

- **OCA Repository:** https://github.com/OCA/stock-logistics-workflow
- **Odoo 18 Docs:** https://www.odoo.com/documentation/18.0/
- **Odoo 19 Docs:** https://www.odoo.com/documentation/19.0/
- **Odoo 19 Changelog:** https://www.odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html
- **Community Forum:** https://www.odoo.com/forum

---

## 🔄 Historial de Revisiones

| Fecha | Decisión | Razón |
|-------|----------|-------|
| Nov 2025 | Quedarse en v18 | stock_no_negative no disponible para v19 |
| Abr 2026 | *Pendiente* | Re-evaluación programada |
| Jul 2026 | *Pendiente* | Revisión trimestral |
| Oct 2026 | *Pendiente* | Revisión trimestral |

---

**⚠️ RECORDATORIO FINAL:** NO iniciar migración a Odoo 19 hasta que stock_no_negative esté disponible, probado, y estable en versión 19.0.
