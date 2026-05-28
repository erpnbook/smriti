/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_item_master/smriti_item_master.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

// ============================================================
//  SMRITI Item Master Import — Paste-from-Excel Grid
//  Shopper9-style: copy from Excel → paste → import
// ============================================================

frappe.pages['smriti-item-master'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Item Master Import',
        single_column: true
    });
    new SmritiItemMasterController(wrapper, page);
};

// ── Column definitions ────────────────────────────────────────────────────
const SIM_COLS = [
    { key: 'BARCODE NO',           label: 'Barcode',     width: '150px', required: true },
    { key: 'PRODUCT STYLE CODE',   label: 'Style/Article No', width: '150px', required: true },
    { key: 'ITEM DESCRIPTION',     label: 'Description', width: '220px', required: true },
    { key: 'BRAND NAME',           label: 'Brand',       width: '110px' },
    { key: 'COLOR',                label: 'Color',       width: '100px', required: true },
    { key: 'SIZE',                 label: 'Size',        width: '65px',  required: true },
    { key: 'PLANNED MRP',          label: 'MRP ₹',       width: '90px',  required: true, type: 'number' },
    { key: 'COST PRICE',           label: 'Cost ₹',      width: '90px',  type: 'number' },
    { key: 'PRODUCT TAX',          label: 'GST%',        width: '65px',  type: 'number', choices: ['', '0', '5', '12', '18', '28'] },
    { key: 'HSN CODE',             label: 'HSN Code',    width: '100px' },
    { key: 'GENDER',               label: 'Gender',      width: '90px',  choices: ['', 'MENS', 'LADIES', 'BOYS', 'GIRLS', 'UNISEX', 'KIDS'] },
    { key: 'VENDOR CODE',          label: 'Vendor/Supplier', width: '130px' },
    { key: 'PURCHASE CLASS',       label: 'Purch. Class', width: '110px',  choices: ['', 'FW', 'MFW', 'LFW', 'BFW', 'GFW', 'KFW', 'ASSTED', 'SPORTS', 'ACC', 'BAG', 'FORMAL', 'CASUAL'] },
    { key: 'DEPARTMENT',           label: 'Department',  width: '120px' },
    { key: 'MERCHANDISE CATEGORY', label: 'Merch. Cat.', width: '120px' },
    { key: 'Sub category',         label: 'Sub Category', width: '120px' },
    { key: 'HEELS',                label: 'Heels',       width: '90px' },
    { key: 'UPPER MATERIAL',       label: 'Upper Mat.',  width: '120px' },
    { key: 'OUTSOLE',              label: 'Outsole',     width: '100px' },
    { key: 'IMAGE LINK',           label: 'Image URL',   width: '130px' },
    { key: 'Product Tax Group',    label: 'Tax Group',   width: '120px' },
];

const REQUIRED_KEYS = SIM_COLS.filter(c => c.required).map(c => c.key);
const VALID_GST = new Set([0, 5, 12, 18, 28]);

// Fuzzy header match map (lowercase → canonical key)
const HEADER_ALIASES = {};
SIM_COLS.forEach(c => {
    HEADER_ALIASES[c.key.toLowerCase()] = c.key;
    HEADER_ALIASES[c.label.toLowerCase()] = c.key;
});
// Extra known aliases from Excel templates
const EXTRA_ALIASES = {
    'barcode': 'BARCODE NO', 'barcode no': 'BARCODE NO', 'barcode number': 'BARCODE NO',
    'style code': 'PRODUCT STYLE CODE', 'article': 'PRODUCT STYLE CODE', 'article no': 'PRODUCT STYLE CODE',
    'item description': 'ITEM DESCRIPTION', 'description': 'ITEM DESCRIPTION', 'name': 'ITEM DESCRIPTION',
    'brand': 'BRAND NAME', 'brand name': 'BRAND NAME',
    'mrp': 'PLANNED MRP', 'planned mrp': 'PLANNED MRP', 'selling price': 'PLANNED MRP',
    'cost': 'COST PRICE', 'cost price': 'COST PRICE', 'purchase price': 'COST PRICE',
    'gst': 'PRODUCT TAX', 'gst%': 'PRODUCT TAX', 'tax%': 'PRODUCT TAX',
    'hsn': 'HSN CODE', 'hsn code': 'HSN CODE',
    'dept': 'DEPARTMENT', 'department': 'DEPARTMENT',
    'vendor': 'VENDOR CODE', 'vendor code': 'VENDOR CODE', 'supplier': 'VENDOR CODE',
    'heels': 'HEELS', 'heel': 'HEELS', 'heel type': 'HEELS',
    'upper': 'UPPER MATERIAL', 'upper material': 'UPPER MATERIAL',
    'outsole': 'OUTSOLE', 'sole': 'OUTSOLE',
    'image': 'IMAGE LINK', 'image link': 'IMAGE LINK', 'image url': 'IMAGE LINK',
    'tax group': 'Product Tax Group', 'product tax group': 'Product Tax Group',
    'purchase class': 'PURCHASE CLASS', 'p class': 'PURCHASE CLASS',
    'merch category': 'MERCHANDISE CATEGORY', 'merchandise category': 'MERCHANDISE CATEGORY',
    'sub cat': 'Sub category', 'sub category': 'Sub category',
};
Object.assign(HEADER_ALIASES, EXTRA_ALIASES);

