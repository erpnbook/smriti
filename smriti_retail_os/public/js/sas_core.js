/**
 * sas_core.js — SMRITI Analytics Studio Core
 * App shell, navigation, panel management, extension points.
 * All communication via frappe.call() → sas_api.py
 */
'use strict';

window.SAS = (function () {

  // ── State ──────────────────────────────────────────────────────────────────
  const state = {
    currentReport: null,
    currentMeta: null,
    reports: {},       // report_key → metadata cache
    categories: [],
    viewsOpen: false,
    colChooserOpen: false,
    chartOpen: false,
    sidebarCollapsed: false,
    density: 'normal',
    kpiVisible: true,
    filterVisible: true,
    toolbarVisible: true,
  };

  // ── DOM Refs ───────────────────────────────────────────────────────────────
  const $ = id => document.getElementById(id);

  // ── Init ───────────────────────────────────────────────────────────────────
  function init() {
    _loadCategories();
    _bindToolbar();
    _bindTopbarActions();
    _bindSearch();
    _bindResize();

    // Check URL param for deep-link to report
    const params = new URLSearchParams(window.location.search);
    const rk = params.get('report');
    if (rk) {
      setTimeout(() => loadReport(rk), 300);
    }
  }

  // ── Category + Report Library ──────────────────────────────────────────────
  function _loadCategories() {
    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_get_categories',
      callback: function (r) {
        state.categories = r.message || [];
        _renderLibrary(state.categories);
      },
      error: function () {
        // Fallback: empty library
        _renderLibrary([]);
      }
    });
  }

  function _renderLibrary(categories) {
    const library = $('sas-report-library');
    if (!library) return;

    library.innerHTML = '';

    categories.forEach(cat => {
      const group = document.createElement('div');
      group.className = 'sas-category-group';

      const header = document.createElement('div');
      header.className = 'sas-category-header';
      header.innerHTML = `
        <span class="material-symbols-outlined" style="font-size:15px">${_catIcon(cat.label)}</span>
        ${cat.label}
        <span class="sas-chevron material-symbols-outlined">chevron_right</span>
      `;

      const items = document.createElement('div');
      items.className = 'sas-category-items';

      (cat.reports || []).forEach(rep => {
        const item = document.createElement('div');
        item.className = 'sas-report-item';
        item.dataset.reportKey = rep.report_key;
        item.innerHTML = `
          <span class="material-symbols-outlined" style="font-size:14px">bar_chart</span>
          <span style="flex:1;overflow:hidden;text-overflow:ellipsis">${rep.report_name}</span>
          ${rep.has_kpi ? '<span class="sas-item-badge">KPI</span>' : ''}
        `;
        item.addEventListener('click', () => loadReport(rep.report_key));
        items.appendChild(item);
      });

      // Toggle collapse
      let isOpen = true;
      header.classList.add('open');
      header.addEventListener('click', () => {
        isOpen = !isOpen;
        header.classList.toggle('open', isOpen);
        items.style.display = isOpen ? 'block' : 'none';
      });

      group.appendChild(header);
      group.appendChild(items);
      library.appendChild(group);
    });
  }

  function _catIcon(label) {
    const icons = {
      'Sales': 'point_of_sale', 'Inventory': 'inventory_2',
      'Purchase': 'shopping_cart', 'Finance': 'account_balance',
      'Cash': 'payments', 'CRM': 'person', 'PSV': 'storefront',
      'Administration': 'admin_panel_settings', 'General': 'analytics',
    };
    for (const [key, icon] of Object.entries(icons)) {
      if (label && label.toLowerCase().includes(key.toLowerCase())) return icon;
    }
    return 'description';
  }

  // ── Report Loader ──────────────────────────────────────────────────────────
  function loadReport(reportKey) {
    if (!reportKey) return;

    state.currentReport = reportKey;
    _setActiveLibraryItem(reportKey);
    _showLoading(true, 'Loading report...');
    _updateBreadcrumb(reportKey);

    // Push URL state
    const url = new URL(window.location.href);
    url.searchParams.set('report', reportKey);
    window.history.pushState({}, '', url.toString());

    // Fetch metadata
    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_get_report_metadata',
      args: { report_key: reportKey },
      callback: function (r) {
        const meta = r.message;
        state.currentMeta = meta;
        state.reports[reportKey] = meta;

        // Update report title
        const titleEl = $('sas-report-title');
        if (titleEl) titleEl.textContent = meta.report_name || reportKey;

        // Render filter bar
        if (window.SASFilters) SASFilters.render(meta.filters || []);

        // Set toolbar visibility options
        _applyToolbarOptions(meta.toolbar_options || []);

        // Restore saved view if any
        SASViews.loadDefault(reportKey, () => {
          // Fetch KPI summary
          if (state.kpiVisible && (meta.kpi_fields || []).length > 0) {
            if (window.SASKpi) SASKpi.load(reportKey, SASFilters.getValues());
          }
          // Fetch data
          fetchData();
        });
      },
      error: function () {
        _showLoading(false);
        _showError('Failed to load report metadata.');
      }
    });
  }

  function fetchData(page) {
    if (!state.currentReport || !state.currentMeta) return;

    const meta = state.currentMeta;
    const filters = window.SASFilters ? SASFilters.getValues() : {};
    const sortModel = window.SASGrid ? SASGrid.getSortModel() : [];
    const groupBy = window.SASGrid ? SASGrid.getGroupByCols() : [];
    const currentPage = page || 1;

    _showLoading(true, `Loading ${meta.report_name}...`);

    const sortBy = sortModel.length ? sortModel[0].colId : null;
    const sortDir = sortModel.length ? sortModel[0].sort : 'desc';

    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_fetch_data',
      args: {
        report_key: state.currentReport,
        filters: JSON.stringify(filters),
        page: currentPage,
        page_size: meta.default_page_size || 500,
        sort_by: sortBy,
        sort_dir: sortDir,
        group_by: JSON.stringify(groupBy),
      },
      callback: function (r) {
        const result = r.message || { rows: [], total_count: 0 };
        _showLoading(false);

        if (window.SASGrid) {
          SASGrid.setData(result.rows, meta, result.total_count, result.page, result.total_pages);
        }

        // Update status bar
        _updateStatusBar(result.rows, result.total_count);

        // Load grand totals async
        _loadGrandTotals(filters);

        // Load KPI
        if (state.kpiVisible && (meta.kpi_fields || []).length > 0) {
          if (window.SASKpi) SASKpi.load(state.currentReport, filters);
        }

        // Refresh chart if open
        if (state.chartOpen && window.SASCharts) {
          SASCharts.update(result.rows, meta);
        }
      },
      error: function () {
        _showLoading(false);
        _showError('Failed to load report data.');
      }
    });
  }

  function _loadGrandTotals(filters) {
    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_get_grand_totals',
      args: {
        report_key: state.currentReport,
        filters: JSON.stringify(filters || {}),
      },
      callback: function (r) {
        if (window.SASGrid && r.message) {
          SASGrid.setGrandTotals(r.message);
        }
      }
    });
  }

  // ── Toolbar Binding ────────────────────────────────────────────────────────
  function _bindToolbar() {
    // Group By button
    _on('sas-btn-groupby', 'click', () => {
      if (window.SASGrid) SASGrid.toggleGroupPanel();
    });

    // Pivot button
    _on('sas-btn-pivot', 'click', () => {
      if (window.SASGrid) SASGrid.togglePivot();
    });

    // Columns chooser
    _on('sas-btn-cols', 'click', () => {
      state.colChooserOpen = !state.colChooserOpen;
      const panel = $('sas-col-chooser');
      if (panel) panel.classList.toggle('open', state.colChooserOpen);
    });

    // Chart toggle
    _on('sas-btn-chart', 'click', () => {
      state.chartOpen = !state.chartOpen;
      const chartPanel = $('sas-chart-panel');
      const gridCont = $('sas-grid-container');
      if (chartPanel) chartPanel.classList.toggle('hidden', !state.chartOpen);
      if (gridCont) gridCont.classList.toggle('chart-open', state.chartOpen);

      const btn = $('sas-btn-chart');
      if (btn) btn.classList.toggle('active', state.chartOpen);

      if (state.chartOpen && window.SASCharts) {
        const meta = state.currentMeta || {};
        const rows = window.SASGrid ? SASGrid.getCurrentRows() : [];
        SASCharts.render(rows, meta, meta.default_chart || {});
      }
    });

    // Density selector
    const densitySel = $('sas-density-select');
    if (densitySel) {
      densitySel.addEventListener('change', () => {
        state.density = densitySel.value;
        const app = document.querySelector('.sas-app');
        if (app) {
          app.classList.remove('sas-density-compact', 'sas-density-comfortable');
          if (state.density !== 'normal') {
            app.classList.add(`sas-density-${state.density}`);
          }
        }
      });
    }

    // Quick filter
    const qf = $('sas-quick-filter');
    if (qf) {
      let debounce;
      qf.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
          if (window.SASGrid) SASGrid.setQuickFilter(qf.value);
        }, 250);
      });
    }

    // Fullscreen
    _on('sas-btn-fullscreen', 'click', () => {
      const app = document.querySelector('.sas-app');
      if (app) {
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else {
          app.requestFullscreen();
        }
      }
    });
  }

  function _bindTopbarActions() {
    // Sidebar toggle
    _on('sas-toggle-sidebar', 'click', () => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
      const panel = document.querySelector('.sas-left-panel');
      if (panel) panel.classList.toggle('collapsed', state.sidebarCollapsed);
    });

    // KPI toggle
    _on('sas-btn-kpi', 'click', () => {
      state.kpiVisible = !state.kpiVisible;
      const kpiRow = $('sas-kpi-row');
      if (kpiRow) kpiRow.classList.toggle('hidden', !state.kpiVisible);
      const btn = $('sas-btn-kpi');
      if (btn) btn.classList.toggle('active', state.kpiVisible);
    });

    // Filter toggle
    _on('sas-btn-filter', 'click', () => {
      state.filterVisible = !state.filterVisible;
      const fb = $('sas-filter-bar');
      if (fb) fb.classList.toggle('hidden', !state.filterVisible);
      const btn = $('sas-btn-filter');
      if (btn) btn.classList.toggle('active', state.filterVisible);
    });

    // Apply filters button
    _on('sas-btn-apply', 'click', () => fetchData());

    // Export dropdown
    _on('sas-btn-export-csv', 'click', () => {
      if (window.SASExport) SASExport.exportCSV();
    });
    _on('sas-btn-export-excel', 'click', () => {
      if (window.SASExport) SASExport.exportExcel();
    });
    _on('sas-btn-export-pdf', 'click', () => {
      if (window.SASExport) SASExport.exportPDF();
    });
    _on('sas-btn-print', 'click', () => window.print());

    // Views (Save/Load)
    _on('sas-btn-views', 'click', () => {
      state.viewsOpen = !state.viewsOpen;
      const panel = $('sas-views-panel');
      if (panel) panel.classList.toggle('open', state.viewsOpen);
      const btn = $('sas-btn-views');
      if (btn) btn.classList.toggle('active', state.viewsOpen);
      if (state.viewsOpen && window.SASViews) {
        SASViews.loadList(state.currentReport);
      }
    });
  }

  function _bindSearch() {
    const searchInput = $('sas-library-search');
    if (!searchInput) return;
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase();
      document.querySelectorAll('.sas-report-item').forEach(el => {
        const name = el.textContent.toLowerCase();
        el.style.display = name.includes(q) ? '' : 'none';
      });
    });
  }

  function _bindResize() {
    window.addEventListener('resize', () => {
      if (window.SASGrid) SASGrid.sizeToFit();
      if (window.SASCharts && state.chartOpen) SASCharts.resize();
    });
  }

  function _applyToolbarOptions(options) {
    const map = {
      'group_by': 'sas-btn-groupby',
      'pivot': 'sas-btn-pivot',
      'columns': 'sas-btn-cols',
      'chart': 'sas-btn-chart',
      'density': 'sas-toolbar-density',
      'fullscreen': 'sas-btn-fullscreen',
    };
    Object.entries(map).forEach(([opt, id]) => {
      const el = $(id);
      if (el) el.style.display = options.includes(opt) ? '' : 'none';
    });
  }

  // ── UI Helpers ─────────────────────────────────────────────────────────────
  function _setActiveLibraryItem(reportKey) {
    document.querySelectorAll('.sas-report-item').forEach(el => {
      el.classList.toggle('active', el.dataset.reportKey === reportKey);
    });
  }

  function _updateBreadcrumb(reportKey) {
    const bc = $('sas-breadcrumb-report');
    if (bc) {
      const meta = state.reports[reportKey] || {};
      bc.textContent = meta.report_name || reportKey.replace(/_/g, ' ');
    }
  }

  function _updateStatusBar(rows, totalCount) {
    const rowEl = $('sas-status-rows');
    if (rowEl) {
      rowEl.innerHTML = `Rows: <strong>${totalCount.toLocaleString()}</strong>`;
    }
  }

  function _showLoading(visible, message) {
    const overlay = $('sas-loading-overlay');
    if (!overlay) return;
    overlay.classList.toggle('hidden', !visible);
    if (visible && message) {
      const p = overlay.querySelector('p');
      if (p) p.textContent = message;
    }
  }

  function _showError(msg) {
    const empty = $('sas-empty-state');
    if (empty) {
      empty.innerHTML = `
        <span class="sas-empty-icon material-symbols-outlined">error</span>
        <h3>Error</h3>
        <p>${msg}</p>
      `;
      empty.style.display = 'flex';
    }
  }

  function _on(id, event, handler) {
    const el = $(id);
    if (el) el.addEventListener(event, handler);
  }

  // ── Coming Soon Handler ────────────────────────────────────────────────────
  function showComingSoon(featureName) {
    window.location.href = `/smriti-coming-soon?feature=${encodeURIComponent(featureName)}`;
  }

  // ── AI Extension Hook (stub) ───────────────────────────────────────────────
  const AI = {
    ask: function (question) {
      console.info('[SAS AI Hook] Query:', question);
      showComingSoon('AI Insights');
    }
  };

  // ── Drill-down Extension Hook ──────────────────────────────────────────────
  function drillDown(rowData, childReportKey, filterField, filterValue) {
    if (!childReportKey) return;
    const filters = {};
    if (filterField && filterValue) filters[filterField] = filterValue;
    // Load child report with inherited filter
    state.drillFilters = filters;
    loadReport(childReportKey);
  }

  // ── Public API ─────────────────────────────────────────────────────────────
  return {
    init,
    loadReport,
    fetchData,
    showComingSoon,
    drillDown,
    AI,
    getState: () => state,
    getCurrentReport: () => state.currentReport,
    getCurrentMeta: () => state.currentMeta,
  };

})();

// Auto-init when DOM ready
document.addEventListener('DOMContentLoaded', () => SAS.init());
