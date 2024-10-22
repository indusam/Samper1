
/** @odoo-module **/

import { KanbanRecord } from 'web.KanbanRecord';
import { session } from 'web.session';

class CustomKanbanRecord extends KanbanRecord {
    events = {
        ...super.events,
        'click .on_preview_ms': '_onPreviewMSAttachment',
        'click .on_preview_google': '_onPreviewGoogleAttachment',
    };

    attachmentUrl() {
        return session.url('/web/content', {
            id: this.recordData.id,
            download: true,
        });
    }

    async _generateAccessToken() {
        const access_token = await this.rpc({
            model: 'ir.attachment',
            method: 'generate_access_token',
            args: [[this.recordData.id]],
        });
        return access_token;
    }

    async _onPreviewMSAttachment(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        let odoo_url = this.attachmentUrl();
        if (this.recordData.type !== 'url' && !this.recordData.public) {
            const access_token = await this._generateAccessToken();
            odoo_url += '&access_token=' + access_token;
        }

        const url = 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(odoo_url);
        window.open(this.recordData.type === 'url' ? this.recordData.url : url, '_blank');
    }

    async _onPreviewGoogleAttachment(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        let odoo_url = this.attachmentUrl();
        if (this.recordData.type !== 'url' && !this.recordData.public) {
            const access_token = await this._generateAccessToken();
            odoo_url += '&access_token=' + access_token;
        }

        const url = 'https://docs.google.com/viewer?url=' + encodeURIComponent(odoo_url);
        window.open(this.recordData.type === 'url' ? this.recordData.url : url, '_blank');
    }
}

export default CustomKanbanRecord;

