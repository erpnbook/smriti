/**
 * sas_grid.js — SMRITI Analytics Studio AG Grid Wrapper
 * Wraps AG Grid Community Edition v32.
 * All column definitions come from sas_api.sas_get_report_metadata().
 * Pivot implementation is SAS-native (swappable without AG Grid Enterprise).
 */
'use strict';

window.SASGrid = (function () {

  let gridApi = null;
  let currentRows = [];
  let currentMeta = {};
  let pivotActive = false;
  let groupCols = [];
  let _formatCurrency, _formatFloat, _formatPercent;

  // ── Currency formatter from SMRITI context ────────────────────────────────
  function _getCurrencySymbol() {
    return (window.frappe && frappe.boot && frappe.boot.sysdefaults &&
      frappe.boot.sysdefaults.currency_symbol) ? frappe.boot.sysdefaults.currency_symbol : '₹';
  }

  // ── Value formatters ───────────────────────────────────────────────────────
  const currencyFormatter = (params) => {
    if (params.value === null || params.value === undefined) return '';
    return `${_getCurrencySymbol()} ${Number(params.value).toLocaleString('en-IN', {
      minimumFractionDigits: 2, maximumFractionDigits: 2
    })}`;
  };

  const floatFormatter = (params) => {
    if (params.value === null || params.value === undefined) return '';
    return Number(params.value).toLocaleString('en-IN', {
      minimumFractionDigits: 2, maximumFractionDigits: 2
    });
  };

  const percentFormatter = (params) => {
    if (params.value === null || params.value === undefined) return '';
    return `${Number(params.value).toFixed(2)}%`;
  };

  const intFormatter = (params) => {
    if (params.value === null || params.value === undefined) return '';
    return Number(params.value).toLocaleString('en-IN');
  };

  // ── Build Cell Class Rules from conditional format metadata ────────────────
  function _buildCellClassRules(rules) {
    const result = {};
    rules.forEach(rule => {
      const { field, op, value, css } = rule;
      if (typeof value === 'string') {
        result[css] = `params.value ${op} "${value}"`;
      } else {
        result[css] = `params.value ${op} ${value}`;
      }
    });
    return result;
  }

  // ── Convert SAS colDefs to AG Grid columnDefs ──────────────────────────────
  function _buildColumnDefs(colDefs, meta) {
    const cfByField = {};
    (meta.conditional_format_rules || []).forEach(r => {
      cfByField[r.field] = cfByField[r.field] || [];
      cfByField[r.field].push(r);
    });

    return colDefs.map((col, idx) => {
      const agCol = {
        ...col,
        // Convert string function references to real functions
        valueFormatter: undefined,
      };

      // Assign value formatters
      if (col.valueFormatter === 'currencyFormatter') agCol.valueFormatter = currencyFormatter;
      else if (col.valueFormatter === 'floatFormatter') agCol.valueFormatter = floatFormatter;
      else if (col.valueFormatter === 'percentFormatter') agCol.valueFormatter = percentFormatter;
      else if (col.type === 'numericColumn') agCol.valueFormatter = intFormatter;

      // Attach header Explain ⓘ button via headerComponentParams
      if (meta.explain_enabled) {
        agCol.headerComponentParams = {
          template: `
            <div class="ag-cell-label-container" role="presentation">
              <span ref="eMenu" class="ag-header-icon ag-header-cell-menu-button"></span>
              <div ref="eLabel" class="ag-header-cell-label" role="presentation">
                <span ref="eText" class="ag-header-cell-text" role="columnheader"></span>
                <span ref="eFilter" class="ag-header-icon ag-header-label-icon ag-filter-icon ag-hidden"></span>
                <span ref="eSortOrder" class="ag-header-icon ag-header-label-icon ag-sort-order ag-hidden"></span>
                <span ref="eSortAsc" class="ag-header-icon ag-header-label-icon ag-sort-ascending-icon ag-hidden"></span>
                <span ref="eSortDesc" class="ag-header-icon ag-header-label-icon ag-sort-descending-icon ag-hidden"></span>
                <span ref="eSortNone" class="ag-header-icon ag-header-label-icon ag-sort-none-icon ag-hidden"></span>
                <span class="sas-explain-btn" title="Explain this field"
                  onclick="SASExplain.open('${col.field}')"
                  style="cursor:pointer;font-size:13px;opacity:0.6;margin-left:4px;color:var(--sas-accent)">ⓘ</span>
              </div>
            </div>
          `
        };
      }

      // Cell class rules for conditional formatting
      if (cfByField[col.field]) {
        const rules = {};
        cfByField[col.field].forEach(r => {
          if (typeof r.value === 'string') {
            rules[r.css] = (params) => params.value == r.value;
          } else if (r.op === '<')   rules[r.css] = (p) => p.value < r.value;
          else if (r.op === '<=')    rules[r.css] = (p) => p.value <= r.value;
          else if (r.op === '>')     rules[r.css] = (p) => p.value > r.value;
          else if (r.op === '>=')    rules[r.css] = (p) => p.value >= r.value;
          else if (r.op === '==')    rules[r.css] = (p) => p.value == r.value;
          else if (r.op === '!=')    rules[r.css] = (p) => p.value != r.value;
        });
        agCol.cellClassRules = rules;
      }

      return agCol;
    });
  }

  // ── Grid Initialization ────────────────────────────────────────────────────
  function init(containerEl, meta, rows) {
    if (!containerEl) return;
    currentMeta = meta || {};
    currentRows = rows || [];

    const colDefs = _buildColumnDefs(meta.col_defs || [], meta);

    const gridOptions = {
      // Column definitions
      columnDefs: colDefs,
      defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
        enableRowGroup: true,
        enableValue: true,
        enablePivot: true,
        minWidth: 80,
      },

      // Row model
      rowData: rows,
      rowModelType: 'clientSide',

      // Row grouping (Community Edition)
      groupDisplayType: 'groupRows',
      groupIncludeFooter: true,
      groupIncludeTotalFooter: false,  // We use pinned bottom instead
      animateRows: true,
      rowGroupPanelShow: 'onlyWhenGrouping',

      // Selection
      rowSelection: 'multiple',
      suppressRowClickSelection: true,

      // Pagination (handled by SAS, not AG Grid native pagination)
      suppressPaginationPanel: true,

      // Performance
      suppressColumnVirtualisation: false,
      rowBuffer: 10,
      maxBlocksInCache: 10,

      // Theme
      // Applied via .ag-theme-smriti class on container

      // Status bar
      statusBar: {
        statusPanels: [
          { statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' },
          { statusPanel: 'agAggregationComponent', align: 'right' },
        ],
      },

      // Sidebar (Community)
      sideBar: {
        toolPanels: [
          {
            id: 'columns',
            labelDefault: 'Columns',
            labelKey: 'columns',
            iconKey: 'columns',
            toolPanel: 'agColumnsToolPanel',
            toolPanelParams: { suppressPivotMode: false, suppressValues: false },
          },
          {
            id: 'filters',
            labelDefault: 'Filters',
            labelKey: 'filters',
            iconKey: 'filter',
            toolPanel: 'agFiltersToolPanel',
          },
        ],
        defaultToolPanel: '',
      },

      // Aggregation functions
      aggFuncs: {
        'sum': params => params.values.reduce((a, b) => (a || 0) + (b || 0), 0),
        'avg': params => {
          const vals = params.values.filter(v => v !== null && v !== undefined);
          return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
        },
        'count': params => params.values.length,
        'min': params => Math.min(...params.values.filter(v => v !== null)),
        'max': params => Math.max(...params.values.filter(v => v !== null)),
      },

      // Events
      onSortChanged: () => SAS.fetchData(),
      onFilterChanged: () => _updateRowCount(),
      onColumnResized: () => {},
      onColumnMoved: () => {},
      onGridReady: (params) => {
        gridApi = params.api;
        _updateColChooser();
        sizeToFit();
      },
      onFirstDataRendered: () => {
        sizeToFit();
      },

      // Context menu (right-click)
      getContextMenuItems: (params) => {
        return [
          'copy', 'copyWithHeaders', 'separator',
          {
            name: `Explain "${params.column ? params.column.getColDef().headerName : ''}"`,
            icon: '<span style="font-size:13px">ⓘ</span>',
            action: () => {
              if (params.column && window.SASExplain) {
                SASExplain.open(params.column.getColId());
              }
            }
          },
          'separator', 'export',
        ];
      },
    };

    // Clear old grid
    containerEl.innerHTML = '';

    // Create grid
    const gridDiv = document.createElement('div');
    gridDiv.className = 'ag-theme-smriti';
    gridDiv.style.cssText = 'width:100%;height:100%;';
    containerEl.appendChild(gridDiv);

    try {
      const grid = agGrid.createGrid(gridDiv, gridOptions);
      if (!gridApi && grid && grid.api) gridApi = grid.api;
    } catch (e) {
      console.error('[SASGrid] AG Grid init failed:', e);
    }
  }

  // ── Data ───────────────────────────────────────────────────────────────────
  function setData(rows, meta, totalCount, page, totalPages) {
    currentRows = rows;
    currentMeta = meta || currentMeta;

    if (!gridApi) {
      // Initialize grid if first time
      const container = document.getElementById('sas-grid-container');
      if (container) {
        init(container, meta, rows);
        return;
      }
    }

    if (gridApi) {
      try {
        // Update col defs if meta changed
        const colDefs = _buildColumnDefs(meta.col_defs || currentMeta.col_defs || [], currentMeta);
        gridApi.setGridOption('columnDefs', colDefs);
        gridApi.setGridOption('rowData', rows);
      } catch (e) {
        console.warn('[SASGrid] setData error:', e);
      }
    }

    _updateRowCount();
  }

  function setGrandTotals(totalsRow) {
    if (!gridApi || !totalsRow) return;
    try {
      gridApi.setGridOption('pinnedBottomRowData', [totalsRow]);
    } catch (e) {}
  }

  function getCurrentRows() {
    if (!gridApi) return currentRows;
    const rows = [];
    try {
      gridApi.forEachNodeAfterFilter(node => {
        if (!node.group && node.data) rows.push(node.data);
      });
    } catch (e) {
      return currentRows;
    }
    return rows;
  }

  // ── Column Chooser ─────────────────────────────────────────────────────────
  function _updateColChooser() {
    if (!gridApi) return;
    const container = document.getElementById('sas-col-chooser-body');
    if (!container) return;

    container.innerHTML = '';
    const cols = gridApi.getColumns() || [];
    cols.forEach(col => {
      try {
        const colDef = col.getColDef() || {};
        const colId = col.getColId() || '';
        const item = document.createElement('div');
        item.className = 'sas-col-chooser-item';
        item.innerHTML = `
          <input type="checkbox" id="col-${colId}" ${col.isVisible() ? 'checked' : ''}>
          <label for="col-${colId}">${colDef.headerName || colId}</label>
        `;
        const input = item.querySelector('input');
        if (!input) {
          console.warn('[SASGrid] Column chooser querySelector failed for column:', {
            id: colId,
            headerName: colDef.headerName,
            visible: col.isVisible()
          });
          return;
        }
        input.addEventListener('change', (e) => {
          gridApi.setColumnVisible(colId, e.target.checked);
        });
        container.appendChild(item);
      } catch (err) {
        console.error('[SASGrid] Error processing column in chooser:', err, col);
      }
    });
  }

  // ── Group By ───────────────────────────────────────────────────────────────
  function toggleGroupPanel() {
    if (!gridApi) return;
    const panel = document.getElementById('sas-group-panel');
    if (panel) {
      panel.classList.toggle('open');
    }
    // Open AG Grid columns tool panel for row grouping
    try {
      const state = gridApi.isSideBarVisible() ? '' : 'columns';
      gridApi.setSideBarVisible(true);
      gridApi.openToolPanel('columns');
    } catch (e) {}
  }

  function setGroupByCols(cols) {
    groupCols = cols;
    if (!gridApi) return;
    try {
      const colState = gridApi.getColumnState().map(c => ({
        ...c,
        rowGroup: cols.includes(c.colId),
        rowGroupIndex: cols.includes(c.colId) ? cols.indexOf(c.colId) : null,
      }));
      gridApi.applyColumnState({ state: colState, applyOrder: false });
    } catch (e) {}
  }

  function getGroupByCols() { return groupCols; }

  // ── Pivot ──────────────────────────────────────────────────────────────────
  function togglePivot() {
    if (!gridApi) return;
    pivotActive = !pivotActive;
    try {
      gridApi.setGridOption('pivotMode', pivotActive);
    } catch (e) {}

    const btn = document.getElementById('sas-btn-pivot');
    if (btn) btn.classList.toggle('active', pivotActive);

    // Update toolbar label
    const label = document.getElementById('sas-pivot-label');
    if (label) label.textContent = pivotActive ? 'Pivot On' : 'Pivot';
  }

  // ── Sorting ────────────────────────────────────────────────────────────────
  function getSortModel() {
    if (!gridApi) return [];
    try {
      return gridApi.getColumnState()
        .filter(c => c.sort)
        .sort((a, b) => (a.sortIndex || 0) - (b.sortIndex || 0))
        .map(c => ({ colId: c.colId, sort: c.sort }));
    } catch (e) {
      return [];
    }
  }

  // ── Quick Filter ───────────────────────────────────────────────────────────
  function setQuickFilter(text) {
    if (!gridApi) return;
    try {
      gridApi.setGridOption('quickFilterText', text);
    } catch (e) {}
    _updateRowCount();
  }

  // ── Layout State (for Saved Views) ────────────────────────────────────────
  function getLayoutState() {
    if (!gridApi) return {};
    let colState = [], filterModel = {}, sortModel = [];
    try {
      colState = gridApi.getColumnState() || [];
      filterModel = gridApi.getFilterModel() || {};
    } catch (e) {}
    return {
      column_state: colState,
      filter_model: filterModel,
      sort_model: getSortModel(),
      group_by_cols: groupCols,
      pivot_active: pivotActive,
    };
  }

  function restoreLayoutState(layoutState) {
    if (!gridApi || !layoutState) return;
    try {
      if (layoutState.column_state) {
        gridApi.applyColumnState({ state: layoutState.column_state, applyOrder: true });
      }
      if (layoutState.filter_model) {
        gridApi.setFilterModel(layoutState.filter_model);
      }
      if (layoutState.group_by_cols) {
        groupCols = layoutState.group_by_cols;
      }
      if (layoutState.pivot_active !== undefined) {
        pivotActive = layoutState.pivot_active;
        gridApi.setGridOption('pivotMode', pivotActive);
      }
    } catch (e) {
      console.warn('[SASGrid] restoreLayoutState error:', e);
    }
  }

  // ── Export (native CSV) ───────────────────────────────────────────────────
  function exportCSV(filename) {
    if (!gridApi) return;
    try {
      gridApi.exportDataAsCsv({
        fileName: filename || `smriti_${SAS.getCurrentReport() || 'report'}_${_today()}.csv`,
        allColumns: false,
        onlySelected: false,
        skipPinnedBottom: false,
      });
    } catch (e) {
      console.error('[SASGrid] CSV export failed:', e);
    }
  }

  // ── Layout Utilities ───────────────────────────────────────────────────────
  function sizeToFit() {
    if (!gridApi) return;
    try { gridApi.sizeColumnsToFit(); } catch (e) {}
  }

  function _updateRowCount() {
    if (!gridApi) return;
    let count = 0;
    try {
      gridApi.forEachNodeAfterFilter(n => { if (!n.group) count++; });
    } catch (e) {}
    const el = document.getElementById('sas-status-rows');
    if (el) el.innerHTML = `Rows: <strong>${count.toLocaleString()}</strong>`;
  }

  function _today() {
    return new Date().toISOString().split('T')[0];
  }

  // ── Public API ─────────────────────────────────────────────────────────────
  return {
    init,
    setData,
    setGrandTotals,
    getCurrentRows,
    getSortModel,
    getGroupByCols,
    setGroupByCols,
    setQuickFilter,
    toggleGroupPanel,
    togglePivot,
    getLayoutState,
    restoreLayoutState,
    exportCSV,
    sizeToFit,
    get api() { return gridApi; },
  };

})();