// ── Main Controller ───────────────────────────────────────────────────────
class SmritiItemMasterController {
    constructor(wrapper, page) {
        this.wrapper  = wrapper;
        this.page     = page;
        this.rows     = [];          // array of {data: {}, status, errors, warnings}
        this.col_map  = null;        // detected column mapping from paste header row
        this.importing = false;

        this._render_layout();
        this._bind_events();
    }

    // ── Layout ────────────────────────────────────────────────────────────
    _render_layout() {
        $(this.wrapper).find('.layout-main-section').addClass('sim-page');

        const html = `
<div class="sim-page-header">
  <h1>📋 Item Master Import <span class="sim-badge">SMRITI</span></h1>
  <div style="display:flex;gap:10px">
    <button class="sim-btn sim-btn-ghost" id="sim-download-tpl">⬇ Download Template</button>
    <button class="sim-btn sim-btn-ghost" id="sim-view-items">📦 View Items</button>
  </div>
</div>

<div class="sim-tabs">
  <div class="sim-tab active" data-tab="paste">📋 Paste from Excel</div>
  <div class="sim-tab" data-tab="upload">📂 Upload File</div>
  <div class="sim-tab" data-tab="manual">✏️ Manual Entry</div>
</div>

<!-- TAB: Paste from Excel -->
<div class="sim-panel active" id="sim-panel-paste">
  <div class="sim-paste-zone" id="sim-paste-zone" tabindex="0">
    <div class="pz-icon">📋</div>
    <div class="pz-title">Click here, then press Ctrl+V</div>
    <div class="pz-sub">Paste your Excel data (select rows including header row)</div>
    <div class="pz-hint">✦ First pasted row is treated as column headers — auto-matched</div>
    <textarea id="sim-paste-capture" aria-hidden="true"></textarea>
  </div>
  ${this._grid_html()}
</div>

<!-- TAB: Upload File -->
<div class="sim-panel" id="sim-panel-upload">
  <div class="sim-upload-zone" id="sim-upload-zone">
    <div class="uz-icon">📂</div>
    <div class="uz-title">Drag & drop your file here, or click to browse</div>
    <div class="uz-sub">Accepts .csv, .xlsx, .xls files</div>
    <input type="file" id="sim-file-input" accept=".csv,.xlsx,.xls" />
  </div>
  <button class="sim-btn sim-btn-ghost" id="sim-download-tpl2" style="margin-bottom:12px;">⬇ Download CSV Template</button>
  ${this._grid_html('upload')}
</div>

<!-- TAB: Manual Entry -->
<div class="sim-panel" id="sim-panel-manual">
  <p style="color:var(--sim-muted);font-size:0.83rem;margin-bottom:14px;">
    Add items one-by-one. Use Tab to move between cells. Same validation as paste mode.
  </p>
  ${this._grid_html('manual')}
</div>`;

        $(this.wrapper).find('.layout-main-section').html(html);
        this._render_grid_rows('paste');
        this._render_grid_rows('upload');
        this._render_grid_rows('manual');
    }

