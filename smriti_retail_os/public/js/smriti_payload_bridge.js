/**
 * @file: smriti_retail_os/public/js/smriti_payload_bridge.js
 * @description: Universal UI-to-Backend Payload Bridge — Frontend Engine
 *               Transforms any custom SMRITI UI state into a normalized
 *               Frappe-compatible JSON payload and dispatches it to the
 *               Stateless Backend Kernel (transaction_kernel.py).
 *
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-31
 * @version: 1.8.6
 * @license: MIT
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 *
 * ─── Architectural Philosophy ─────────────────────────────────────────────────
 *
 *  1. ZERO HARDCODING: No module-specific (billing/inventory/purchase) logic.
 *  2. METAPROGRAMMING: Field type coercion driven by Frappe schema at runtime.
 *  3. MATRIX FLATTENING: Horizontal size grids → vertical Frappe child rows.
 *  4. COMPOSABLE: SmritiPayloadBridge.from(state).to('Sales Invoice').validate()
 *
 * ─── Quick Start ──────────────────────────────────────────────────────────────
 *
 *  // Validate (enrich, no DB write):
 *  const result = await SmritiPayloadBridge
 *    .from({ customer: 'Rajesh', _matrix: { ... } })
 *    .to('Sales Invoice')
 *    .validate();
 *
 *  // Save draft:
 *  const result = await SmritiPayloadBridge
 *    .from(uiState)
 *    .to('Sales Invoice')
 *    .save();
 *
 *  // Submit:
 *  const result = await SmritiPayloadBridge
 *    .from(uiState)
 *    .to('Sales Invoice')
 *    .submit();
 *
 *  // Resolve identifiers (barcodes, article+color, customer mobile):
 *  const items = await SmritiPayloadBridge.resolveIdentifiers([
 *    { type: 'barcode', value: '8901234567890' },
 *    { type: 'article_color', article: '20016', color: 'BLACK' },
 *  ]);
 *
 * ─────────────────────────────────────────────────────────────────────────────
 */

'use strict';

// ═══════════════════════════════════════════════════════════════════════════════
//  MATRIX FLATTENER
//  Converts horizontal size-grid UI state → vertical Frappe child table rows.
// ═══════════════════════════════════════════════════════════════════════════════

class MatrixFlattener {
  /**
   * Flattens a UI size-matrix into standard child-table row objects.
   *
   * @param {Object} matrixConfig
   *   {
   *     child_table: "items",          // which child fieldname to populate
   *     size_columns: ["36","37","38"],
   *     rows: [
   *       {
   *         article:      "20016",
   *         color:        "BLACK",
   *         category:     "SANDAL",
   *         sub_category: "LASTIC PATTA",
   *         sizes:        { "36": 0, "37": 9, "38": 5 },
   *         mrp:          1899,
   *         rate:         1610.17,
   *         gst_pct:      18,
   *         hsn_code:     "64041990",
   *         item_code:    "",           // optional override
   *         uom:          "Nos",
   *       }
   *     ]
   *   }
   * @returns {Array} Flat array of Frappe child-table-compatible row objects.
   */
  static flatten(matrixConfig) {
    if (!matrixConfig || typeof matrixConfig !== 'object') return [];

    const sizeColumns  = MatrixFlattener._normalizeColumns(matrixConfig.size_columns || []);
    const matrixRows   = matrixConfig.rows || [];
    const expandedRows = [];

    for (const row of matrixRows) {
      if (!row || typeof row !== 'object') continue;

      const article      = String(row.article      || '').trim();
      const color        = String(row.color        || '').trim();
      const category     = String(row.category     || '').trim();
      const subCategory  = String(row.sub_category || '').trim();
      const sizes        = row.sizes || {};
      const mrp          = parseFloat(row.mrp      || 0);
      const rate         = parseFloat(row.rate     || 0);
      const gstPct       = parseFloat(row.gst_pct  || 0);
      const hsnCode      = String(row.hsn_code     || '').trim();
      const itemCode     = String(row.item_code    || '').trim();
      const uom          = String(row.uom          || 'Nos').trim();
      const taxTemplate  = row.item_tax_template   || '';

      for (const size of sizeColumns) {
        const qty = parseFloat(sizes[String(size)] ?? sizes[size] ?? 0);
        if (qty <= 0) continue;

        expandedRows.push({
          // Core Frappe Sales Invoice Item fields
          item_code:        itemCode,          // resolved later by kernel
          item_name:        [article, color, size].filter(Boolean).join(' '),
          description: (
            `Article: ${article} | Color: ${color} | ` +
            `Category: ${category} | Sub: ${subCategory} | ` +
            `Size: ${size} | MRP: ₹${mrp}`
          ),
          qty:              qty,
          rate:             rate,
          price_list_rate:  mrp,
          uom:              uom,
          gst_hsn_code:     hsnCode,
          item_tax_template: taxTemplate,

          // Kernel enrichment hints (prefixed with _ so Frappe ignores them)
          _article:         article,
          _color:           color,
          _size:            String(size),
          _mrp:             mrp,
          _gst_pct:         gstPct,
        });
      }
    }

    return expandedRows;
  }

