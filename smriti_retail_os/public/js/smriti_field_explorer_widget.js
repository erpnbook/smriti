/**
 * @file: smriti_retail_os/public/js/smriti_field_explorer_widget.js
 * @description: SMRITI Universal Field Explorer — Embeddable Modal Widget.
 *               Any SMRITI page can open the Field Explorer as an in-page modal overlay
 *               without navigating away. The calling page stays active.
 *
 * @author: Jawahar R. Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-26
 * @version: 1.0.0
 * @license: MIT
 * @copyright: 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 *
 * Usage:
 *   // From barcode.html — PRN mapping row:
 *   smritiFieldExplorer.openModal({
 *       doctype: 'Item',
 *       mode: 'barcode',     // 'fields' | 'search' | 'barcode' | 'preview'
 *       query: 'barcode',
 *       onSelect: function(field) {
 *           // field = { field_id, label, fieldname, path, doctype, fieldtype }
 *           insertMappingField(activeRow, field.field_id || field.path);
 *       }
 *   });
 *
 *   // From reports.html — column picker:
 *   smritiFieldExplorer.openModal({
 *       doctype: 'POS Invoice',
 *       mode: 'fields',
 *       onSelect: function(field) {
 *           addReportColumn(field.fieldname, field.label, field.fieldtype);
 *       }
 *   });
 *
 *   // Open standalone in new tab:
 *   smritiFieldExplorer.openPage({ doctype: 'Item', mode: 'barcode' });
 */

