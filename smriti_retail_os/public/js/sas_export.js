/**
 * sas_export.js — SMRITI Analytics Studio Export Center
 * CSV: client-side via AG Grid native export
 * Excel: server-side via sas_api.sas_export_excel (openpyxl)
 * PDF: print-to-PDF via window.print() with print CSS
 */
'use strict';

window.SASExport = (function () {

  function _today() {
    return new Date().toISOString().split('T')[0];
  }

  // ── CSV (AG Grid native, client-side) ─────────────────────────────────────
  function exportCSV() {
    const reportKey = SAS.getCurrentReport();
    if (!reportKey) {
      frappe.msgprint('Please select a report first.');
      return;
    }
    if (window.SASGrid) {
      SASGrid.exportCSV(`smriti_${reportKey}_${_today()}.csv`);
    }
  }

  // ── Excel (server-side via openpyxl) ─────────────────────────────────────
  function exportExcel() {
    const reportKey = SAS.getCurrentReport();
    if (!reportKey) {
      frappe.msgprint('Please select a report first.');
      return;
    }

    const filters = window.SASFilters ? SASFilters.getValues() : {};
    const layoutState = window.SASGrid ? SASGrid.getLayoutState() : {};
    const viewName = window.SASViews ? SASViews.getActiveViewName() : null;

    _showExportBadge('Excel', 'loading');

    // Frappe file download via whitelisted method
    const params = {
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_export_excel',
      args: {
        report_key: reportKey,
        filters: JSON.stringify(filters),
        state_json: JSON.stringify({ ...layoutState, view_name: viewName }),
      },
    };

    // Use frappe.call with type binary to trigger download
    const url = new URL('/api/method/' + params.method, window.location.origin);
    url.searchParams.set('report_key', reportKey);
    url.searchParams.set('filters', JSON.stringify(filters));
    url.searchParams.set('state_json', JSON.stringify({ ...layoutState, view_name: viewName }));

    // Create a form and submit for file download
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/api/method/${params.method}`;
    form.target = '_blank';
    form.style.display = 'none';

    const addField = (name, value) => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      input.value = value;
      form.appendChild(input);
    };

    addField('report_key', reportKey);
    addField('filters', JSON.stringify(filters));
    addField('state_json', JSON.stringify({ ...layoutState, view_name: viewName }));

    // CSRF token
    if (frappe.csrf_token) addField('X-Frappe-CSRF-Token', frappe.csrf_token);

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);

    _showExportBadge('Excel', 'done');
  }

  // ── PDF (print-to-PDF) ────────────────────────────────────────────────────
  function exportPDF() {
    const reportKey = SAS.getCurrentReport();
    const meta = SAS.getCurrentMeta() || {};
    const reportName = meta.report_name || (reportKey || '').replace(/_/g, ' ');

    // Inject print title
    const printTitle = document.getElementById('sas-print-title');
    if (printTitle) {
      printTitle.textContent = `SMRITI Analytics Studio — ${reportName}`;
    }

    window.print();
  }

  // ── Export Badge (small toast feedback) ───────────────────────────────────
  function _showExportBadge(type, state) {
    const existing = document.getElementById('sas-export-badge');
    if (existing) existing.remove();

    const badge = document.createElement('div');
    badge.id = 'sas-export-badge';
    badge.style.cssText = `
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      background: var(--smriti-color-bg-secondary);
      border: 1px solid var(--smriti-color-border-default);
      border-radius: 10px; padding: 12px 18px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
      display: flex; align-items: center; gap: 10px;
      font-size: 13px; color: var(--smriti-color-text-primary);
      animation: sas-slide-up 0.2s ease;
    `;

    if (state === 'loading') {
      badge.innerHTML = `
        <div class="sas-spinner" style="width:20px;height:20px;border-width:2px"></div>
        Generating ${type} export...
      `;
    } else if (state === 'done') {
      badge.innerHTML = `
        <span style="color:var(--smriti-color-status-success,#10b981);font-size:18px">✓</span>
        ${type} export ready
      `;
      setTimeout(() => badge.remove(), 3000);
    } else if (state === 'error') {
      badge.innerHTML = `
        <span style="color:var(--smriti-color-status-danger,#ef4444);font-size:18px">✕</span>
        ${type} export failed
      `;
      setTimeout(() => badge.remove(), 4000);
    }

    document.body.appendChild(badge);
  }

  return { exportCSV, exportExcel, exportPDF };

})();
