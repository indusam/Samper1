# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Odoo 18.0 custom modules repository for **Industrias Alimenticias SAM SA de CV (Samper)**, a food manufacturing company. The repository contains 10 custom modules that extend Odoo's manufacturing, inventory, accounting, and reporting capabilities with specialized functionality for food production, formula management, and Mexican retail integrations.

## 🎯 Odoo Version Strategy

### Current Version: **Odoo 18.0** (Stable, Recommended)

**Decision Date:** November 2025
**Status:** ✅ Active Production Version
**Support Until:** October 2027

### Why Odoo 18 (Not Odoo 19)?

**CRITICAL BLOCKER:** The required OCA module `stock_no_negative` is **NOT available** for Odoo 19.

**Decision Rationale:**
1. **Module Availability** - OCA stock_no_negative only exists up to v18.0 (as of November 2025)
2. **Version Maturity** - Odoo 19 was released September 2025 (only 2 months old)
3. **Stability** - Odoo 18 is mature, stable, and all dependencies are available
4. **Recent Migration** - All Samper modules were recently updated and tested for v18
5. **Support Timeline** - Odoo 18 has 2 years of remaining support (until Oct 2027)

### Migration Timeline to Odoo 19

**Short Term (Nov 2025 - Mar 2026):**
- ✅ Remain on Odoo 18.0
- 🔍 Monitor OCA repository for stock_no_negative v19 release
- 📊 Track Odoo 19 stability reports from early adopters

**Medium Term (Apr 2026 - Sep 2026):**
- 🔄 Re-evaluate migration when:
  - `stock_no_negative` v19.0 is available and tested
  - Odoo 19 has 6+ months of production maturity
  - OCA has migrated majority of critical modules
  - Community reports positive experiences

**Long Term (2026-2027):**
- 📅 Plan migration to Odoo 19 before October 2027 (v18 end-of-support)
- ⏰ Recommended migration window: Q4 2026 or Q1 2027

### Monitoring Checklist

Check these resources quarterly to assess migration readiness:

- [ ] **OCA Repository:** https://github.com/OCA/stock-logistics-workflow
  - Look for `19.0` branch
  - Verify `stock_no_negative` module exists and is stable
- [ ] **Odoo Apps Store:** https://apps.odoo.com/apps/modules/browse?search=stock_no_negative
  - Check for 19.0 version
- [ ] **Community Forums:** Search for Odoo 19 migration experiences
- [ ] **Release Notes:** Review Odoo 19.x bugfix updates

**⚠️ DO NOT migrate to Odoo 19 until stock_no_negative is available. This module is critical for Samper's inventory control.**

### Odoo 19 Breaking Changes (For Future Reference)

When the time comes to migrate, be aware of these confirmed breaking changes:

**Deprecated Methods:**
- `model.name_get()` → Use `model.display_name` field instead
- `model.read_group()` → Use `model._read_group()` or `model.formatted_read_group()`
- `model.fields_get_keys()` → Removed
- `model.get_xml_id()` → Deprecated
- `model._mapped_cache()` → Removed

**Removed Attributes:**
- `Field.column_format` → Removed
- `Field.deprecated` → Removed
- `Model._sequence` → Removed (PostgreSQL handles sequences automatically)
- `One2many/Many2many limit=` → Removed

**Controller Changes:**
- `@http.route(..., type='json')` → Change to `type='jsonrpc'`

**Good News:** As of November 2025, Samper modules **do not use any** of these deprecated APIs, so migration should be straightforward once stock_no_negative is available.

## Development Environment

### Module Installation/Update
```bash
# Install a module (from Odoo root directory)
odoo-bin -c /path/to/config.conf -d database_name -i module_name

# Update a module after code changes
odoo-bin -c /path/to/config.conf -d database_name -u module_name

# Update multiple modules
odoo-bin -c /path/to/config.conf -d database_name -u sam_formulas,sam_inventario,sam_quantity_validator

# Start Odoo server with modules path
odoo-bin -c /path/to/config.conf --addons-path=/path/to/odoo/addons,/path/to/Samper1
```

### Running Tests
```bash
# Run tests for a specific module
odoo-bin -c /path/to/config.conf -d test_database --test-enable --stop-after-init -i stock_no_negative

# Run tests for an already installed module
odoo-bin -c /path/to/config.conf -d test_database --test-enable --stop-after-init -u stock_no_negative

# Run specific test class
odoo-bin -c /path/to/config.conf -d test_database --test-enable --test-tags /stock_no_negative
```