    _grid_html(suffix = 'paste') {
        return `
<div class="sim-stats" id="sim-stats-${suffix}">
  <span class="sim-stat valid"><span class="dot"></span><span class="cnt" id="cnt-valid-${suffix}">0</span> valid</span>
  <span class="sim-stat warn"> <span class="dot"></span><span class="cnt" id="cnt-warn-${suffix}">0</span> warnings</span>
  <span class="sim-stat err">  <span class="dot"></span><span class="cnt" id="cnt-err-${suffix}">0</span> errors</span>
  <div class="sim-stats-right">
    <button class="sim-btn sim-btn-danger sim-btn-clear" data-suffix="${suffix}">🗑 Clear</button>
    <button class="sim-btn sim-btn-ghost sim-btn-addrow" data-suffix="${suffix}">➕ Add Row</button>
  </div>
</div>
<div class="sim-grid-wrapper" id="sim-grid-wrapper-${suffix}">
  <table class="sim-grid" id="sim-grid-${suffix}">
    <thead><tr id="sim-grid-thead-${suffix}"></tr></thead>
    <tbody id="sim-grid-tbody-${suffix}">
      <tr><td colspan="${SIM_COLS.length + 2}" class="sim-empty-state">
        <div class="es-icon">📋</div>
        <div class="es-text">No data yet — paste from Excel, upload a file, or add rows manually</div>
      </td></tr>
    </tbody>
  </table>
</div>

<div class="sim-settings">
  <div class="sim-setting-group">
    <div class="sim-setting-label">On Duplicate Barcode</div>
    <select id="sim-dup-action-${suffix}" class="sim-dup-action">
      <option value="block" selected>🚫 Block (Hard Error)</option>
    </select>
  </div>
  <div class="sim-setting-group">
    <div class="sim-setting-label">Selling Price Source</div>
    <select id="sim-price-src-${suffix}">
      <option value="mrp" selected>Use Planned MRP (Standard Selling)</option>
    </select>
  </div>
</div>

<div class="sim-toolbar">
  <button class="sim-btn sim-btn-primary sim-btn-validate" data-suffix="${suffix}">🔍 Validate Rows</button>
  <button class="sim-btn sim-btn-success sim-btn-import" data-suffix="${suffix}" disabled>🚀 Import Valid Rows</button>
</div>

<div class="sim-progress-panel" id="sim-progress-${suffix}">
  <div class="sim-progress-label" id="sim-prog-label-${suffix}">Preparing import…</div>
  <div class="sim-progress-bar-wrap"><div class="sim-progress-bar" id="sim-prog-bar-${suffix}"></div></div>
  <div class="sim-result-summary" id="sim-result-${suffix}"></div>
  <div class="sim-err-detail" id="sim-err-detail-${suffix}">
    <table>
      <thead><tr><th>Row</th><th>Barcode</th><th>Style Code</th><th>Error</th></tr></thead>
      <tbody id="sim-err-tbody-${suffix}"></tbody>
    </table>
  </div>
</div>`;
    }

    _render_grid_header(suffix) {
        const $thead = $(`#sim-grid-thead-${suffix}`);
        $thead.empty();
        let html = '<th class="sim-rownum">#</th><th title="Row status">✓</th>';
        SIM_COLS.forEach(col => {
            const req = col.required ? ' required-col' : '';
            html += `<th class="${req}" style="min-width:${col.width}">
                       <abbr title="${col.key}">${col.label}${col.required ? ' *' : ''}</abbr>
                     </th>`;
        });
        html += '<th style="width:36px"></th>';
        $thead.html(html);
    }

