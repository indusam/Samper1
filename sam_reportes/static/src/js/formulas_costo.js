odoo.define('sam_reportes.formulas_costo', function (require) {
    "use strict";

    var FormView = require('web.FormView');
    var FormController = require('web.FormController');
    var view_registry = require('web.view_registry');

    // Crear un controlador personalizado para el wizard
    var FormulasCostoFormController = FormController.extend({
        events: _.extend({}, FormController.prototype.events, {
            'click .o_form_button_imprime_formula_costo': '_onImprimeButtonClick',
        }),

        // Sobrescribir el método init para capturar el nombre del modelo
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.modelName = model;
        },

        // Manejador del evento click del botón de impresión
        _onImprimeButtonClick: function (ev) {
            var self = this;
            
            // Primero ejecutar la acción original
            this._super.apply(this, arguments);
            
            // Luego, después de un pequeño retraso, recargar el wizard
            setTimeout(function() {
                self.reload();
            }, 1000);
        },
    });

    // Crear una vista personalizada que use nuestro controlador
    var FormulasCostoFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: FormulasCostoFormController,
        }),
    });

    // Registrar la vista personalizada
    view_registry.add('formulas_costo_form', FormulasCostoFormView);

    // Devolver las clases para que estén disponibles si se necesitan
    return {
        FormulasCostoFormController: FormulasCostoFormController,
        FormulasCostoFormView: FormulasCostoFormView
    };
});