### Debugging
```bash
# Run Odoo with debug logging
odoo-bin -c /path/to/config.conf --log-level=debug

# Run with specific module debug
odoo-bin -c /path/to/config.conf --log-handler=odoo.addons.sam_formulas:DEBUG
```

## Architecture Overview

### Module Structure
All modules follow standard Odoo structure:
```
module_name/
├── __init__.py                 # Imports for models, wizards, etc.
├── __manifest__.py             # Module metadata, dependencies, data files
├── models/                     # Model extensions and new models
│   ├── __init__.py
│   └── *.py
├── views/                      # XML view definitions
│   └── *.xml
├── wizards/                    # Transient models for user interactions
│   ├── __init__.py
│   ├── *.py
│   └── *_view.xml
├── security/
│   └── ir.model.access.csv     # Access control rules
├── data/                       # Optional: data files
└── tests/                      # Optional: unit tests
    ├── __init__.py
    └── test_*.py
```

### Core Modules

**Manufacturing & Production:**
- **sam_quantity_validator** - Validates quantities across all models, sets values <0.0001 to 0, includes post-install hook for data cleanup
- **sam_formulas** - Formula/BOM management with limiting ingredients, nutritional calculations, intermediates/packaging tracking
- **sam_inventario** - Inventory extensions with waste tracking, origin stock display

**Control & Validation:**
- **stock_no_negative** - Prevents negative stock with granular control (product/category/location levels)
- **sam_procesos** - Purchase order validation against supplier price lists

**Reporting & UI:**
- **sam_reportes** - Custom reports (nutritional labels, formulas, costs, balances)
- **sam_views** - View customizations and field additions
- **sam_contabilidad** - Accounting customizations and PDF management

**Integrations:**
- **addenda_comercial_mexicana** - Comercial Mexicana retail addenda
- **w_addenda_liverpool** - Liverpool store integration and addenda

### Important Note: stock_no_negative Module

**CRITICAL:** The `stock_no_negative` module is a **REQUIRED** OCA (Odoo Community Association) module, not a temporary solution.

**Why it's necessary:**
- Odoo 18 does **NOT** have native functionality to prevent negative stock
- By design, Odoo allows negative inventory to reveal underlying problems
- There is **NO** built-in configuration in `Inventory > Settings` to disable negative stock

**Module Details:**
- **Source:** OCA stock-logistics-workflow repository
- **Version:** 18.0.1.0.0 (actively maintained for Odoo 18)
- **Repository:** https://github.com/OCA/stock-logistics-workflow
- **Odoo Apps Store:** https://apps.odoo.com/apps/modules/18.0/stock_no_negative

**Why Samper uses this module:**
- Provides granular control at three levels: product, category, and location
- Only blocks negative stock in `internal` and `transit` locations
- Excludes service and consumable products
- Essential for manufacturing inventory control

**Do NOT remove this module** - it's the industry-standard solution for preventing negative stock in Odoo 18. Any documentation suggesting migration to "native Odoo 18 functionality" is incorrect, as no such functionality exists.

### Key Architectural Patterns

#### 1. Model Inheritance
Always use `_inherit` to extend existing Odoo models:
```python
class StockMove(models.Model):
    _inherit = 'stock.move'

    x_custom_field = fields.Float(string="Custom Field")
```

#### 2. Custom Field Naming
All custom fields MUST use `x_` prefix:
- Prevents conflicts with core Odoo fields
- Makes customizations easily identifiable
- Examples: `x_porcentaje`, `x_merma_pct`, `x_exis_origen`

#### 3. Precision Requirements
Food manufacturing requires high precision:
```python
# Formula percentages - 6 decimal places
x_porcentaje = fields.Float(digits=(3, 6))

# Quantities - 4 decimal places
product_qty = fields.Float(digits=(12, 4))

# Limiting ingredient calculations - 6 decimal places
x_cantidad_il = fields.Float(digits=(12, 6))
```

#### 4. Validation Pattern
Implement validation in `create` and `write` methods:
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        vals = self._validate_quantity_fields(vals)
    return super().create(vals_list)

def write(self, vals):
    vals = self._validate_quantity_fields(vals)
    return super().write(vals)