    _render_grid_rows(suffix) {
        this._render_grid_header(suffix);
        const $tbody = $(`#sim-grid-tbody-${suffix}`);
        $tbody.empty();

        const rows = this._get_rows(suffix);

        if (!rows.length) {
            $tbody.html(`<tr><td colspan="${SIM_COLS.length + 3}" class="sim-empty-state">
              <div class="es-icon">📋</div>
              <div class="es-text">No data yet — ${suffix === 'paste' ? 'paste from Excel above' : suffix === 'upload' ? 'upload a file above' : 'click ➕ Add Row to start'}</div>
            </td></tr>`);
            return;
        }

        rows.forEach((row, idx) => {
            const statusClass = row.status === 'error' ? 'row-error' : row.status === 'warning' ? 'row-warn' : row.status === 'valid' ? 'row-valid' : '';
            const statusIcon  = row.status === 'error' ? '🔴' : row.status === 'warning' ? '🟡' : row.status === 'valid' ? '🟢' : '⬜';
            const allMsgs     = [...(row.errors || []), ...(row.warnings || [])];
            const tipHtml     = allMsgs.length ? `<span class="sim-err-tip">${allMsgs.join('<br>')}</span>` : '';

            let tds = `<td class="sim-rownum ${statusClass}">${tipHtml}${idx + 1}</td>`;
            tds += `<td class="sim-status-cell">${statusIcon}</td>`;

            SIM_COLS.forEach(col => {
                const val = row.data[col.key] || '';
                if (col.choices) {
                    let optionsHtml = col.choices.map(opt => {
                        const selected = String(opt).trim().toUpperCase() === String(val).trim().toUpperCase() ? 'selected' : '';
                        return `<option value="${_esc(opt)}" ${selected}>${_esc(opt)}</option>`;
                    }).join('');
                    tds += `<td><select class="sim-cell-input" 
                               data-suffix="${suffix}" data-row="${idx}" data-col="${col.key}">
                             ${optionsHtml}
                           </select></td>`;
                } else {
                    tds += `<td><input class="sim-cell-input" 
                               data-suffix="${suffix}" data-row="${idx}" data-col="${col.key}"
                               type="text" value="${_esc(val)}"
                               ${col.type === 'number' ? 'inputmode="decimal"' : ''}></td>`;
                }
            });

            tds += `<td><button class="sim-del-btn sim-btn-delrow" data-suffix="${suffix}" data-row="${idx}" title="Delete row">✕</button></td>`;
            $tbody.append(`<tr class="${statusClass}" id="sim-row-${suffix}-${idx}">${tds}</tr>`);
        });

        this._update_stats(suffix);
    }

    // ── Row store (separate per tab) ──────────────────────────────────────
    _get_rows(suffix) {
        this._rows = this._rows || {};
        if (!this._rows[suffix]) {
            this._rows[suffix] = [];
            if (suffix === 'manual') {
                for (let i = 0; i < 5; i++) {
                    this._rows[suffix].push({ data: {}, status: null, errors: [], warnings: [] });
                }
            }
        }
        return this._rows[suffix];
    }

    _set_rows(suffix, rows) {
        this._rows = this._rows || {};
        if (suffix === 'manual' && (!rows || rows.length === 0)) {
            rows = [];
            for (let i = 0; i < 5; i++) {
                rows.push({ data: {}, status: null, errors: [], warnings: [] });
            }
        }
        this._rows[suffix] = rows;
    }