  /**
   * Computes per-row totals from a flat expanded rows array.
   * Useful for UI summary rendering before submission.
   */
  static computeSummary(flatRows) {
    const summary = {
      total_qty:     0,
      net_total:     0,
      total_tax:     0,
      grand_total:   0,
      row_count:     flatRows.length,
    };

    for (const row of flatRows) {
      const qty    = parseFloat(row.qty    || 0);
      const rate   = parseFloat(row.rate   || 0);
      const gstPct = parseFloat(row._gst_pct || 0);
      const net    = qty * rate;
      const tax    = net * (gstPct / 100);

      summary.total_qty   += qty;
      summary.net_total   += net;
      summary.total_tax   += tax;
      summary.grand_total += net + tax;
    }

    summary.net_total   = Math.round(summary.net_total   * 100) / 100;
    summary.total_tax   = Math.round(summary.total_tax   * 100) / 100;
    summary.grand_total = Math.round(summary.grand_total * 100) / 100;

    return summary;
  }

  /** Normalize size_columns — accept strings, numbers, or mixed arrays. */
  static _normalizeColumns(cols) {
    if (!Array.isArray(cols)) return [];
    return cols.map(c => String(c).trim()).filter(Boolean);
  }
}


// ═══════════════════════════════════════════════════════════════════════════════
//  FIELD TYPE COERCER
//  Converts JS values to the type expected by Frappe field definitions.
//  Runs client-side before dispatch to catch type mismatches early.
// ═══════════════════════════════════════════════════════════════════════════════

class FieldTypeCoercer {
  /**
   * Coerces a single value based on its Frappe fieldtype string.
   * @param {*}      value
   * @param {string} fieldtype  e.g. "Float", "Int", "Check", "Data", "Date"
   * @returns {*} Coerced value.
   */
  static coerce(value, fieldtype) {
    if (value === null || value === undefined) return value;

    switch (fieldtype) {
      case 'Float':
      case 'Currency':
      case 'Percent': {
        const n = parseFloat(value);
        return isNaN(n) ? 0 : n;
      }
      case 'Int':
      case 'Check': {
        const n = parseInt(value, 10);
        return isNaN(n) ? 0 : n;
      }
      case 'Data':
      case 'Small Text':
      case 'Text':
      case 'Long Text':
      case 'Text Editor':
      case 'Code':
      case 'Link':
      case 'Dynamic Link':
      case 'Select':
      case 'Read Only':
        return value === null || value === undefined ? '' : String(value);
      case 'Date':
        return FieldTypeCoercer._normalizeDate(value);
      case 'Datetime':
        return value ? String(value) : null;
      default:
        return value;
    }
  }

