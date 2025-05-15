/** @odoo-module */

odoo.define('sam_reportes.formulas_costo', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');

    var FormulasCostoFormController = FormController.extend({
        /**
         * @override
         */
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            
            // Verificar si estamos en el wizard de fórmulas de costo
            if (this.modelName === 'wizard.formulas.costo') {
                var self = this;
                
                // Sobrescribir el manejador del botón de impresión
                this.$buttons.on('click', 'button.o_form_button_imprime_formula_costo', function () {
                    // Ejecutar la acción original
                    self._superButtons.apply(self, arguments);
                    
                    // Recargar el wizard después de un pequeño retraso
                    setTimeout(function() {
                        self.reload({
                            noAlert: true,
                            reload: true
                        });
                    }, 1000);
                });
            }
        }
    });

    var FormulasCostoFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: FormulasCostoFormController,
        }),
    });

    viewRegistry.add('formulas_costo_form', FormulasCostoFormView);
});
