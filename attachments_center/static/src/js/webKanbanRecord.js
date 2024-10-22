
/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";

patch(KanbanRecord.prototype, 'attachments_center.webKanbanRecord', {
    setup() {
        this._super(...arguments);
    },

    // Añadimos eventos adicionales para los botones de previsualización
    events: {
        ...KanbanRecord.prototype.events,
        'click .on_preview_ms': '_onPreviewMSAttachment',
        'click .on_preview_google': '_onPreviewGoogleAttachment',
    },

    // Generar la URL del adjunto
    attachmentUrl() {
        return session.url('/web/content', {
            id: this.record.data.id,
            download: true,
        });
    },

    // Generar un token de acceso para los adjuntos privados
    async _generateAccessToken() {
        const access_token = await this.rpc({
            model: 'ir.attachment',
            method: 'generate_access_token',
            args: [
                [this.record.data.id]
            ],
        });
        return access_token;
    },

    // Previsualizar adjuntos de Microsoft Office
    async _onPreviewMSAttachment(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        let odoo_url = this.attachmentUrl();
        if (this.record.data.type !== 'url' && !this.record.data.public) {
            const access_token = await this._generateAccessToken();
            odoo_url += '&access_token=' + access_token;
        }

        let url = 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(odoo_url);
        if (this.record.data.type === 'url') {
            url = this.record.data.url;
        }

        window.open(url, '_blank');
    },

    // Previsualizar adjuntos de Google Docs
    async _onPreviewGoogleAttachment(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        let odoo_url = this.attachmentUrl();
        if (this.record.data.type !== 'url' && !this.record.data.public) {
            const access_token = await this._generateAccessToken();
            odoo_url += '&access_token=' + access_token;
        }

        let url = 'https://docs.google.com/viewer?url=' + encodeURIComponent(odoo_url);
        if (this.record.data.type === 'url') {
            url = this.record.data.url;
        }

        window.open(url, '_blank');
    },
});