    // ── Events ────────────────────────────────────────────────────────────
    _bind_events() {
        const self = this;

        // Tab switching
        $(this.wrapper).on('click', '.sim-tab', function () {
            $('.sim-tab').removeClass('active');
            $('.sim-panel').removeClass('active');
            $(this).addClass('active');
            $(`#sim-panel-${$(this).data('tab')}`).addClass('active');
        });

        // ── Paste zone activation ─────────────────────────────────────────
        $(this.wrapper).on('click', '#sim-paste-zone', function () {
            $(this).addClass('active');
            $('#sim-paste-capture').focus();
        });

        $(this.wrapper).on('paste', '#sim-paste-capture', function (e) {
            e.preventDefault();
            const text = (e.originalEvent.clipboardData || window.clipboardData).getData('text');
            $('#sim-paste-zone').removeClass('active');
            if (text) self._handle_paste(text, 'paste');
        });

        // ── Cell editing ──────────────────────────────────────────────────
        $(this.wrapper).on('change', '.sim-cell-input', function () {
            const suffix = $(this).data('suffix');
            const rowIdx = parseInt($(this).data('row'));
            const col    = $(this).data('col');
            const rows   = self._get_rows(suffix);
            if (rows[rowIdx]) {
                rows[rowIdx].data[col] = $(this).val();
                rows[rowIdx].status    = null;  // reset validation
            }
            self._update_stats(suffix);
        });

        // ── Keyboard nav inside grid ──────────────────────────────────────
        $(this.wrapper).on('keydown', '.sim-cell-input', function (e) {
            const $inputs = $(this).closest('table').find('.sim-cell-input');
            const idx     = $inputs.index(this);
            const colCount = SIM_COLS.length;
            if (e.key === 'Tab' || e.key === 'Enter') {
                e.preventDefault();
                $inputs.eq(idx + 1).focus().select();
            } else if (e.key === 'ArrowRight' && this.selectionStart === this.value.length) {
                $inputs.eq(idx + 1).focus().select();
            } else if (e.key === 'ArrowLeft' && this.selectionStart === 0) {
                $inputs.eq(idx - 1).focus().select();
            } else if (e.key === 'ArrowDown') {
                $inputs.eq(idx + colCount).focus().select();
            } else if (e.key === 'ArrowUp') {
                $inputs.eq(idx - colCount).focus().select();
            }
        });

        // ── Delete row ────────────────────────────────────────────────────
        $(this.wrapper).on('click', '.sim-btn-delrow', function () {
            const suffix = $(this).data('suffix');
            const idx    = parseInt($(this).data('row'));
            const rows   = self._get_rows(suffix);
            rows.splice(idx, 1);
            self._set_rows(suffix, rows);
            self._render_grid_rows(suffix);
        });

        // ── Add empty row ─────────────────────────────────────────────────
        $(this.wrapper).on('click', '.sim-btn-addrow', function () {
            const suffix = $(this).data('suffix');
            const rows   = self._get_rows(suffix);
            rows.push({ data: {}, status: null, errors: [], warnings: [] });
            self._set_rows(suffix, rows);
            self._render_grid_rows(suffix);
            // Focus first cell of new row
            setTimeout(() => {
                $(`#sim-grid-${suffix} .sim-cell-input`).last().closest('tr').find('.sim-cell-input').first().focus();
            }, 50);
        });

        // ── Clear ─────────────────────────────────────────────────────────
        $(this.wrapper).on('click', '.sim-btn-clear', function () {
            const suffix = $(this).data('suffix');
            if (!self._get_rows(suffix).length || confirm('Clear all rows?')) {
                self._set_rows(suffix, []);
                self._render_grid_rows(suffix);
                $(`#sim-progress-${suffix}`).removeClass('active');
            }
        });

        // ── Validate ──────────────────────────────────────────────────────
        $(this.wrapper).on('click', '.sim-btn-validate', async function () {
            const suffix = $(this).data('suffix');
            await self._validate_rows(suffix);
        });

        // ── Import ────────────────────────────────────────────────────────
        $(this.wrapper).on('click', '.sim-btn-import', async function () {
            if (self.importing) return;
            const suffix = $(this).data('suffix');
            await self._import_rows(suffix);
        });

        // ── File upload ───────────────────────────────────────────────────
        $(this.wrapper).on('click', '#sim-upload-zone', function (e) {
            if ($(e.target).is('#sim-file-input')) return;
            $('#sim-file-input').click();
        });
        $(this.wrapper).on('change', '#sim-file-input', function () {
            const file = this.files[0];
            if (file) self._handle_file_upload(file);
        });

        // Drag and drop
        const $uz = $(this.wrapper).find('#sim-upload-zone');
        $uz.on('dragover', e => { e.preventDefault(); $uz.addClass('dragover'); });
        $uz.on('dragleave', () => $uz.removeClass('dragover'));
        $uz.on('drop', e => {
            e.preventDefault();
            $uz.removeClass('dragover');
            const file = e.originalEvent.dataTransfer.files[0];
            if (file) self._handle_file_upload(file);
        });

        // ── Download template ─────────────────────────────────────────────
        $(this.wrapper).on('click', '#sim-download-tpl, #sim-download-tpl2', () => self._download_template());

        // ── View Items ───────────────────────────────────────────────────
        $(this.wrapper).on('click', '#sim-view-items', () => {
            frappe.set_route('List', 'Item');
        });
    }

    // ── Paste Handler ─────────────────────────────────────────────────────
    _handle_paste(text, suffix) {
        const lines = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').trim().split('\n');
        if (lines.length < 2) {
            frappe.show_alert({ message: 'Paste at least 2 rows (header + 1 data row)', indicator: 'orange' }, 4);
            return;
        }

        // Detect if first row looks like headers (contains known column names)
        const firstRow  = _parse_tsv_line(lines[0]);
        const colMap    = _auto_detect_columns(firstRow);
        const hasHeader = Object.keys(colMap).length > 0;

        const dataLines = hasHeader ? lines.slice(1) : lines;
        const startIdx  = this._get_rows(suffix).length;

        const newRows = dataLines
            .filter(l => l.trim())
            .map(line => {
                const cells = _parse_tsv_line(line);
                const data  = {};
                if (hasHeader) {
                    firstRow.forEach((hdr, i) => {
                        const canonical = colMap[i];
                        if (canonical) data[canonical] = cells[i] || '';
                    });
                } else {
                    // No header detected → map positionally
                    SIM_COLS.forEach((col, i) => { data[col.key] = cells[i] || ''; });
                }
                return { data, status: null, errors: [], warnings: [] };
            });

        const existing = this._get_rows(suffix);
        this._set_rows(suffix, [...existing, ...newRows]);
        this._render_grid_rows(suffix);

        frappe.show_alert({
            message: `✅ ${newRows.length} row${newRows.length > 1 ? 's' : ''} pasted — click Validate to check`,
            indicator: 'green'
        }, 4);
    }