(function (global) {
    'use strict';

    // ── Private State ────────────────────────────────────────────────────────
    let _modal = null;
    let _onSelect = null;
    let _fieldIdRegistry = null;
    let _registryLoaded = false;

    // ── CSS injection ─────────────────────────────────────────────────────────
    function _injectStyles() {
        if (document.getElementById('ufe-widget-styles')) return;
        const style = document.createElement('style');
        style.id = 'ufe-widget-styles';
        style.textContent = `
            #ufe-modal-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0,0,0,0.55);
                backdrop-filter: blur(4px);
                z-index: 99000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: ufe-fade-in 0.2s ease;
            }

            @keyframes ufe-fade-in {
                from { opacity: 0; }
                to   { opacity: 1; }
            }

            #ufe-modal {
                background: #fff;
                border-radius: 16px;
                box-shadow: 0 24px 64px rgba(26,43,92,0.22);
                width: 90vw;
                max-width: 900px;
                height: 80vh;
                max-height: 700px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                animation: ufe-slide-up 0.22s cubic-bezier(0.4, 0, 0.2, 1);
            }

            @keyframes ufe-slide-up {
                from { transform: translateY(20px); opacity: 0; }
                to   { transform: translateY(0);    opacity: 1; }
            }

            #ufe-modal-header {
                background: #1A2B5C;
                color: white;
                padding: 16px 24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-shrink: 0;
            }

            #ufe-modal-header h3 {
                font-size: 16px;
                font-weight: 800;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            #ufe-modal-header .ufe-badge {
                font-size: 10px;
                background: rgba(255,255,255,0.2);
                padding: 3px 8px;
                border-radius: 20px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }

            #ufe-close-btn {
                background: rgba(255,255,255,0.12);
                border: none;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }

            #ufe-close-btn:hover { background: rgba(255,255,255,0.25); }

            #ufe-modal-tabs {
                display: flex;
                gap: 2px;
                padding: 0 24px;
                background: #F8FAFC;
                border-bottom: 1px solid #E2E8F0;
                flex-shrink: 0;
            }

            .ufe-tab {
                padding: 10px 16px;
                font-size: 12px;
                font-weight: 600;
                color: #475569;
                cursor: pointer;
                border-bottom: 3px solid transparent;
                transition: all 0.2s;
                white-space: nowrap;
            }

            .ufe-tab:hover { color: #2563EB; background: #EFF6FF; border-radius: 6px 6px 0 0; }
            .ufe-tab.ufe-tab-active { color: #2563EB; border-bottom-color: #2563EB; }

            #ufe-toolbar {
                padding: 10px 16px;
                background: #F8FAFC;
                border-bottom: 1px solid #E2E8F0;
                display: flex;
                gap: 8px;
                align-items: center;
                flex-shrink: 0;
            }

            #ufe-search-input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                font-size: 13px;
                outline: none;
                transition: border-color 0.2s;
            }

            #ufe-search-input:focus { border-color: #2563EB; }

            #ufe-doctype-select {
                padding: 8px 12px;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                font-size: 13px;
                outline: none;
                background: white;
            }

            #ufe-modal-body {
                flex: 1;
                overflow-y: auto;
                padding: 12px 16px;
            }

            .ufe-field-row {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 9px 12px;
                border-radius: 8px;
                cursor: pointer;
                transition: background 0.15s;
                border: 1px solid transparent;
            }

            .ufe-field-row:hover {
                background: #EFF6FF;
                border-color: #BFDBFE;
            }

            .ufe-field-id {
                background: #1A2B5C;
                color: white;
                font-size: 9px;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: monospace;
                font-weight: 800;
                flex-shrink: 0;
            }

            .ufe-field-label {
                font-size: 13px;
                font-weight: 600;
                color: #0F172A;
            }

            .ufe-field-meta {
                font-size: 11px;
                color: #64748B;
                font-family: monospace;
            }

            .ufe-badge-custom {
                background: #D1FAE5;
                color: #065F46;
                font-size: 9px;
                padding: 1px 5px;
                border-radius: 4px;
                font-weight: 800;
            }

            .ufe-badge-type {
                background: #EFF6FF;
                color: #2563EB;
                font-size: 10px;
                padding: 2px 7px;
                border-radius: 4px;
                font-weight: 600;
            }

            .ufe-select-btn {
                margin-left: auto;
                background: #2563EB;
                color: white;
                border: none;
                padding: 5px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 700;
                cursor: pointer;
                white-space: nowrap;
                transition: background 0.2s;
            }

            .ufe-select-btn:hover { background: #1D4ED8; }

            .ufe-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 40px;
                color: #94A3B8;
                text-align: center;
            }

            .ufe-spinner {
                width: 24px;
                height: 24px;
                border: 3px solid #E2E8F0;
                border-top-color: #2563EB;
                border-radius: 50%;
                animation: ufe-spin 0.7s linear infinite;
            }

            @keyframes ufe-spin { to { transform: rotate(360deg); } }

            .ufe-footer {
                padding: 10px 16px;
                border-top: 1px solid #E2E8F0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 12px;
                color: #64748B;
                flex-shrink: 0;
                background: #F8FAFC;
            }

            .ufe-open-full-btn {
                background: none;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 12px;
                font-weight: 600;
                color: #475569;
                cursor: pointer;
                transition: all 0.2s;
            }

            .ufe-open-full-btn:hover { border-color: #2563EB; color: #2563EB; }
        `;
        document.head.appendChild(style);
    }

    // ── Modal Builder ─────────────────────────────────────────────────────────
    function _buildModal(options) {
        // Overlay
        const overlay = document.createElement('div');
        overlay.id = 'ufe-modal-overlay';
        overlay.onclick = (e) => { if (e.target === overlay) smritiFieldExplorer.closeModal(); };

        // Modal
        const modal = document.createElement('div');
        modal.id = 'ufe-modal';
        modal.innerHTML = `
            <div id="ufe-modal-header">
                <h3>
                    🔎 SMRITI Field Explorer
                    <span class="ufe-badge">FIELD DISCOVERY</span>
                </h3>
                <button id="ufe-close-btn" onclick="smritiFieldExplorer.closeModal()">✕</button>
            </div>

            <div id="ufe-modal-tabs">
                <div class="ufe-tab ufe-tab-active" data-ufe-tab="fields"   onclick="smritiFieldExplorer._switchTab('fields')">🔎 Fields</div>
                <div class="ufe-tab"                 data-ufe-tab="search"   onclick="smritiFieldExplorer._switchTab('search')">🔍 Search</div>
                <div class="ufe-tab"                 data-ufe-tab="barcode"  onclick="smritiFieldExplorer._switchTab('barcode')">📦 Barcode IDs</div>
                <div class="ufe-tab"                 data-ufe-tab="preview"  onclick="smritiFieldExplorer._switchTab('preview')">🖨 Preview</div>
            </div>

            <div id="ufe-toolbar">
                <select id="ufe-doctype-select" onchange="smritiFieldExplorer._onDtChange(this.value)"></select>
                <input type="text" id="ufe-search-input" placeholder="Search fields…"
                       oninput="smritiFieldExplorer._onSearch(this.value)">
            </div>

            <div id="ufe-modal-body">
                <div class="ufe-state"><div class="ufe-spinner"></div></div>
            </div>

            <div class="ufe-footer">
                <span>Click a field to select it</span>
                <button class="ufe-open-full-btn" onclick="smritiFieldExplorer.openPage()">
                    ↗ Open Full Explorer
                </button>
            </div>`;

        overlay.appendChild(modal);
        return overlay;
    }

    // ── Public API ─────────────────────────────────────────────────────────────
    const smritiFieldExplorer = {
        _currentTab: 'fields',
        _currentDoctype: 'Item',
        _searchTimer: null,

        /**
         * Open the Field Explorer as a modal overlay.
         * @param {Object} options
         * @param {string}   options.doctype   Pre-selected DocType
         * @param {string}   options.mode      'fields' | 'search' | 'barcode' | 'preview'
         * @param {string}   options.query     Pre-filled search term
         * @param {Function} options.onSelect  Callback when user selects a field
         *                                     Called with: { field_id, label, fieldname, path, doctype, fieldtype }
         */
        openModal(options) {
            _injectStyles();

            // Close any existing modal
            this.closeModal();

            options = options || {};
            _onSelect = options.onSelect || null;
            this._currentDoctype = options.doctype || 'Item';
            this._currentTab = options.mode || 'fields';

            _modal = _buildModal(options);
            document.body.appendChild(_modal);
            document.body.style.overflow = 'hidden';

            // Populate DocType selector with common retail types
            const dtSelect = document.getElementById('ufe-doctype-select');
            const commonTypes = [
                'Item', 'Customer', 'Supplier', 'Sales Invoice', 'POS Invoice',
                'Purchase Order', 'Purchase Receipt', 'Payment Entry',
                'Stock Entry', 'Delivery Note',
            ];
            commonTypes.forEach(dt => {
                const opt = document.createElement('option');
                opt.value = dt;
                opt.textContent = dt;
                if (dt === this._currentDoctype) opt.selected = true;
                dtSelect.appendChild(opt);
            });

            // Pre-fill search
            if (options.query) {
                document.getElementById('ufe-search-input').value = options.query;
            }

            // Switch to requested tab
            this._switchTab(this._currentTab);

            // Keyboard close
            document.addEventListener('keydown', this._handleEsc);
        },

        closeModal() {
            if (_modal && _modal.parentNode) {
                _modal.parentNode.removeChild(_modal);
            }
            _modal = null;
            document.body.style.overflow = '';
            document.removeEventListener('keydown', this._handleEsc);
        },

        _handleEsc(e) {
            if (e.key === 'Escape') smritiFieldExplorer.closeModal();
        },

        openPage(options) {
            options = options || {};
            const dt = options.doctype || this._currentDoctype || 'Item';
            const mode = options.mode || 'fields';
            window.open(`/smriti-field-explorer?doctype=${encodeURIComponent(dt)}&mode=${mode}`, '_blank');
        },

        _switchTab(tab) {
            this._currentTab = tab;
            document.querySelectorAll('.ufe-tab').forEach(el => {
                el.classList.toggle('ufe-tab-active', el.dataset.ufeTab === tab);
            });

            const query = document.getElementById('ufe-search-input')?.value || '';

            if (tab === 'fields') this._loadFields(query);
            else if (tab === 'search') this._loadSearch(query);
            else if (tab === 'barcode') this._loadBarcodeMode(query);
            else if (tab === 'preview') this._showPreviewHint();
        },

        _onDtChange(dt) {
            this._currentDoctype = dt;
            const tab = this._currentTab;
            if (tab === 'fields') this._loadFields('');
            else if (tab === 'barcode') this._loadBarcodeMode('');
        },

        _onSearch(val) {
            clearTimeout(this._searchTimer);
            this._searchTimer = setTimeout(() => {
                if (this._currentTab === 'fields') this._loadFields(val);
                else if (this._currentTab === 'search') this._loadSearch(val);
                else if (this._currentTab === 'barcode') this._loadBarcodeMode(val);
            }, 320);
        },

        _setBody(html) {
            const body = document.getElementById('ufe-modal-body');
            if (body) body.innerHTML = html;
        },

        _setLoading() {
            this._setBody('<div class="ufe-state"><div class="ufe-spinner"></div></div>');
        },

        async _loadFields(search) {
            const dt = this._currentDoctype;
            if (!dt) return;

            this._setLoading();

            try {
                const res = await frappe.call({
                    method: 'smriti_retail_os.api.field_explorer_api.get_doctype_fields',
                    args: { doctype: dt, search: search || null },
                    freeze: false,
                });

                const data = res.message || {};
                const body = document.getElementById('ufe-modal-body');
                if (!body) return;

                body.innerHTML = '';

                if (!data.sections || data.sections.length === 0) {
                    body.innerHTML = '<div class="ufe-state">No fields found.</div>';
                    return;
                }

                data.sections.forEach(section => {
                    const heading = document.createElement('div');
                    heading.style.cssText = 'font-size:11px;font-weight:700;text-transform:uppercase;color:#94A3B8;padding:10px 4px 4px;letter-spacing:0.7px;';
                    heading.textContent = section.section;
                    body.appendChild(heading);

                    (section.fields || []).forEach(f => {
                        const row = this._makeFieldRow(f, false);
                        body.appendChild(row);
                    });
                });

            } catch (e) {
                this._setBody(`<div class="ufe-state">Error loading fields.</div>`);
            }
        },

        async _loadSearch(query) {
            if (!query || query.length < 2) {
                this._setBody('<div class="ufe-state">Type at least 2 characters to search.</div>');
                return;
            }

            this._setLoading();

            try {
                const res = await frappe.call({
                    method: 'smriti_retail_os.api.field_explorer_api.search_fields',
                    args: { query: query },
                    freeze: false,
                });

                const results = res.message || [];
                const body = document.getElementById('ufe-modal-body');
                if (!body) return;

                body.innerHTML = '';

                if (results.length === 0) {
                    body.innerHTML = '<div class="ufe-state">No results found.</div>';
                    return;
                }

                results.forEach(f => {
                    const row = this._makeFieldRow(f, false);
                    body.appendChild(row);
                });

            } catch (e) {
                this._setBody('<div class="ufe-state">Search failed.</div>');
            }
        },

        async _loadBarcodeMode(search) {
            this._setLoading();

            try {
                // Use cached registry if available
                if (!_registryLoaded || !_fieldIdRegistry) {
                    const res = await frappe.call({
                        method: 'smriti_retail_os.api.field_explorer_api.get_field_id_registry',
                        args: { printable_only: true },
                        freeze: false,
                    });
                    _fieldIdRegistry = res.message || [];
                    _registryLoaded = true;
                }

                let fields = _fieldIdRegistry;
                if (search) {
                    const q = search.toLowerCase();
                    fields = fields.filter(f =>
                        f.label.toLowerCase().includes(q) ||
                        f.field_id.toLowerCase().includes(q) ||
                        f.fieldname.toLowerCase().includes(q)
                    );
                }

                const body = document.getElementById('ufe-modal-body');
                if (!body) return;

                body.innerHTML = '';

                if (fields.length === 0) {
                    body.innerHTML = '<div class="ufe-state">No printable fields found.</div>';
                    return;
                }

                const note = document.createElement('div');
                note.style.cssText = 'background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:8px 12px;font-size:12px;color:#1D4ED8;font-weight:600;margin-bottom:10px;';
                note.innerHTML = '📦 Selecting a field inserts its stable <strong>Field ID</strong> — not a raw path. Your label templates stay valid even if the schema changes.';
                body.appendChild(note);

                fields.forEach(f => {
                    const row = this._makeFieldRow(f, true);
                    body.appendChild(row);
                });

            } catch (e) {
                this._setBody('<div class="ufe-state">Failed to load Barcode Mode.</div>');
            }
        },

        _showPreviewHint() {
            this._setBody(`
                <div class="ufe-state" style="gap:12px;">
                    <div style="font-size:32px;">🖨</div>
                    <div style="font-size:14px;font-weight:700;color:#0F172A;">Label Preview</div>
                    <div style="font-size:13px;max-width:320px;">
                        Open the full Field Explorer to use Label Preview mode,
                        where you can paste field paths and verify values before printing.
                    </div>
                    <button class="ufe-open-full-btn" onclick="smritiFieldExplorer.openPage({mode:'preview'})" style="margin-top:8px;padding:8px 20px;font-size:13px;">
                        ↗ Open Label Preview
                    </button>
                </div>`);
        },

        _makeFieldRow(f, isBarcodeMode) {
            const row = document.createElement('div');
            row.className = 'ufe-field-row';

            const fieldId = f.field_id;
            const displayId = fieldId || null;
            const label = f.label || f.fieldname;
            const path = f.path || `${f.doctype}.${f.fieldname}`;

            row.innerHTML = `
                ${displayId ? `<span class="ufe-field-id">${_esc(displayId)}</span>` : ''}
                <div style="flex:1;min-width:0;">
                    <div class="ufe-field-label">
                        ${_esc(label)}
                        ${f.is_custom ? '<span class="ufe-badge-custom">C</span>' : ''}
                    </div>
                    <div class="ufe-field-meta">${_esc(isBarcodeMode ? path : (f.doctype ? `${f.doctype}.${f.fieldname}` : f.fieldname))}</div>
                </div>
                ${f.fieldtype ? `<span class="ufe-badge-type">${_esc(f.fieldtype)}</span>` : ''}
                ${_onSelect ? `<button class="ufe-select-btn" data-fid="${_esc(fieldId || '')}" data-path="${_esc(path)}" data-label="${_esc(label)}" data-fn="${_esc(f.fieldname)}" data-dt="${_esc(f.doctype || '')}" data-ft="${_esc(f.fieldtype || '')}">Select →</button>` : ''}`;

            // Bind select button
            const selectBtn = row.querySelector('.ufe-select-btn');
            if (selectBtn && _onSelect) {
                selectBtn.onclick = (e) => {
                    e.stopPropagation();
                    const field = {
                        field_id:  selectBtn.dataset.fid || null,
                        label:     selectBtn.dataset.label,
                        fieldname: selectBtn.dataset.fn,
                        path:      selectBtn.dataset.path,
                        doctype:   selectBtn.dataset.dt,
                        fieldtype: selectBtn.dataset.ft,
                    };
                    _onSelect(field);
                    smritiFieldExplorer.closeModal();
                };
            }

            return row;
        },
    };

    // ── Helper ────────────────────────────────────────────────────────────────
    function _esc(str) {
        if (str == null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // ── Expose to global ──────────────────────────────────────────────────────
    global.smritiFieldExplorer = smritiFieldExplorer;

})(window);