```

#### 5. View Inheritance
Extend views using XPath positioning:
```xml
<record id="view_move_tree_inherit_sam" model="ir.ui.view">
    <field name="name">stock.move.tree.inherit.sam</field>
    <field name="model">stock.move</field>
    <field name="inherit_id" ref="stock.view_move_tree"/>
    <field name="arch" type="xml">
        <field name="product_id" position="after">
            <field name="x_custom_field" optional="show"/>
        </field>
    </field>
</record>
```

**View Attribute Notes:**
- `optional="show"` - Visible by default, user can hide
- `optional="hide"` - Hidden by default, user can show
- No attribute - Always visible, cannot be hidden

#### 6. Wizards for User Interactions
Use TransientModels for temporary data capture:
```python
class MyWizard(models.TransientModel):
    _name = 'wizard.my_wizard'
    _description = 'My Wizard'

    field1 = fields.Char(required=True)

    def action_apply(self):
        self.ensure_one()
        # Perform operations
        return {'type': 'ir.actions.act_window_close'}
```

### Critical Data Flows

#### Formula-to-Production Flow
1. **Formula Definition** (`sam_formulas`)
   - `mrp.bom` + `mrp.bom.line` define formulas
   - One ingredient marked as "limiting ingredient" (`x_ingrediente_limitante`)
   - All other quantities calculated proportionally based on limiting ingredient
   - Nutritional values computed from ingredient percentages

2. **Production Order** (`mrp.production`)
   - Generates `stock.move` records for components
   - Quantities validated by `sam_quantity_validator`

3. **Stock Movement** (`stock.move`)
   - Extended with `x_exis_origen` (shows available stock)
   - Extended with `x_merma_pct` (waste percentage)
   - Validated to 4 decimal places

4. **Inventory Update** (`stock.quant`)
   - Negative stock check via `stock_no_negative`
   - Quantity validation via `sam_quantity_validator`

#### Purchase Order Validation Flow
1. User enters purchase order line (`sam_procesos`)
2. `@api.onchange` validates product exists in supplier price list
3. Auto-updates `price_unit` if mismatch found
4. Shows warning if product not found for supplier

### Commonly Extended Models

- **stock.move** - Extended by: sam_quantity_validator, sam_inventario
- **mrp.production** - Extended by: sam_quantity_validator
- **mrp.bom / mrp.bom.line** - Extended by: sam_formulas
- **stock.quant** - Extended by: sam_quantity_validator, sam_formulas, stock_no_negative
- **product.template** - Extended by: sam_formulas, stock_no_negative
- **account.move** - Extended by: sam_contabilidad, addenda modules

## Important Technical Details

### Post-Install Hooks
`sam_quantity_validator` uses a post-install hook to clean existing data:
```python
# In __manifest__.py
'post_init_hook': 'post_init_hook'

# In hooks.py
def post_init_hook(cr, registry):
    # Corrects quantities <0.0001 to 0 across all models
```

This is critical when installing the module on existing databases.

### Quantity Validation Threshold
The threshold of **0.0001** is used consistently across `sam_quantity_validator` to handle floating-point precision issues. Any quantity with absolute value < 0.0001 is set to 0.

### Negative Stock Control
`stock_no_negative` provides three-tier control:
1. Product level (`product.template.allow_negative_stock`)
2. Category level (`product.category.allow_negative_stock`)
3. Location level (`stock.location.allow_negative_stock`)

All three must allow negative stock for it to be permitted.

### Context Usage
Use context to pass state and skip validations:
```python
# Skip specific validations
record.with_context(skip_consumption=True).button_mark_done()

# Pass default values to forms
action['context'] = {'default_product_id': product.id}
```

### Translation Pattern
Wrap all user-facing strings with `_()`:
```python
from odoo import _

raise ValidationError(_("El producto debe tener al menos Kgs/Unidad o Unidad/Pieza"))
```

### Security Model
Every new model requires access rules in `security/ir.model.access.csv`:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,access_model_user,model_my_model,mrp.group_mrp_user,1,1,1,1
access_model_manager,access_model_manager,model_my_model,mrp.group_mrp_manager,1,1,1,1
```

Typically define access for both User and Manager groups from relevant core module.

### Logging
Use consistent logging pattern:
```python
import logging
_logger = logging.getLogger(__name__)

_logger.info("Operation completed: %d records processed", count)
_logger.warning("Price mismatch detected for product: %s", product.name)
_logger.error("Failed to process record: %s", error)
```

## Common Development Tasks