    // ── Validate rows (calls backend) ─────────────────────────────────────
    async _validate_rows(suffix) {
        const rows = this._get_rows(suffix);
        if (!rows.length) {
            frappe.show_alert({ message: 'No rows to validate', indicator: 'orange' }, 3);
            return;
        }

        frappe.show_alert({ message: 'Validating…', indicator: 'blue' }, 2);

        const rowData = rows.map(r => r.data);

        try {
            const results = await frappe.call({
                method: 'smriti_retail_os.item_master_api.validate_import_rows',
                args: { rows_json: JSON.stringify(rowData) }
            });

            const validations = results.message || [];
            validations.forEach((v, i) => {
                if (rows[i]) {
                    rows[i].status   = v.status;
                    rows[i].errors   = v.errors;
                    rows[i].warnings = v.warnings;
                }
            });
            this._set_rows(suffix, rows);
            this._render_grid_rows(suffix);

            // Enable import button only if there are valid rows
            const validCount = rows.filter(r => r.status === 'valid').length;
            const warnCount  = rows.filter(r => r.status === 'warning').length;
            const errCount   = rows.filter(r => r.status === 'error').length;

            const hasImportable = validCount + warnCount > 0;
            $(`[data-suffix="${suffix}"].sim-btn-import`).prop('disabled', !hasImportable).text(
                `🚀 Import ${validCount + warnCount} Valid Row${(validCount + warnCount) !== 1 ? 's' : ''}`
            );

            frappe.show_alert({
                message: `Validation done — ${validCount} valid, ${warnCount} warnings, ${errCount} errors`,
                indicator: errCount > 0 ? (validCount > 0 ? 'orange' : 'red') : 'green'
            }, 5);

        } catch (err) {
            frappe.show_alert({ message: 'Validation failed: ' + (err.message || err), indicator: 'red' }, 6);
        }
    }

    // ── Import rows ───────────────────────────────────────────────────────
    async _import_rows(suffix) {
        const rows = this._get_rows(suffix);
        // Only send rows that are valid or have only warnings (errors are hard-blocked)
        const importable = rows.filter(r => r.status === 'valid' || r.status === 'warning');

        if (!importable.length) {
            frappe.show_alert({ message: 'No valid rows to import. Run Validate first.', indicator: 'orange' }, 4);
            return;
        }

        const $panel = $(`#sim-progress-${suffix}`);
        const $bar   = $(`#sim-prog-bar-${suffix}`);
        const $label = $(`#sim-prog-label-${suffix}`);
        const $res   = $(`#sim-result-${suffix}`);
        const $errDet = $(`#sim-err-detail-${suffix}`);
        const $errTbody = $(`#sim-err-tbody-${suffix}`);

        $panel.addClass('active');
        $res.empty();
        $errTbody.empty();
        $errDet.removeClass('active');
        $bar.css('width', '5%');
        $label.text(`Importing ${importable.length} rows…`);
        this.importing = true;
        $(`[data-suffix="${suffix}"].sim-btn-import`).prop('disabled', true);

        try {
            const result = await frappe.call({
                method: 'smriti_retail_os.item_master_api.import_item_master',
                args: { rows_json: JSON.stringify(importable.map(r => r.data)) }
            });

            $bar.css('width', '100%');

            const r = result.message || {};
            const created   = r.created          || 0;
            const dups      = r.duplicate_errors || [];
            const failed    = r.failed           || [];

            $label.text('Import complete');

            // Summary lines
            if (created > 0) {
                $res.append(`<div class="sim-result-line success">✅ ${created} item${created !== 1 ? 's' : ''} created / updated successfully</div>`);
            }
            if (dups.length) {
                $res.append(`<div class="sim-result-line warning">🚫 ${dups.length} row${dups.length !== 1 ? 's' : ''} rejected — duplicate barcode</div>`);
                dups.forEach(d => {
                    $errTbody.append(`<tr>
                      <td>${d.row}</td>
                      <td>${_esc(d.barcode)}</td>
                      <td>—</td>
                      <td class="err-msg">🚫 ${_esc(d.reason)}</td>
                    </tr>`);
                });
            }
            if (failed.length) {
                $res.append(`<div class="sim-result-line error">❌ ${failed.length} row${failed.length !== 1 ? 's' : ''} failed due to errors</div>`);
                failed.forEach(f => {
                    $errTbody.append(`<tr>
                      <td>${f.row}</td>
                      <td>${_esc(f.barcode)}</td>
                      <td>${_esc(f.style_code)}</td>
                      <td class="err-msg">❌ ${_esc((f.error || '').substring(0, 120))}</td>
                    </tr>`);
                });
            }

            if (dups.length || failed.length) $errDet.addClass('active');

            if (created > 0) {
                frappe.show_alert({ message: `✅ ${created} items created!`, indicator: 'green' }, 6);
            }

        } catch (err) {
            $bar.css('width', '100%').css('background', 'var(--sim-red)');
            $label.text('Import failed');
            $res.append(`<div class="sim-result-line error">❌ ${err.message || 'Unexpected error during import'}</div>`);
            frappe.show_alert({ message: 'Import error: ' + (err.message || err), indicator: 'red' }, 8);
        }

        this.importing = false;
        $(`[data-suffix="${suffix}"].sim-btn-import`).prop('disabled', false);
    }

