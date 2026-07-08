/**
 * @file:    smriti_retail_os/public/js/smriti_form_renderer.js
 * @desc:    SMRITI Form Renderer — renders SmritiForm schemas into DOM containers.
 *           Reads the JSON schema produced by SmritiForm.schema() (via smriti.api.schema())
 *           and builds a fully-functional, platform-agnostic form in any DOM container.
 *
 *           Usage:
 *               // Render a form in a container div
 *               const form = await smriti.forms.render("Purchase", "#po-form-container");
 *               form.on("save", doc  => smriti.notify.success("Saved", `PO ${doc.name} saved.`));
 *               form.on("submit", doc => smriti.notify.success("Submitted", `PO ${doc.name} posted.`));
 *
 *               // Pre-fill an existing document
 *               const form = await smriti.forms.render("Purchase", "#po-form", { name: "PO-001" });
 *
 *               // Get current form data
 *               const data = form.getData();
 *
 *               // Validate without saving
 *               const result = form.validate();
 *
 *           Architecture:
 *               www/*.html  →  smriti.forms.render()  →  SmritiFormRenderer
 *                                    ↓
 *               smriti.api.schema(model) → server schema
 *               smriti.api.get(model, name) → existing document
 *               smriti.api.save(model, data) → save
 *               smriti.api.submit(model, name) → submit
 *
 * @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
 * @version: 1.0.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function (smriti) {
    'use strict';

    // ── SmritiFormRenderer ────────────────────────────────────────────────────

    class SmritiFormRenderer {
        /**
         * @param {object} schema       - Form schema from smriti.api.schema()
         * @param {HTMLElement} container - DOM container to render into
         * @param {object} [opts]
         * @param {string} [opts.name]  - Document name to load (edit mode)
         * @param {object} [opts.data]  - Pre-fill data for new document
         */
        constructor(schema, container, opts = {}) {
            this._schema    = schema;
            this._container = container;
            this._model     = schema.model;
            this._name      = opts.name || null;
            this._data      = Object.assign({}, opts.data || {});
            this._listeners = {};  // event → [callbacks]
            this._fieldEls  = {}; // fieldname → input element
            this._dirty     = false;
        }

        // ── Lifecycle ─────────────────────────────────────────────────────────

        async init() {
            if (this._name) {
                try {
                    this._data = await smriti.api.get(this._model, this._name);
                } catch (e) {
                    smriti.notify.error("Load Failed",
                        `Could not load ${this._schema.title} "${this._name}". ${e.message}`);
                }
            }
            this._render();
            this._bindEvents();
            return this;
        }

        // ── Rendering ─────────────────────────────────────────────────────────

        _render() {
            this._container.innerHTML = '';
            this._container.classList.add('smriti-form');

            const header = this._makeHeader();
            this._container.appendChild(header);

            const body = document.createElement('div');
            body.className = 'smriti-form-body';

            this._schema.fields.forEach(field => {
                if (field.type === 'SectionBreak') {
                    body.appendChild(this._makeSectionBreak(field));
                } else if (!field.hidden) {
                    body.appendChild(this._makeFieldRow(field));
                }
            });

            this._container.appendChild(body);
            this._container.appendChild(this._makeActionBar());
        }

        _makeHeader() {
            const el = document.createElement('div');
            el.className = 'smriti-form-header';
            el.innerHTML = `
                <h2 class="smriti-form-title">${this._escHtml(this._schema.title)}</h2>
                ${this._name ? `<span class="smriti-form-doc-name">${this._escHtml(this._name)}</span>` : '<span class="smriti-form-doc-name smriti-form-new-badge">New</span>'}
            `;
            return el;
        }

        _makeSectionBreak(field) {
            const el = document.createElement('div');
            el.className = 'smriti-form-section' + (field.collapsible ? ' smriti-collapsible' : '');
            el.innerHTML = `<h3 class="smriti-section-label">${this._escHtml(field.label)}</h3>`;
            if (field.collapsible) {
                el.querySelector('h3').addEventListener('click', () => {
                    el.classList.toggle('smriti-collapsed');
                });
            }
            return el;
        }

        _makeFieldRow(field) {
            const row = document.createElement('div');
            row.className = 'smriti-field-row';
            row.dataset.field = field.name;

            const label = document.createElement('label');
            label.className = 'smriti-field-label' + (field.required ? ' smriti-required' : '');
            label.setAttribute('for', `smriti-field-${field.name}`);
            label.textContent = field.label;

            const inputWrap = document.createElement('div');
            inputWrap.className = 'smriti-field-input-wrap';

            const input = this._makeInput(field);
            inputWrap.appendChild(input);

            if (field.help_text) {
                const hint = document.createElement('p');
                hint.className = 'smriti-field-hint';
                hint.textContent = field.help_text;
                inputWrap.appendChild(hint);
            }

            const errEl = document.createElement('p');
            errEl.className = 'smriti-field-error';
            errEl.setAttribute('aria-live', 'polite');
            inputWrap.appendChild(errEl);

            row.appendChild(label);
            row.appendChild(inputWrap);
            return row;
        }

        _makeInput(field) {
            let el;
            const val = this._data[field.name] ?? (field.default ?? '');

            switch (field.type) {
                case 'SelectField': {
                    el = document.createElement('select');
                    el.className = 'smriti-input smriti-select';
                    if (!field.required) {
                        const blank = document.createElement('option');
                        blank.value = '';
                        blank.textContent = '— Select —';
                        el.appendChild(blank);
                    }
                    (field.options || []).forEach(opt => {
                        const o = document.createElement('option');
                        o.value = opt;
                        o.textContent = opt;
                        if (opt === val) o.selected = true;
                        el.appendChild(o);
                    });
                    break;
                }
                case 'TextAreaField': {
                    el = document.createElement('textarea');
                    el.className = 'smriti-input smriti-textarea';
                    el.rows = field.rows || 4;
                    el.value = val;
                    break;
                }
                case 'CheckboxField': {
                    el = document.createElement('input');
                    el.type = 'checkbox';
                    el.className = 'smriti-input smriti-checkbox';
                    el.checked = !!val;
                    break;
                }
                case 'DateField':
                case 'DateTimeField': {
                    el = document.createElement('input');
                    el.type = field.type === 'DateField' ? 'date' : 'datetime-local';
                    el.className = 'smriti-input smriti-date';
                    el.value = val;
                    if (field.min_date) el.min = field.min_date;
                    if (field.max_date) el.max = field.max_date;
                    break;
                }
                case 'NumberField': {
                    el = document.createElement('input');
                    el.type = 'number';
                    el.className = 'smriti-input smriti-number';
                    el.value = val;
                    el.step = field.precision > 0 ? (1 / Math.pow(10, field.precision)).toString() : '1';
                    if (field.min_value != null) el.min = field.min_value;
                    if (field.max_value != null) el.max = field.max_value;
                    break;
                }
                case 'CurrencyField': {
                    el = document.createElement('input');
                    el.type = 'number';
                    el.className = 'smriti-input smriti-currency';
                    el.value = val;
                    el.step = '0.01';
                    if (field.min_value != null) el.min = field.min_value;
                    break;
                }
                case 'LookupField': {
                    // Renders as a searchable input with datalist + async lookup
                    const wrap = document.createElement('div');
                    wrap.className = 'smriti-lookup-wrap';
                    el = document.createElement('input');
                    el.type = 'text';
                    el.className = 'smriti-input smriti-lookup';
                    el.value = val;
                    el.setAttribute('autocomplete', 'off');
                    el.placeholder = `Search ${field.label}…`;

                    const list = document.createElement('datalist');
                    list.id = `smriti-list-${field.name}`;
                    el.setAttribute('list', list.id);

                    // Async lookup on input
                    el.addEventListener('input', this._debounce(async () => {
                        const q = el.value.trim();
                        if (q.length < 1) return;
                        try {
                            const results = await smriti.api.lookup(field.model, {
                                query: q,
                                display_field: field.display_field || 'name',
                                limit: 10
                            });
                            list.innerHTML = '';
                            results.forEach(r => {
                                const opt = document.createElement('option');
                                opt.value = r.value;
                                opt.label = r.label || r.value;
                                list.appendChild(opt);
                            });
                        } catch (_) { /* silently ignore lookup errors */ }
                    }, 300));

                    wrap.appendChild(el);
                    wrap.appendChild(list);
                    this._fieldEls[field.name] = el;
                    return wrap;
                }
                case 'TableField': {
                    // Minimal table renderer — shows row count + "Edit" link
                    el = document.createElement('div');
                    el.className = 'smriti-table-field';
                    const rows = Array.isArray(val) ? val : [];
                    el.innerHTML = `
                        <div class="smriti-table-summary">
                            <span>${rows.length} ${field.label || 'item'}${rows.length === 1 ? '' : 's'}</span>
                            <button type="button" class="smriti-btn smriti-btn-secondary smriti-table-edit-btn">Edit ${field.label}</button>
                        </div>
                    `;
                    el.querySelector('.smriti-table-edit-btn').addEventListener('click', () => {
                        this._emit('table:edit', { field: field.name, rows });
                    });
                    this._fieldEls[field.name] = el;
                    return el;
                }
                default: {
                    el = document.createElement('input');
                    el.type = 'text';
                    el.className = 'smriti-input smriti-text';
                    el.value = val;
                    if (field.max_length) el.maxLength = field.max_length;
                    if (field.placeholder) el.placeholder = field.placeholder;
                }
            }

            el.id = `smriti-field-${field.name}`;
            el.name = field.name;
            if (field.readonly) el.setAttribute('readonly', true);
            if (field.required) el.setAttribute('required', true);
            this._fieldEls[field.name] = el;
            return el;
        }

        _makeActionBar() {
            const bar = document.createElement('div');
            bar.className = 'smriti-form-actions';
            bar.innerHTML = `
                <button type="button" class="smriti-btn smriti-btn-primary" id="smriti-form-save-btn">Save</button>
                <button type="button" class="smriti-btn smriti-btn-success smriti-btn-submit" id="smriti-form-submit-btn" style="display:none">Submit</button>
                <button type="button" class="smriti-btn smriti-btn-secondary" id="smriti-form-cancel-btn">Cancel</button>
            `;
            return bar;
        }

        // ── Event Binding ─────────────────────────────────────────────────────

        _bindEvents() {
            // Input change → dirty flag + on_change delegation
            Object.entries(this._fieldEls).forEach(([name, el]) => {
                el.addEventListener('change', async (e) => {
                    this._dirty = true;
                    const value = el.type === 'checkbox' ? el.checked : el.value;
                    this._data[name] = value;
                    this._emit('change', { field: name, value, data: this._data });

                    // Ask server for dependent field updates
                    try {
                        const updates = await smriti.api.call(
                            'smriti_retail_os.core.api.on_change',
                            { model: this._model, field_name: name, value, data: this._data }
                        );
                        if (updates && typeof updates === 'object') {
                            Object.entries(updates).forEach(([f, v]) => {
                                this._data[f] = v;
                                if (this._fieldEls[f]) this._setInputValue(this._fieldEls[f], v);
                            });
                        }
                    } catch (_) { /* on_change is best-effort */ }
                });
            });

            // Save button
            const saveBtn = this._container.querySelector('#smriti-form-save-btn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => this.save());
            }

            // Submit button
            const submitBtn = this._container.querySelector('#smriti-form-submit-btn');
            if (submitBtn) {
                submitBtn.addEventListener('click', () => this.submit());
            }

            // Cancel
            const cancelBtn = this._container.querySelector('#smriti-form-cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => {
                    this._emit('cancel', {});
                });
            }
        }

        _setInputValue(el, value) {
            if (el.type === 'checkbox') el.checked = !!value;
            else el.value = value ?? '';
        }

        // ── Public API ────────────────────────────────────────────────────────

        getData() {
            const data = Object.assign({}, this._data);
            Object.entries(this._fieldEls).forEach(([name, el]) => {
                if (el.tagName === 'INPUT' && el.type === 'checkbox') {
                    data[name] = el.checked;
                } else if (el.value !== undefined) {
                    data[name] = el.value;
                }
            });
            return data;
        }

        validate() {
            const data = this.getData();
            const errors = {};
            let ok = true;

            this._schema.fields.forEach(field => {
                if (!field.name || field.hidden || field.type === 'SectionBreak') return;
                const val = data[field.name];
                if (field.required && (val === null || val === undefined || val === '')) {
                    errors[field.name] = [`${field.label} is required.`];
                    ok = false;
                }
                // Show field error in UI
                const row = this._container.querySelector(`[data-field="${field.name}"]`);
                if (row) {
                    const errEl = row.querySelector('.smriti-field-error');
                    if (errEl) errEl.textContent = errors[field.name]?.[0] || '';
                    row.classList.toggle('smriti-field-invalid', !!errors[field.name]);
                }
            });

            return { ok, errors };
        }

        async save() {
            const result = this.validate();
            if (!result.ok) {
                smriti.notify.error("Validation Failed",
                    "Please fill in all required fields before saving.");
                return;
            }
            const data = this.getData();
            const saveBtn = this._container.querySelector('#smriti-form-save-btn');
            try {
                if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = 'Saving…'; }
                const doc = await smriti.api.save(this._model, data);
                this._data = doc;
                this._name = doc.name;
                this._dirty = false;
                // Show submit button after successful save if applicable
                const submitBtn = this._container.querySelector('#smriti-form-submit-btn');
                if (submitBtn && doc.docstatus === 0) submitBtn.style.display = '';
                smriti.notify.success("Saved", `${this._schema.title} saved successfully.`);
                this._emit('save', doc);
            } catch (e) {
                smriti.notify.error("Save Failed", e.message);
            } finally {
                if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = 'Save'; }
            }
        }

        async submit() {
            if (!this._name) {
                smriti.notify.error("Cannot Submit", "Please save the document before submitting.");
                return;
            }
            const confirmed = await smriti.dialog.confirm(
                "Submit Document",
                `Are you sure you want to submit ${this._schema.title} "${this._name}"? This action cannot be undone.`
            );
            if (!confirmed) return;
            try {
                const doc = await smriti.api.submit(this._model, this._name);
                smriti.notify.success("Submitted", `${this._schema.title} submitted successfully.`);
                this._emit('submit', doc);
            } catch (e) {
                smriti.notify.error("Submit Failed", e.message);
            }
        }

        on(event, callback) {
            if (!this._listeners[event]) this._listeners[event] = [];
            this._listeners[event].push(callback);
            return this;
        }

        // ── Utilities ─────────────────────────────────────────────────────────

        _emit(event, data) {
            (this._listeners[event] || []).forEach(cb => {
                try { cb(data); } catch (_) {}
            });
        }

        _debounce(fn, ms) {
            let t;
            return function (...args) {
                clearTimeout(t);
                t = setTimeout(() => fn.apply(this, args), ms);
            };
        }

        _escHtml(str) {
            const d = document.createElement('div');
            d.textContent = str || '';
            return d.innerHTML;
        }
    }


    // ── smriti.forms namespace ────────────────────────────────────────────────

    smriti.forms = smriti.forms || {};

    /**
     * Render a SMRITI form in a DOM container.
     *
     * Usage:
     *   const form = await smriti.forms.render("Purchase", "#po-container");
     *   const form = await smriti.forms.render("Purchase", "#po-container", { name: "PO-001" });
     *   const form = await smriti.forms.render("Customer", document.getElementById("cust-form"));
     *
     * @param {string}            model      - SMRITI model name
     * @param {string|HTMLElement} container - CSS selector or DOM element
     * @param {object}            [opts]
     * @param {string}            [opts.name] - Document name to load (edit mode)
     * @param {object}            [opts.data] - Pre-fill data (new mode)
     * @returns {Promise<SmritiFormRenderer>}
     */
    smriti.forms.render = async function (model, container, opts = {}) {
        const el = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        if (!el) {
            smriti.notify.error("Form Error",
                `smriti.forms.render: container "${container}" not found in the DOM.`);
            throw new Error(`Container "${container}" not found.`);
        }

        // Show loading state
        el.innerHTML = '<div class="smriti-form-loading"><span class="smriti-spinner"></span> Loading form…</div>';

        try {
            const schema = await smriti.api.schema(model);
            const renderer = new SmritiFormRenderer(schema, el, opts);
            await renderer.init();
            return renderer;
        } catch (e) {
            el.innerHTML = `<div class="smriti-form-error">Failed to load form: ${e.message}</div>`;
            throw e;
        }
    };

    /**
     * Quick inline factory for registering form definitions by model name.
     * Useful for custom forms beyond the built-in retail presets.
     *
     * Usage:
     *   smriti.forms.register("WarehouseTransfer", schema);
     *   const form = await smriti.forms.render("WarehouseTransfer", "#wt-form");
     */
    const _registeredSchemas = {};

    smriti.forms.register = function (model, schema) {
        _registeredSchemas[model] = schema;
    };

    // Patch api.schema to check local registry first (for client-side-only forms)
    const _originalSchema = smriti.api.schema;
    smriti.api.schema = function (model) {
        if (_registeredSchemas[model]) {
            return Promise.resolve(_registeredSchemas[model]);
        }
        return _originalSchema.call(smriti.api, model);
    };

})(window.smriti);