### Adding a New Field to Existing Model
1. Create/edit model file in `models/`
2. Add field with `x_` prefix
3. Update `__manifest__.py` to include view file
4. Create/edit view file in `views/` to display field
5. Update module with `-u module_name`

### Creating a New Model
1. Define model in `models/` with appropriate `_name` and `_description`
2. Add to `models/__init__.py`
3. Create access rules in `security/ir.model.access.csv`
4. Create views in `views/`
5. Update `__manifest__.py` data list
6. Install/update module

### Adding Computed Fields
```python
@api.depends('field1', 'field2')
def _compute_field3(self):
    for record in self:
        record.field3 = record.field1 + record.field2
```

Computed fields recalculate automatically when dependencies change.

### Adding Constraints
```python
@api.constrains('field1', 'field2')
def _check_fields(self):
    for record in self:
        if record.field1 > record.field2:
            raise ValidationError(_("Field1 cannot exceed Field2"))
```

### Adding Onchange Methods
```python
@api.onchange('product_id')
def onchange_product_id(self):
    if self.product_id:
        self.price = self.product_id.list_price
```

Onchange methods provide real-time UI updates.

## Module Dependencies

All custom modules are independent - they depend only on core Odoo modules, not on each other. Key dependencies:

- `base` - All modules
- `stock` - sam_quantity_validator, stock_no_negative, sam_inventario, sam_formulas
- `mrp` - sam_quantity_validator, sam_formulas, sam_inventario
- `account` - sam_contabilidad, addenda modules
- `purchase` - sam_procesos

**Special Note:** `stock_no_negative` is an OCA (Odoo Community Association) module from the stock-logistics-workflow repository. While located in this repository, it's maintained by the OCA community and should be treated as a stable, production-ready dependency.

## Testing Best Practices

See `stock_no_negative/tests/test_stock_no_negative.py` for reference implementation:

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestMyModule(TransactionCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up shared test data

    def setUp(self):
        super().setUp()
        # Set up per-test data

    def test_feature_name(self):
        """Test description."""
        # Arrange
        # Act
        # Assert
        self.assertEqual(expected, actual)
```

## File Path Conventions

When referencing code locations:
- Models: `module_name/models/model_name.py:line_number`
- Views: `module_name/views/view_name.xml:line_number`
- Wizards: `module_name/wizards/wizard_name.py:line_number`

## Company Information

- **Company**: Industrias Alimenticias SAM SA de CV (Samper)
- **Website**: https://www.samper.mx
- **Industry**: Food Manufacturing
- **Odoo Version**: 18.0
- **License**: AGPL-3 / LGPL-3 (varies by module)

## Important Warnings

### 🚨 DO NOT Migrate to Odoo 19 (Yet)

**CRITICAL:** As of November 2025, migration to Odoo 19 is **BLOCKED**.

**Reason:** The OCA `stock_no_negative` module (critical for Samper) does NOT exist for Odoo 19.

**What happens if you ignore this warning:**
- Samper will lose the ability to prevent negative stock
- Inventory control will be compromised
- Production operations may be blocked or create data inconsistencies

**When can we migrate to Odoo 19?**
- Earliest: Q2 2026 (April-June) - when stock_no_negative v19 becomes available
- Recommended: Q4 2026 / Q1 2027 - after Odoo 19 has matured
- Latest: Before October 2027 - when Odoo 18 support ends

**Monitoring:** Check the OCA repository quarterly for stock_no_negative v19 availability:
https://github.com/OCA/stock-logistics-workflow

See the "Odoo Version Strategy" section at the top of this document for detailed timeline and decision rationale.

---

### ⚠️ Obsolete Files

The following files may exist in parent directories but contain **INCORRECT** information:

**`../uninstall_stock_no_negative.py`** - OBSOLETE SCRIPT
- Claims Odoo 18 has "native functionality" for preventing negative stock
- This is **FALSE** - Odoo 18 has NO such native feature
- The script was likely created based on a misunderstanding
- **DO NOT** use this script to uninstall `stock_no_negative`
- The `stock_no_negative` module is **REQUIRED** and should remain installed

**Why the confusion?**
Odoo intentionally allows negative stock by design to reveal inventory problems. Some developers mistakenly believed Odoo 18 would add native controls, but this never materialized. The OCA `stock_no_negative` module remains the industry-standard solution.

**If you need to prevent negative stock in Odoo 18 or 19, you MUST use the `stock_no_negative` module or implement custom constraints. There is no native alternative in either version.**
