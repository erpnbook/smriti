/**
 * @file:    public/js/ui/form.js
 * @desc:    SMRITI Form Engine - Metadata-driven CRUD form renderer.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.Form = class {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`SMRITI Form Engine: Container #${containerId} not found.`);
            return;
        }
        this.fields = options.fields || [];
        this.onSubmit = options.onSubmit || null;
        this.onCancel = options.onCancel || null;
        this.submitLabel = options.submitLabel || "Save Record";
        this.init();
    }

    init() {
        let fieldsHtml = this.fields.map(f => {
            let req = f.required ? ' <span style="color:var(--smriti-color-brand-light);">*</span>' : '';
            let placeholder = f.placeholder || '';
            let val = f.value || '';
            
            let inputHtml = "";
            if (f.type === "Select") {
                let options = (f.options || []).map(o => {
                    let selected = o.value === val ? "selected" : "";
                    return `<option value="${o.value}" ${selected}>${o.label}</option>`;
                }).join('');
                inputHtml = `<select class="form-input" id="field-${f.id}">${options}</select>`;
            } else if (f.type === "Number" || f.type === "Currency") {
                inputHtml = `<input type="number" class="form-input" id="field-${f.id}" value="${val}" placeholder="${placeholder}">`;
            } else {
                inputHtml = `<input type="text" class="form-input" id="field-${f.id}" value="${val}" placeholder="${placeholder}">`;
            }

            return `
                <div class="form-group">
                    <label class="form-label">${f.label}${req}</label>
                    ${inputHtml}
                </div>
            `;
        }).join('');

        this.container.innerHTML = `
            <div class="smriti-form-wrapper">
                ${fieldsHtml}
                <div class="form-actions" style="display:flex; gap:12px; margin-top:24px;">
                    <button class="btn-cancel" id="btn-form-cancel" style="flex:1;">Cancel</button>
                    <button class="btn-submit" id="btn-form-save" style="flex:2;">
                        <span class="material-symbols-outlined">save</span> ${this.submitLabel}
                    </button>
                </div>
            </div>
        `;

        this.container.querySelector("#btn-form-cancel").addEventListener("click", () => {
            if (this.onCancel) this.onCancel();
        });

        this.container.querySelector("#btn-form-save").addEventListener("click", () => this.submit());
    }

    getValues() {
        const values = {};
        this.fields.forEach(f => {
            const input = document.getElementById(`field-${f.id}`);
            if (input) {
                values[f.id] = input.value.trim();
            }
        });
        return values;
    }

    setValues(values) {
        this.fields.forEach(f => {
            const input = document.getElementById(`field-${f.id}`);
            if (input && values[f.id] !== undefined) {
                input.value = values[f.id];
            }
        });
    }

    validate() {
        let valid = true;
        this.fields.forEach(f => {
            const input = document.getElementById(`field-${f.id}`);
            if (f.required && input && !input.value.trim()) {
                input.style.borderColor = "var(--smriti-color-brand-light)";
                valid = false;
            } else if (input) {
                input.style.borderColor = "var(--smriti-color-border-default)";
            }
        });
        return valid;
    }

    async submit() {
        if (!this.validate()) {
            SMRITI.toast.error("Please fill in all mandatory fields.");
            return;
        }

        const values = this.getValues();
        const saveButton = this.container.querySelector("#btn-form-save");

        try {
            saveButton.disabled = true;
            saveButton.innerHTML = `<span class="material-symbols-outlined spinner">sync</span> Saving...`;

            if (this.onSubmit) {
                await this.onSubmit(values);
            }
        } catch (e) {
            SMRITI.toast.error(e.message);
        } finally {
            saveButton.disabled = false;
            saveButton.innerHTML = `<span class="material-symbols-outlined">save</span> ${this.submitLabel}`;
        }
    }
};