  /**
   * Coerces an entire flat object against a schema map.
   * @param {Object} obj        The flat object to coerce.
   * @param {Object} schemaMap  { fieldname: { fieldtype, ... }, ... }
   * @returns {Object} Coerced copy.
   */
  static coerceObject(obj, schemaMap) {
    const result = {};
    for (const [key, val] of Object.entries(obj)) {
      if (key.startsWith('_')) {
        result[key] = val; // pass kernel markers through
        continue;
      }
      const fieldDef = schemaMap[key];
      result[key] = fieldDef
        ? FieldTypeCoercer.coerce(val, fieldDef.fieldtype)
        : val;
    }
    return result;
  }

  static _normalizeDate(value) {
    if (!value) return null;
    if (/^\d{4}-\d{2}-\d{2}$/.test(String(value))) return String(value);
    try {
      const d = new Date(value);
      if (isNaN(d.getTime())) return null;
      return d.toISOString().slice(0, 10);
    } catch (_) {
      return null;
    }
  }
}


// ═══════════════════════════════════════════════════════════════════════════════
//  PAYLOAD VALIDATOR
//  Client-side pre-validation before dispatching to kernel.
//  Runs synchronously — does NOT call any API.
// ═══════════════════════════════════════════════════════════════════════════════

class PayloadValidator {
  /**
   * Validates a normalized payload against a set of rules.
   * @param {Object}   payload       Normalized payload dict.
   * @param {Object}   options
   * @param {string[]} options.required   Fields that must be non-empty.
   * @param {Object}   options.schema     { fieldname: { fieldtype } } for type checks.
   * @returns {{ valid: boolean, errors: string[] }}
   */
  static validate(payload, { required = [], schema = {} } = {}) {
    const errors = [];

    // Required field checks
    for (const field of required) {
      const val = payload[field];
      if (val === null || val === undefined || val === '') {
        errors.push(`Required field missing: ${field}`);
      }
    }

    // Type sanity checks for numeric fields
    for (const [field, def] of Object.entries(schema)) {
      if (!def || !def.fieldtype) continue;
      const val = payload[field];
      if (val === null || val === undefined) continue;
      if (['Float', 'Currency', 'Int', 'Check'].includes(def.fieldtype)) {
        if (isNaN(parseFloat(val))) {
          errors.push(`Field '${field}' must be numeric. Got: ${val}`);
        }
      }
    }

    // Item rows sanity
    const items = payload.items;
    if (Array.isArray(items)) {
      if (items.length === 0) {
        errors.push('No item rows found. Please add at least one item.');
      }
      items.forEach((row, idx) => {
        if (!row.item_code && !row._article) {
          errors.push(`Row ${idx + 1}: item_code is required.`);
        }
        if (parseFloat(row.qty || 0) <= 0) {
          errors.push(`Row ${idx + 1}: qty must be > 0.`);
        }
      });
    }

    return { valid: errors.length === 0, errors };
  }
}


// ═══════════════════════════════════════════════════════════════════════════════
//  SMRITI PAYLOAD BRIDGE  — Main Class
// ═══════════════════════════════════════════════════════════════════════════════

class SmritiPayloadBridge {
  /**
   * @param {Object} uiState  Raw UI state object from any SMRITI module.
   */
  constructor(uiState = {}) {
    this._uiState   = uiState || {};
    this._doctype   = null;
    this._schema    = null;  // cached from get_doctype_schema
    this._listeners = { onValidate: [], onSave: [], onSubmit: [], onError: [] };
  }

  // ── Fluent builder ──────────────────────────────────────────────────────────

  /** Static factory: SmritiPayloadBridge.from(state) */
  static from(uiState) {
    return new SmritiPayloadBridge(uiState);
  }

  /** Set target DocType. Chainable. */
  to(doctype) {
    this._doctype = doctype;
    return this;
  }

  /** Attach event listener. Chainable. */
  on(event, fn) {
    if (this._listeners[event]) this._listeners[event].push(fn);
    return this;
  }

  // ── Primary action methods ──────────────────────────────────────────────────

  /**
   * VALIDATE: Normalize, enrich, return enriched payload. No DB write.
   * @returns {Promise<Object>} Enriched payload from kernel.
   */
  async validate() {
    return this._dispatch('validate');
  }

  /**
   * SAVE: Normalize, enrich, write Draft document.
   * @returns {Promise<Object>} { name, docstatus, grand_total, ... }
   */
  async save() {
    return this._dispatch('save');
  }

