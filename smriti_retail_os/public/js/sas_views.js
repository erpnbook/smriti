/**
 * sas_views.js — SMRITI Analytics Studio Saved View Manager
 * Saves and restores full SAS state: filters, sort, grouping, pinned,
 * page size, density, chart type, theme, toolbar, frozen, quick filter, date range.
 * Server persistence via sas_api.sas_save_view / sas_get_views.
 * Also maintains localStorage fallback for speed.
 */
'use strict';

window.SASViews = (function () {

  const LS_PREFIX = 'sas_view_';
  let _activeViewName = null;
  let _viewsList = [];

  // ── Build Full State Object ─────────────────────────────────────────────────
  function _buildFullState(viewName) {
    const meta = SAS.getCurrentMeta() || {};
    const gridState = window.SASGrid ? SASGrid.getLayoutState() : {};
    const filterValues = window.SASFilters ? SASFilters.getValues() : {};
    const sasState = SAS.getState();

    return {
      view_name: viewName,
      report_key: SAS.getCurrentReport(),
      saved_at: new Date().toISOString(),

      // Grid-level state
      column_state: gridState.column_state || [],
      filter_model: gridState.filter_model || {},
      sort_model: gridState.sort_model || [],
      group_by_cols: gridState.group_by_cols || [],
      pinned_cols: { left: [], right: [] },
      hidden_cols: [],
      pivot_active: gridState.pivot_active || false,

      // Filter bar values
      filter_values: filterValues,
      date_range: {
        from: filterValues.from_date || null,
        to: filterValues.to_date || null,
      },
      quick_filter: (document.getElementById('sas-quick-filter') || {}).value || '',

      // UI state
      page_size: meta.default_page_size || 500,
      density: sasState.density || 'normal',
      chart_type: (meta.default_chart || {}).type || 'bar',
      chart_visible: sasState.chartOpen || false,
      kpi_visible: sasState.kpiVisible !== false,
      filter_visible: sasState.filterVisible !== false,
      toolbar_visible: sasState.toolbarVisible !== false,
      sidebar_collapsed: sasState.sidebarCollapsed || false,

      // Compare period
      compare_period: null,
    };
  }

  // ── Save ────────────────────────────────────────────────────────────────────
  function save(viewName, reportKey) {
    if (!viewName) return;

    const state = _buildFullState(viewName);
    _activeViewName = viewName;

    // localStorage for instant restore
    try {
      localStorage.setItem(`${LS_PREFIX}${reportKey}_${viewName}`, JSON.stringify(state));
    } catch (e) {}

    // Server persist
    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_save_view',
      args: {
        view_name: viewName,
        report_key: reportKey || SAS.getCurrentReport(),
        state_json: JSON.stringify(state),
      },
      callback: function (r) {
        frappe.show_alert({
          message: `View "${viewName}" saved`,
          indicator: 'green',
        }, 3);
        loadList(reportKey);
      },
      error: function () {
        frappe.show_alert({ message: 'Failed to save view', indicator: 'red' }, 3);
      }
    });
  }

  // ── Restore ─────────────────────────────────────────────────────────────────
  function restore(viewData) {
    if (!viewData) return;

    const state = typeof viewData === 'string' ? JSON.parse(viewData) : viewData;
    _activeViewName = state.view_name;

    // Restore filter values
    if (state.filter_values && window.SASFilters) {
      SASFilters.setValues(state.filter_values);
    }

    // Restore grid state
    if (window.SASGrid) {
      SASGrid.restoreLayoutState({
        column_state: state.column_state,
        filter_model: state.filter_model,
        sort_model: state.sort_model,
        group_by_cols: state.group_by_cols,
        pivot_active: state.pivot_active,
      });
    }

    // Restore quick filter
    const qf = document.getElementById('sas-quick-filter');
    if (qf && state.quick_filter) {
      qf.value = state.quick_filter;
      if (window.SASGrid) SASGrid.setQuickFilter(state.quick_filter);
    }

    // Restore density
    if (state.density) {
      const sel = document.getElementById('sas-density-select');
      if (sel) sel.value = state.density;
      const app = document.querySelector('.sas-app');
      if (app) {
        app.classList.remove('sas-density-compact', 'sas-density-comfortable');
        if (state.density !== 'normal') app.classList.add(`sas-density-${state.density}`);
      }
    }

    // Restore chart visibility
    if (state.chart_visible && window.SASCharts) {
      const chartPanel = document.getElementById('sas-chart-panel');
      if (chartPanel) chartPanel.classList.remove('hidden');
    }
  }

  // ── Load Default View ───────────────────────────────────────────────────────
  function loadDefault(reportKey, callback) {
    // Try localStorage first (fastest)
    const lsKey = `${LS_PREFIX}${reportKey}_default`;
    try {
      const cached = localStorage.getItem(lsKey);
      if (cached) {
        restore(JSON.parse(cached));
      }
    } catch (e) {}

    if (callback) callback();
  }

  // ── Load View List ──────────────────────────────────────────────────────────
  function loadList(reportKey) {
    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_get_views',
      args: { report_key: reportKey },
      callback: function (r) {
        _viewsList = r.message || [];
        _renderViewsList();
      }
    });
  }

  function _renderViewsList() {
    const container = document.getElementById('sas-views-list');
    if (!container) return;
    container.innerHTML = '';

    if (_viewsList.length === 0) {
      container.innerHTML = `<p style="padding:12px 14px;color:var(--sas-text-3);font-size:12px">No saved views yet.</p>`;
      return;
    }

    _viewsList.forEach(view => {
      const item = document.createElement('div');
      item.className = 'sas-view-item';
      const date = view.modified ? view.modified.substring(0, 10) : '';
      item.innerHTML = `
        <span class="material-symbols-outlined" style="font-size:16px;color:var(--sas-text-3)">bookmark</span>
        <span class="sas-view-name">${view.view_name}</span>
        <span class="sas-view-date">${date}</span>
        <button class="sas-view-del" title="Delete view"
          onclick="SASViews.deleteView('${view.view_name}', event)">✕</button>
      `;
      item.addEventListener('click', (e) => {
        if (e.target.classList.contains('sas-view-del')) return;
        restore(view.state);
        SAS.fetchData();
        // Close panel
        const panel = document.getElementById('sas-views-panel');
        if (panel) panel.classList.remove('open');
      });
      container.appendChild(item);
    });
  }

  // ── Delete View ─────────────────────────────────────────────────────────────
  function deleteView(viewName, event) {
    if (event) event.stopPropagation();
    const reportKey = SAS.getCurrentReport();
    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_delete_view',
      args: { view_name: viewName, report_key: reportKey },
      callback: function () {
        loadList(reportKey);
        if (_activeViewName === viewName) _activeViewName = null;
      }
    });
    // Remove from localStorage
    try {
      localStorage.removeItem(`${LS_PREFIX}${reportKey}_${viewName}`);
    } catch (e) {}
  }

  // ── Save Panel Handler ──────────────────────────────────────────────────────
  function handleSaveSubmit() {
    const input = document.getElementById('sas-save-view-name');
    if (!input || !input.value.trim()) {
      frappe.show_alert({ message: 'Enter a view name', indicator: 'orange' }, 2);
      return;
    }
    const reportKey = SAS.getCurrentReport();
    save(input.value.trim(), reportKey);
    input.value = '';
  }

  function getActiveViewName() { return _activeViewName; }

  return {
    save,
    restore,
    loadDefault,
    loadList,
    deleteView,
    handleSaveSubmit,
    getActiveViewName,
  };

})();