    // ── File upload handler ───────────────────────────────────────────────
    _handle_file_upload(file) {
        const suffix = 'upload';
        const ext    = file.name.split('.').pop().toLowerCase();

        if (ext === 'csv') {
            const reader = new FileReader();
            reader.onload = (e) => this._handle_paste(e.target.result, suffix);
            reader.readAsText(file, 'utf-8');
        } else {
            // For .xlsx/.xls we show a message to save as CSV first
            frappe.show_alert({
                message: 'For .xlsx files, please save as CSV in Excel first (File → Save As → CSV UTF-8), then upload.',
                indicator: 'orange'
            }, 8);
        }
    }

    // ── Download template ─────────────────────────────────────────────────
    _download_template() {
        const headers  = SIM_COLS.map(c => `"${c.key}"`).join(',');
        const sample1  = '"2000000001","D-20001-SND","BELLARINA ASHA CASUAL","ASSIA","PEACH","8","29","18","5","64159090","LADIES","SUP001","FW","LADIES FTW","FLAT","BASIC","CASUAL","CLOTH","EVA","","12"';
        const sample2  = '"2000000002","D-20001-SND","BELLARINA ASHA CASUAL","ASSIA","BLACK","8","29","18","5","64159090","LADIES","SUP001","FW","LADIES FTW","FLAT","BASIC","CASUAL","CLOTH","EVA","","12"';
        const csv = `${headers}\n${sample1}\n${sample2}`;
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href = url; a.download = 'smriti_item_master_template.csv';
        a.click();
        URL.revokeObjectURL(url);
    }

    // ── Stats bar update ──────────────────────────────────────────────────
    _update_stats(suffix) {
        const rows = this._get_rows(suffix);
        $(`#cnt-valid-${suffix}`).text(rows.filter(r => r.status === 'valid').length);
        $(`#cnt-warn-${suffix}`).text(rows.filter(r => r.status === 'warning').length);
        $(`#cnt-err-${suffix}`).text(rows.filter(r => r.status === 'error').length);
    }
}

// ── Utility functions ─────────────────────────────────────────────────────

function _parse_tsv_line(line) {
    // Handle both tab-separated (from Excel) and comma-separated
    const sep = line.includes('\t') ? '\t' : ',';
    if (sep === '\t') return line.split('\t').map(c => c.trim().replace(/^"|"$/g, ''));
    // Simple CSV parse (handles quoted fields)
    const result = [];
    let cur = '', inQ = false;
    for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (ch === '"' && (i === 0 || line[i-1] === sep)) { inQ = true; continue; }
        if (ch === '"' && inQ) { inQ = false; continue; }
        if (ch === sep && !inQ) { result.push(cur.trim()); cur = ''; continue; }
        cur += ch;
    }
    result.push(cur.trim());
    return result;
}

function _auto_detect_columns(headerRow) {
    // Returns {colIndex → canonical key} map
    const map = {};
    headerRow.forEach((hdr, i) => {
        const norm = hdr.trim().toLowerCase();
        const canonical = HEADER_ALIASES[norm];
        if (canonical) map[i] = canonical;
    });
    return map;
}

function _esc(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