  /**
   * SUBMIT: Normalize, enrich, save + submit (commits ledger).
   * @returns {Promise<Object>} { name, docstatus, grand_total, ... }
   */
  async submit() {
    return this._dispatch('submit');
  }

  // ── Static utility methods ──────────────────────────────────────────────────

  /**
   * Resolve a list of primary identifiers (barcodes, article+color, etc.)
   * via the kernel's stateless lookup endpoint.
   *
   * @param {Array}  identifiers  Array of { type, value, ... } objects.
   * @param {string} company      Optional company override.
   * @returns {Promise<Array>}    Enriched records (same order).
   */
  static async resolveIdentifiers(identifiers, company = null) {
    if (!Array.isArray(identifiers) || identifiers.length === 0) return [];
    return SmritiPayloadBridge._callKernel(
      'smriti_retail_os.transaction_kernel.resolve_identifiers',
      { identifiers: JSON.stringify(identifiers), company: company || '' }
    );
  }

  /**
   * Fetch DocType schema from kernel for dynamic form generation.
   * Result is cached in-memory per doctype per page session.
   *
   * @param {string} doctype
   * @returns {Promise<Object>} { fields, child_tables, mandatory_fields }
   */
  static async getSchema(doctype) {
    if (!doctype) throw new Error('SmritiPayloadBridge.getSchema: doctype required');
    const cacheKey = `__smriti_schema__${doctype}`;
    if (window[cacheKey]) return window[cacheKey];
    const schema = await SmritiPayloadBridge._callKernel(
      'smriti_retail_os.transaction_kernel.get_doctype_schema',
      { doctype }
    );
    window[cacheKey] = schema;
    return schema;
  }

  /**
   * Apply pricing rules to an item rows array.
   * @param {string} doctype
   * @param {Object} payload  { customer, posting_date, items: [...] }
   * @returns {Promise<Object>} { items: [...with discount/rate applied] }
   */
  static async applyPricingRules(doctype, payload) {
    return SmritiPayloadBridge._callKernel(
      'smriti_retail_os.transaction_kernel.apply_pricing_rules',
      { doctype, payload: JSON.stringify(payload) }
    );
  }

  /**
   * Flatten a horizontal size matrix into vertical child table rows.
   * Runs entirely client-side — no network call.
   *
   * @param {Object} matrixConfig  { size_columns, rows }
   * @returns {Array}
   */
  static flattenMatrix(matrixConfig) {
    return MatrixFlattener.flatten(matrixConfig);
  }

  /**
   * Compute a running summary (qty, net, tax, grand total) from flat rows.
   * Runs entirely client-side — no network call.
   *
   * @param {Array} flatRows
   * @returns {Object} { total_qty, net_total, total_tax, grand_total }
   */
  static computeSummary(flatRows) {
    return MatrixFlattener.computeSummary(flatRows);
  }

  // ── Internal normalize + dispatch ───────────────────────────────────────────

  async _dispatch(action) {
    if (!this._doctype) {
      throw new Error('SmritiPayloadBridge: call .to(doctype) before dispatching.');
    }

    try {
      // 1. Normalize UI state → kernel payload
      const normalized = await this._normalize();

      // 2. Client-side validation
      const { valid, errors } = this._clientValidate(normalized);
      if (!valid) {
        const err = new Error(`Payload validation failed:\n${errors.join('\n')}`);
        err.validationErrors = errors;
        this._emit('onError', err);
        throw err;
      }

      // 3. Dispatch to kernel
      const result = await SmritiPayloadBridge._callKernel(
        'smriti_retail_os.transaction_kernel.execute_smriti_transaction',
        {
          doctype: this._doctype,
          payload: JSON.stringify(normalized),
          action,
        }
      );

      // 4. Emit success event
      this._emit(`on${action.charAt(0).toUpperCase() + action.slice(1)}`, result);
      return result;

    } catch (err) {
      this._emit('onError', err);
      throw err;
    }
  }

