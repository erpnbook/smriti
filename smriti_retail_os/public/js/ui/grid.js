/**
 * @file:    public/js/ui/grid.js
 * @desc:    SMRITI Grid Component - Handles list displays, formatting, actions, and row selection.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.Grid = class {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`SMRITI Grid: Container #${containerId} not found.`);
            return;
        }
        this.columns           = options.columns || [];
        this.dataSource        = options.dataSource || null;
        this.actions           = options.actions || [];
        this.onRowClick        = options.onRowClick || null;
        this.contextObject     = options.contextObject || null;
        this.contextModule     = options.contextModule || null;
        this.selectable        = options.selectable !== false; // default ON
        this.onSelectionChange = options.onSelectionChange || null;
        this.data              = [];
        this.raw_data          = [];
        this._selectedKeys     = new Set();
        this.init();
    }

    // ─── Column count helper ───────────────────────────────────────────────────
    get _colCount() {
        return this.columns.length
            + (this.selectable ? 1 : 0)
            + (this.actions.length ? 1 : 0);
    }

    // ─── Initialise ────────────────────────────────────────────────────────────
    init() {
        this.container.innerHTML = `
            <div class="smriti-grid-wrapper">
                <table class="smriti-table">
                    <thead>
                        <tr id="grid-header-row"></tr>
                        <tr id="grid-filter-row"></tr>
                    </thead>
                    <tbody id="grid-tbody">
                        <tr><td colspan="${this._colCount}" style="text-align:center; padding:40px 0;">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        `;
        this.renderHeaders();
        this.renderFilters();
        this.refresh();
    }

    // ─── Headers ───────────────────────────────────────────────────────────────
    renderHeaders() {
        const headerRow = this.container.querySelector('#grid-header-row');
        let html = '';

        if (this.selectable) {
            html += `<th style="width:40px; text-align:center; padding:8px 6px;">
                <input type="checkbox" id="grid-chk-select-all" title="Select / Deselect All"
                    style="cursor:pointer; width:15px; height:15px; accent-color:var(--smriti-color-brand-primary);">
            </th>`;
        }

        html += this.columns.map(col => `
            <th style="width: ${col.width || 'auto'}; text-align: ${col.align || 'left'};">
                ${col.label}
            </th>
        `).join('');

        if (this.actions.length) {
            html += `<th style="width:100px; text-align:center;">Actions</th>`;
        }

        headerRow.innerHTML = html;

        if (this.selectable) {
            const chkAll = headerRow.querySelector('#grid-chk-select-all');
            if (chkAll) {
                chkAll.addEventListener('change', () => this.selectAll(chkAll.checked));
            }
        }
    }

    // ─── Column filters ────────────────────────────────────────────────────────
    renderFilters() {
        const filterRow = this.container.querySelector('#grid-filter-row');
        if (!filterRow) return;

        let html = '';
        if (this.selectable) {
            html += `<th style="padding:6px 8px; width:40px;"></th>`;
        }

        html += this.columns.map((col, index) => {
            const align = col.align === 'right'  ? 'text-align:right;'
                        : col.align === 'center' ? 'text-align:center;'
                        : 'text-align:left;';
            return `
                <th style="padding:6px 8px; width:${col.width || 'auto'}; ${align}">
                    <input type="text" class="smriti-grid-filter-input"
                        data-col-index="${index}" data-field="${col.field}"
                        placeholder="Filter..."
                        style="width:100%; padding:4px 8px; font-size:11px;
                               border:1px solid var(--smriti-card-border);
                               background:var(--smriti-bg-dark, rgba(0,0,0,0.2));
                               color:var(--smriti-text); border-radius:var(--radius-sm, 4px); outline:none;">
                </th>
            `;
        }).join('');

        if (this.actions.length) {
            html += `<th></th>`;
        }

        filterRow.innerHTML = html;
        filterRow.querySelectorAll('.smriti-grid-filter-input').forEach(input => {
            input.addEventListener('input', () => this.applyColumnFilters());
        });
    }

    // ─── Data fetch ────────────────────────────────────────────────────────────
    async refresh() {
        const tbody = this.container.querySelector('#grid-tbody');
        if (!this.dataSource) return;
        try {
            tbody.innerHTML = `<tr><td colspan="${this._colCount}" style="text-align:center; padding:40px 0;">
                <div class="loading-spinner"></div> Loading records...</td></tr>`;
            const fetched = await this.dataSource();
            this.raw_data = fetched || [];
            this._selectedKeys.clear();
            this._notifySelection();
            this.applyColumnFilters();
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="${this._colCount}" style="text-align:center; padding:40px 0;
                color:var(--smriti-color-brand-light);">Error: ${e.message}</td></tr>`;
            SMRITI.toast.error('Failed to load grid: ' + e.message);
        }
    }

    // ─── Column filter logic ───────────────────────────────────────────────────
    applyColumnFilters() {
        const inputs = this.container.querySelectorAll('.smriti-grid-filter-input');
        let filtered = [...this.raw_data];

        inputs.forEach(input => {
            const field = input.getAttribute('data-field');
            const query = input.value.toLowerCase().trim();
            if (query) {
                filtered = filtered.filter(row => {
                    const val = row[field];
                    if (val === undefined || val === null) return false;
                    return String(val).toLowerCase().includes(query);
                });
            }
        });

        this.data = filtered;
        this.renderRows();
    }

    // ─── Row rendering ─────────────────────────────────────────────────────────
    renderRows() {
        const tbody = this.container.querySelector('#grid-tbody');
        if (!this.data || !this.data.length) {
            tbody.innerHTML = `<tr><td colspan="${this._colCount}"
                style="text-align:center; padding:40px 0; color:var(--text-muted);">No records found.</td></tr>`;
            this._syncSelectAllCheckbox();
            return;
        }

        tbody.innerHTML = this.data.map((row, rowIndex) => {
            const contextObj    = this.contextObject || '';
            const contextId     = row.name || row.id || row.item_code || row.customer_name || row.supplier_name || '';
            const contextState  = row.status || row.workflow_state || '';
            const contextModule = this.contextModule || '';
            const isChecked     = this._selectedKeys.has(contextId);

            let rowHtml = `<tr class="grid-row${isChecked ? ' grid-row-selected' : ''}" data-index="${rowIndex}"`;
            if (contextObj) {
                rowHtml += ` data-smriti-context-object="${contextObj}"`;
                rowHtml += ` data-smriti-context-id="${contextId}"`;
                if (contextState)  rowHtml += ` data-smriti-context-state="${contextState}"`;
                if (contextModule) rowHtml += ` data-smriti-context-module="${contextModule}"`;
                if (row.stock_qty !== undefined)          rowHtml += ` data-smriti-context-val-stock_qty="${row.stock_qty}"`;
                if (row.reorder_level !== undefined)      rowHtml += ` data-smriti-context-val-reorder_level="${row.reorder_level}"`;
                if (row.outstanding_amount !== undefined) rowHtml += ` data-smriti-context-val-outstanding_amount="${row.outstanding_amount}"`;
            }
            rowHtml += `>`;

            // ── Checkbox cell ──────────────────────────────────────────────────
            if (this.selectable) {
                rowHtml += `<td style="text-align:center; padding:6px;" onclick="event.stopPropagation()">
                    <input type="checkbox" class="grid-row-chk"
                        data-key="${contextId}" data-index="${rowIndex}"
                        ${isChecked ? 'checked' : ''}
                        style="cursor:pointer; width:15px; height:15px; accent-color:var(--smriti-color-brand-primary);">
                </td>`;
            }

            // ── Data cells ────────────────────────────────────────────────────
            this.columns.forEach(col => {
                let val = (row[col.field] === undefined || row[col.field] === null) ? '' : row[col.field];
                if (typeof col.formatter === 'function') {
                    val = col.formatter(val, row);
                } else if (col.formatter === 'currency') {
                    val = `Rs. ${parseFloat(val || 0).toFixed(2)}`;
                } else if (col.formatter === 'percent') {
                    val = `${val}%`;
                }
                let style = `text-align: ${col.align || 'left'};`;
                if (col.bold) style += ' font-weight:600; color:var(--text);';
                rowHtml += `<td style="${style}">${val}</td>`;
            });

            // ── Action buttons ────────────────────────────────────────────────
            if (this.actions.length) {
                rowHtml += `<td style="text-align:center; padding:4px 6px;"><div style="display:flex; justify-content:center; gap:6px; align-items:center;">`;
                this.actions.forEach(act => {
                    rowHtml += `<button class="grid-action-btn" data-action="${act.id}" data-index="${rowIndex}" title="${act.label}"
                        style="display:inline-flex; align-items:center; justify-content:center; cursor:pointer;
                               background:transparent; border:1px solid var(--smriti-card-border);
                               border-radius:4px; padding:4px 6px; color:var(--smriti-text-muted);
                               transition:all 0.15s ease; pointer-events:all; z-index:2;">
                        <span class="material-symbols-outlined" style="font-size:16px; pointer-events:none;">${act.icon}</span>
                    </button>`;
                });
                rowHtml += `</div></td>`;
            }

            rowHtml += `</tr>`;
            return rowHtml;
        }).join('');

        // ── Row click listener ────────────────────────────────────────────────
        tbody.querySelectorAll('.grid-row').forEach(tr => {
            tr.addEventListener('click', e => {
                if (e.target.closest('.grid-action-btn') || e.target.closest('.grid-row-chk')) return;
                const idx = parseInt(tr.getAttribute('data-index'), 10);
                if (this.onRowClick) this.onRowClick(this.data[idx]);
            });
        });

        // ── Row checkbox change ───────────────────────────────────────────────
        tbody.querySelectorAll('.grid-row-chk').forEach(chk => {
            chk.addEventListener('change', () => {
                const key = chk.getAttribute('data-key');
                if (chk.checked) {
                    this._selectedKeys.add(key);
                } else {
                    this._selectedKeys.delete(key);
                }
                const tr = chk.closest('tr');
                if (tr) tr.classList.toggle('grid-row-selected', chk.checked);
                this._syncSelectAllCheckbox();
                this._notifySelection();
            });
        });

        // ── Action button listeners ───────────────────────────────────────────
        tbody.querySelectorAll('.grid-action-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.stopPropagation(); // prevent row-click from firing
                const actionId = btn.getAttribute('data-action');
                const idx      = parseInt(btn.getAttribute('data-index'), 10);
                const act      = this.actions.find(a => a.id === actionId);
                if (act && typeof act.callback === 'function') act.callback(this.data[idx]);
            });
        });

        this._syncSelectAllCheckbox();
    }

    // ─── Public selection API ──────────────────────────────────────────────────
    selectAll(checked) {
        this.data.forEach(row => {
            const key = row.name || row.id || row.item_code || '';
            if (key) checked ? this._selectedKeys.add(key) : this._selectedKeys.delete(key);
        });
        this.container.querySelectorAll('.grid-row-chk').forEach(chk => {
            chk.checked = checked;
            const tr = chk.closest('tr');
            if (tr) tr.classList.toggle('grid-row-selected', checked);
        });
        this._syncSelectAllCheckbox();
        this._notifySelection();
    }

    getSelectedKeys() {
        return [...this._selectedKeys];
    }

    getSelectedRows() {
        return this.data.filter(row => {
            const key = row.name || row.id || row.item_code || '';
            return this._selectedKeys.has(key);
        });
    }

    getSelectedCount() {
        return this._selectedKeys.size;
    }

    clearSelection() {
        this._selectedKeys.clear();
        this.container.querySelectorAll('.grid-row-chk').forEach(chk => {
            chk.checked = false;
            const tr = chk.closest('tr');
            if (tr) tr.classList.remove('grid-row-selected');
        });
        this._syncSelectAllCheckbox();
        this._notifySelection();
    }

    // ─── Private helpers ───────────────────────────────────────────────────────
    _syncSelectAllCheckbox() {
        const chkAll = this.container.querySelector('#grid-chk-select-all');
        if (!chkAll) return;
        const total    = this.data.length;
        const selected = this.data.filter(r => this._selectedKeys.has(r.name || r.id || r.item_code || '')).length;
        chkAll.checked       = total > 0 && selected === total;
        chkAll.indeterminate = selected > 0 && selected < total;
    }

    _notifySelection() {
        if (typeof this.onSelectionChange === 'function') {
            this.onSelectionChange(this.getSelectedKeys(), this.getSelectedRows());
        }
    }

    setData(newData) {
        this.raw_data = newData || [];
        this.applyColumnFilters();
    }
};
