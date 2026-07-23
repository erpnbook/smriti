/**
 * @file:    public/js/ui/dialog.js
 * @desc:    SMRITI dialog component for popup confirmations.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.Dialog = class {
    constructor(options = {}) {
        this.title     = options.title     || 'Confirm Action';
        this.content   = options.content   || '';
        this.onConfirm = options.onConfirm || null;
        this.onCancel  = options.onCancel  || null;
        this.confirmLabel = options.confirmLabel || 'Confirm';
        this.cancelLabel  = options.cancelLabel  || 'Cancel';
        this.id = 'smriti-dialog-' + Math.floor(Math.random() * 1000000);
        this._init();
    }

    _init() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-backdrop';
        this.overlay.id = this.id;

        this.overlay.innerHTML = `
            <div class="modal" onclick="event.stopPropagation()" style="max-width:440px;">
                <div class="modal-header">
                    <h3 style="margin:0; font-size:1rem;">${this.title}</h3>
                    <button class="modal-close" id="${this.id}-btn-x" style="font-size:22px;">&times;</button>
                </div>
                <div style="padding: 8px 0 20px 0; color: var(--smriti-text-muted, #9ca3af); line-height:1.6; font-size:14px;">
                    ${this.content}
                </div>
                <div style="display:flex; justify-content:flex-end; gap:10px;">
                    <button id="${this.id}-btn-cancel"
                        style="padding:8px 18px; border-radius:6px; border:1px solid var(--smriti-card-border);
                               background:transparent; color:var(--smriti-text-muted); cursor:pointer; font-size:13px;">
                        ${this.cancelLabel}
                    </button>
                    <button id="${this.id}-btn-confirm"
                        style="padding:8px 18px; border-radius:6px; border:none;
                               background:#ef4444; color:#fff; cursor:pointer; font-weight:700; font-size:13px;">
                        ${this.confirmLabel}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);

        // Use requestAnimationFrame so the browser paints the initial state before adding 'open'
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                this.overlay.classList.add('open');
            });
        });

        // Close on backdrop click
        this.overlay.addEventListener('click', () => this.cancel());

        // Button bindings
        document.getElementById(`${this.id}-btn-x`).addEventListener('click',      () => this.cancel());
        document.getElementById(`${this.id}-btn-cancel`).addEventListener('click',  () => this.cancel());
        document.getElementById(`${this.id}-btn-confirm`).addEventListener('click', () => this.confirm());
    }

    confirm() {
        if (typeof this.onConfirm === 'function') this.onConfirm();
        this.close();
    }

    cancel() {
        if (typeof this.onCancel === 'function') this.onCancel();
        this.close();
    }

    close() {
        this.overlay.classList.remove('open');
        setTimeout(() => {
            if (this.overlay && this.overlay.parentNode) {
                this.overlay.parentNode.removeChild(this.overlay);
            }
        }, 250);
    }
};