  /**
   * Normalize raw UI state into a clean kernel payload.
   * Handles:
   *  - _matrix shorthand → _matrix key (kernel does the actual DB-side resolution)
   *  - items array → ensure it's an array
   *  - scalar field coercion if schema loaded
   */
  async _normalize() {
    const state   = this._uiState;
    const payload = {};

    for (const [key, val] of Object.entries(state)) {
      if (val === undefined) continue;  // drop undefined

      if (key === '_matrix') {
        // Keep _matrix as-is for kernel flattening + item_code resolution
        payload._matrix = val;
        continue;
      }

      if (Array.isArray(val)) {
        // Child table arrays — normalize each row
        payload[key] = val.map(row => (typeof row === 'object' && row !== null)
          ? SmritiPayloadBridge._normalizeRow(row)
          : row
        );
        continue;
      }

      payload[key] = val;
    }

    // Schema-driven coercion (if schema already loaded)
    if (this._schema) {
      const schemaMap = {};
      for (const f of (this._schema.fields || [])) {
        schemaMap[f.fieldname] = f;
      }
      return FieldTypeCoercer.coerceObject(payload, schemaMap);
    }

    return payload;
  }

  _clientValidate(payload) {
    const requiredFields = [];

    // Infer common required fields by doctype
    const doctypeRequiredMap = {
      'Sales Invoice':     ['customer'],
      'POS Invoice':       ['customer'],
      'Purchase Order':    ['supplier'],
      'Purchase Receipt':  ['supplier'],
      'Stock Entry':       ['stock_entry_type'],
    };

    const required = doctypeRequiredMap[this._doctype] || [];
    return PayloadValidator.validate(payload, { required });
  }

  _emit(event, data) {
    for (const fn of (this._listeners[event] || [])) {
      try { fn(data); } catch (_) {}
    }
  }

  static _normalizeRow(row) {
    const clean = {};
    for (const [k, v] of Object.entries(row)) {
      if (v === undefined) continue;
      clean[k] = v;
    }
    return clean;
  }

  // ── HTTP transport ──────────────────────────────────────────────────────────

  /**
   * Calls a Frappe whitelisted method.
   * Works in both Frappe Desk (frappe.call) and standalone HTML pages (fetch).
   *
   * @param {string} method   Full Python dotted path.
   * @param {Object} args     Key-value arguments.
   * @returns {Promise<*>}    Resolved message value.
   */
  static async _callKernel(method, args = {}) {
    // ── Frappe Desk context (frappe.call available) ───────────────────────────
    if (typeof frappe !== 'undefined' && typeof frappe.call === 'function') {
      return new Promise((resolve, reject) => {
        frappe.call({
          method,
          args,
          freeze: false,
          callback: r => resolve(r.message),
          error:    e => reject(SmritiPayloadBridge._extractError(e)),
        });
      });
    }

    // ── Standalone page context (bare fetch) ──────────────────────────────────
    const formData = new FormData();
    for (const [k, v] of Object.entries(args)) {
      formData.append(k, v === null || v === undefined ? '' : String(v));
    }

    const resp = await fetch(`/api/method/${method}`, {
      method:      'POST',
      body:        formData,
      credentials: 'same-origin',
      headers:     {
        'X-Frappe-CSRF-Token': SmritiPayloadBridge._getCsrfToken(),
      },
    });

    if (!resp.ok) {
      let errMsg = `HTTP ${resp.status}`;
      try {
        const body = await resp.json();
        errMsg = body.exception || body.message || errMsg;
      } catch (_) {}
      throw new Error(`Kernel API error: ${errMsg}`);
    }

    const json = await resp.json();
    return json.message;
  }

  static _getCsrfToken() {
    // Frappe sets csrf_token on the cookie
    const match = document.cookie.match(/csrf_token=([^;]+)/);
    if (match) return decodeURIComponent(match[1]);
    // Fallback: read from frappe boot
    if (typeof frappe !== 'undefined' && frappe.csrf_token) return frappe.csrf_token;
    return '';
  }

