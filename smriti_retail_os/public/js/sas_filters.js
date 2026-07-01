/**
 * sas_filters.js — SMRITI Analytics Studio Filter Bar
 * Dynamically renders filter fields from report metadata filters_json.
 * Produces clean key-value filter object for sas_api.sas_fetch_data().
 */
'use strict';

window.SASFilters = (function () {

  const CONTAINER_ID = 'sas-filter-bar';
  const ACTIONS_ID   = 'sas-filter-actions';

  let _currentFilters = [];
  let _values = {};

  // ── Render ──────────────────────────────────────────────────────────────────
  function render(filterDefs) {
    _currentFilters = filterDefs || [];
    _values = {};

    const container = document.getElementById(CONTAINER_ID);
    if (!container) return;

    // Preserve the actions row
    const actionsEl = document.getElementById(ACTIONS_ID);

    // Clear current filter fields (not the actions)
    Array.from(container.children).forEach(child => {
      if (child.id !== ACTIONS_ID) child.remove();
    });

    // Set defaults
    const today = _today();
    const monthStart = _monthStart();

    _currentFilters.forEach(fd => {
      // Set default values
      if (fd.fieldtype === 'Date') {
        if (fd.fieldname === 'from_date') _values[fd.fieldname] = monthStart;
        else if (fd.fieldname === 'to_date') _values[fd.fieldname] = today;
        else _values[fd.fieldname] = today;
      } else if (fd.default !== undefined && fd.default !== null) {
        _values[fd.fieldname] = fd.default;
      } else {
        _values[fd.fieldname] = '';
      }

      const fieldEl = _createField(fd);
      if (fieldEl) {
        container.insertBefore(fieldEl, actionsEl);
      }
    });

    // Auto-populate company from Frappe defaults
    if (_values.hasOwnProperty('company')) {
      const company = (frappe.boot && frappe.boot.sysdefaults &&
        frappe.boot.sysdefaults.company) || '';
      if (company) {
        _values['company'] = company;
        const el = container.querySelector('[data-field="company"]');
        if (el) el.value = company;
      }
    }
  }

  // ── Field Builder ───────────────────────────────────────────────────────────
  function _createField(fd) {
    const { fieldname, label, fieldtype, options, reqd } = fd;

    const wrap = document.createElement('div');
    wrap.className = 'sas-filter-field';

    const lbl = document.createElement('label');
    lbl.textContent = label + (reqd ? ' *' : '');
    lbl.htmlFor = `sf-${fieldname}`;

    let input;

    if (fieldtype === 'Date') {
      input = document.createElement('input');
      input.type = 'date';
      input.value = _values[fieldname] || '';
    } else if (fieldtype === 'Select' && options) {
      input = document.createElement('select');
      // Options can be a newline-separated string
      const opts = typeof options === 'string' ? options.split('\n') : (Array.isArray(options) ? options : []);
      const blank = document.createElement('option');
      blank.value = ''; blank.textContent = `— All ${label} —`;
      input.appendChild(blank);
      opts.forEach(opt => {
        const o = document.createElement('option');
        o.value = opt; o.textContent = opt;
        input.appendChild(o);
      });
      input.value = _values[fieldname] || '';
    } else if (fieldtype === 'Link') {
      // For Link fields, render as a text input with a fetch-on-blur (lightweight)
      input = document.createElement('input');
      input.type = 'text';
      input.placeholder = `Select ${label}`;
      input.value = _values[fieldname] || '';
      input.dataset.doctype = options || '';
    } else if (fieldtype === 'Check') {
      input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = !!_values[fieldname];
    } else {
      input = document.createElement('input');
      input.type = 'text';
      input.placeholder = label;
      input.value = _values[fieldname] || '';
    }

    input.id = `sf-${fieldname}`;
    input.dataset.field = fieldname;

    input.addEventListener('change', (e) => {
      _values[fieldname] = e.target.type === 'checkbox' ? (e.target.checked ? 1 : 0) : e.target.value;
    });
    input.addEventListener('input', (e) => {
      if (e.target.type !== 'checkbox') {
        _values[fieldname] = e.target.value;
      }
    });

    wrap.appendChild(lbl);
    wrap.appendChild(input);
    return wrap;
  }

  // ── Quick Date Presets ──────────────────────────────────────────────────────
  function applyPreset(preset) {
    const today = _today();
    const from = document.getElementById('sf-from_date');
    const to   = document.getElementById('sf-to_date');

    let fromDate = today, toDate = today;

    if (preset === 'today') {
      fromDate = today; toDate = today;
    } else if (preset === 'yesterday') {
      fromDate = toDate = _addDays(today, -1);
    } else if (preset === 'this_week') {
      const d = new Date();
      const day = d.getDay();
      const diff = d.getDate() - day + (day === 0 ? -6 : 1);
      const mon = new Date(d.setDate(diff));
      fromDate = mon.toISOString().split('T')[0];
      toDate = today;
    } else if (preset === 'this_month') {
      fromDate = _monthStart(); toDate = today;
    } else if (preset === 'last_month') {
      const now = new Date();
      const first = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const last  = new Date(now.getFullYear(), now.getMonth(), 0);
      fromDate = first.toISOString().split('T')[0];
      toDate   = last.toISOString().split('T')[0];
    } else if (preset === 'this_quarter') {
      const now = new Date();
      const q = Math.floor(now.getMonth() / 3);
      const first = new Date(now.getFullYear(), q * 3, 1);
      fromDate = first.toISOString().split('T')[0];
      toDate = today;
    } else if (preset === 'this_year') {
      fromDate = `${new Date().getFullYear()}-04-01`;  // India FY
      toDate = today;
    }

    if (from) { from.value = fromDate; _values['from_date'] = fromDate; }
    if (to)   { to.value = toDate;     _values['to_date'] = toDate; }
  }

  // ── Compare Period Filters ──────────────────────────────────────────────────
  function getCompareFilters(period) {
    const from = _values['from_date'];
    const to   = _values['to_date'];
    if (!from || !to) return null;

    const fromD = new Date(from);
    const toD   = new Date(to);
    const diff  = (toD - fromD) / (1000 * 60 * 60 * 24);

    let cFrom, cTo;
    if (period === 'yesterday') {
      cFrom = cTo = _addDays(from, -1);
    } else if (period === 'last_week') {
      cFrom = _addDays(from, -7);
      cTo   = _addDays(to, -7);
    } else if (period === 'last_month') {
      const f = new Date(fromD);
      f.setMonth(f.getMonth() - 1);
      const t = new Date(toD);
      t.setMonth(t.getMonth() - 1);
      cFrom = f.toISOString().split('T')[0];
      cTo   = t.toISOString().split('T')[0];
    } else if (period === 'last_year') {
      const f = new Date(fromD);
      const t = new Date(toD);
      f.setFullYear(f.getFullYear() - 1);
      t.setFullYear(t.getFullYear() - 1);
      cFrom = f.toISOString().split('T')[0];
      cTo   = t.toISOString().split('T')[0];
    } else {
      return null;
    }

    return { ..._values, from_date: cFrom, to_date: cTo };
  }

  // ── Getters ─────────────────────────────────────────────────────────────────
  function getValues() {
    // Return only non-empty values
    const clean = {};
    Object.entries(_values).forEach(([k, v]) => {
      if (v !== '' && v !== null && v !== undefined) clean[k] = v;
    });
    return clean;
  }

  function setValues(values) {
    _values = { ..._values, ...values };
    // Update DOM
    Object.entries(values).forEach(([k, v]) => {
      const el = document.querySelector(`[data-field="${k}"]`);
      if (el) {
        if (el.type === 'checkbox') el.checked = !!v;
        else el.value = v || '';
      }
    });
  }

  // ── Utility ─────────────────────────────────────────────────────────────────
  function _today() {
    return new Date().toISOString().split('T')[0];
  }
  function _monthStart() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`;
  }
  function _addDays(dateStr, days) {
    const d = new Date(dateStr);
    d.setDate(d.getDate() + days);
    return d.toISOString().split('T')[0];
  }

  // ── Public ──────────────────────────────────────────────────────────────────
  return { render, getValues, setValues, applyPreset, getCompareFilters };

})();
