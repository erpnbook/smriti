/**
 * @file:    public/js/ui/dialog.js
 * @desc:    SMRITI dialog component for popup forms and confirmations.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.Dialog = class {
    constructor(options = {}) {
        this.title = options.title || "Confirm Action";
        this.content = options.content || "";
        this.onConfirm = options.onConfirm || null;
        this.onCancel = options.onCancel || null;
        this.id = options.id || "smriti-dialog-" + Math.floor(Math.random() * 1000000);
        this.init();
    }

    init() {
        // Create backdrop and dialog structure
        this.overlay = document.createElement("div");
        this.overlay.className = "modal-backdrop";
        this.overlay.id = this.id;
        
        this.overlay.innerHTML = `
            <div class="modal-card">
                <div class="modal-header">
                    <h3>${this.title}</h3>
                    <button class="modal-close-btn" onclick="document.getElementById('${this.id}').remove()">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
                <div class="modal-body">
                    ${this.content}
                </div>
                <div class="modal-footer" style="display:flex; justify-content:flex-end; gap:12px; margin-top:20px;">
                    <button class="btn-cancel" id="${this.id}-btn-cancel">Cancel</button>
                    <button class="btn-submit" id="${this.id}-btn-confirm">Confirm</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);

        // Bind events
        document.getElementById(`${this.id}-btn-cancel`).addEventListener("click", () => this.cancel());
        document.getElementById(`${this.id}-btn-confirm`).addEventListener("click", () => this.confirm());
        
        // Render opacity transition
        setTimeout(() => this.overlay.classList.add("show"), 50);
    }

    confirm() {
        if (this.onConfirm) this.onConfirm();
        this.close();
    }

    cancel() {
        if (this.onCancel) this.onCancel();
        this.close();
    }

    close() {
        this.overlay.classList.remove("show");
        setTimeout(() => this.overlay.remove(), 250);
    }
};