  static _extractError(e) {
    if (!e) return new Error('Unknown kernel error');
    if (typeof e === 'string') return new Error(e);
    if (e.message) return e;
    if (e.responseJSON && e.responseJSON.exception) return new Error(e.responseJSON.exception);
    return new Error(JSON.stringify(e));
  }
}


// ═══════════════════════════════════════════════════════════════════════════════
//  SMRITI TRANSACTION API CLIENT
//  Thin wrapper with toast feedback, retry, and loading state management.
// ═══════════════════════════════════════════════════════════════════════════════

class SmritiTransaction {
  /**
   * @param {string}   doctype   Target Frappe DocType.
   * @param {Object}   options
   * @param {Function} options.onSuccess   Called with result on success.
   * @param {Function} options.onError     Called with error on failure.
   * @param {Function} options.onLoading   Called with true/false for UI spinners.
   * @param {boolean}  options.toast       Show frappe.msgprint / alert toasts.
   * @param {number}   options.retries     Number of retries on network error (default 1).
   */
  constructor(doctype, options = {}) {
    this.doctype    = doctype;
    this.onSuccess  = options.onSuccess  || null;
    this.onError    = options.onError    || null;
    this.onLoading  = options.onLoading  || null;
    this.toast      = options.toast !== false;
    this.retries    = options.retries    ?? 1;
  }

  /**
   * Execute a transaction action with UI feedback and retry logic.
   * @param {Object} uiState  Raw UI state.
   * @param {string} action   'validate' | 'save' | 'submit'
   * @returns {Promise<Object>}
   */
  async execute(uiState, action = 'validate') {
    this._setLoading(true);
    let lastErr;

    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const result = await SmritiPayloadBridge
          .from(uiState)
          .to(this.doctype)
          [action]();

        this._setLoading(false);

        if (this.toast) {
          SmritiTransaction._showSuccess(action, result);
        }
        if (this.onSuccess) this.onSuccess(result);
        return result;

      } catch (err) {
        lastErr = err;
        if (attempt < this.retries) {
          await SmritiTransaction._sleep(600 * (attempt + 1)); // exponential back-off
        }
      }
    }

    this._setLoading(false);

    if (this.toast) {
      SmritiTransaction._showError(lastErr);
    }
    if (this.onError) this.onError(lastErr);
    throw lastErr;
  }

  _setLoading(state) {
    if (typeof this.onLoading === 'function') this.onLoading(state);
  }

  static _showSuccess(action, result) {
    const actionLabels = { validate: 'Validated', save: 'Saved', submit: 'Submitted' };
    const label  = actionLabels[action] || action;
    const name   = result?.name || '';
    const total  = result?.grand_total != null ? ` | ₹${result.grand_total}` : '';
    const msg    = `✅ ${label}: ${name}${total}`;

    if (typeof frappe !== 'undefined' && frappe.show_alert) {
      frappe.show_alert({ message: msg, indicator: 'green' }, 5);
    } else {
      console.info('[SMRITI Kernel]', msg);
    }
  }

  static _showError(err) {
    const msg = err?.message || 'Unknown kernel error';
    if (typeof frappe !== 'undefined' && frappe.msgprint) {
      frappe.msgprint({ title: 'Transaction Error', message: msg, indicator: 'red' });
    } else {
      console.error('[SMRITI Kernel Error]', msg);
    }
  }

  static _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}


// ═══════════════════════════════════════════════════════════════════════════════
//  EXPORTS
//  Works as both a plain browser script (window globals) and ES module.
// ═══════════════════════════════════════════════════════════════════════════════

// Browser globals (standalone HTML pages & Frappe Desk)
if (typeof window !== 'undefined') {
  window.SmritiPayloadBridge  = SmritiPayloadBridge;
  window.SmritiTransaction    = SmritiTransaction;
  window.MatrixFlattener      = MatrixFlattener;
  window.FieldTypeCoercer     = FieldTypeCoercer;
  window.PayloadValidator     = PayloadValidator;
}

// ES module export (if bundler used)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    SmritiPayloadBridge,
    SmritiTransaction,
    MatrixFlattener,
    FieldTypeCoercer,
    PayloadValidator,
  };
}
