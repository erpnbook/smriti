/**
 * sas_charts.js — SMRITI Analytics Studio Chart Panel
 * Uses Chart.js v4 (CDN). Builds charts from current AG Grid visible data.
 * Supports: Bar, Line, Pie, Area, Stacked Bar, Donut.
 * All colors from SMRITI CSS token system via getComputedStyle.
 */
'use strict';

window.SASCharts = (function () {

  let chartInstance = null;
  const CANVAS_ID = 'sas-chart-canvas';

  // ── Token colors (no hardcoded hex in JS) ─────────────────────────────────
  function _tok(name) {
    return getComputedStyle(document.documentElement)
      .getPropertyValue(name).trim() || '#2563EB';
  }

  function _palette(count) {
    const base = [
      '--smriti-color-brand-primary',
      '--smriti-color-brand-light',
      '--smriti-color-status-success',
      '--smriti-color-status-warning',
      '--smriti-color-status-danger',
      '--smriti-color-brand-overlay-xs',
    ];
    // Fallback palette using CSS variable alpha variants
    const fallback = ['#2563EB','#60A5FA','#10B981','#F59E0B','#EF4444','#8B5CF6','#EC4899','#14B8A6'];
    const result = [];
    for (let i = 0; i < count; i++) {
      result.push(i < base.length ? _tok(base[i]) : fallback[i % fallback.length]);
    }
    return result;
  }

  // ── Render / Update ────────────────────────────────────────────────────────
  function render(rows, meta, chartConfig) {
    const canvas = document.getElementById(CANVAS_ID);
    if (!canvas) return;

    if (!rows || rows.length === 0) {
      _showEmpty(canvas);
      return;
    }

    const type = (chartConfig && chartConfig.type) || 'bar';
    const xField = (chartConfig && chartConfig.x) || _inferXField(meta);
    const yField = (chartConfig && chartConfig.y) || _inferYField(meta);

    if (!xField || !yField) {
      _showEmpty(canvas, 'Select X and Y fields to generate chart.');
      return;
    }

    // Aggregate data (group by xField, sum yField)
    const aggregated = _aggregate(rows, xField, yField, type);

    // Build Chart.js config
    const cfg = _buildChartConfig(type, aggregated, xField, yField, meta);

    // Destroy old chart
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }

    try {
      chartInstance = new Chart(canvas, cfg);
    } catch (e) {
      console.error('[SASCharts] Chart.js error:', e);
    }
  }

  function update(rows, meta) {
    if (!chartInstance) return;
    const xField = chartInstance._sasXField;
    const yField = chartInstance._sasYField;
    const type = chartInstance._sasType;
    if (!xField || !yField) return;

    const aggregated = _aggregate(rows, xField, yField, type);
    chartInstance.data.labels = aggregated.labels;
    chartInstance.data.datasets[0].data = aggregated.values;
    chartInstance.update('active');
  }

  function setType(type, rows, meta, chartConfig) {
    render(rows, meta, { ...(chartConfig || {}), type });
  }

  function resize() {
    if (chartInstance) chartInstance.resize();
  }

  // ── Data Aggregation ───────────────────────────────────────────────────────
  function _aggregate(rows, xField, yField, type) {
    const map = new Map();
    rows.forEach(row => {
      const xVal = String(row[xField] || '');
      const yVal = parseFloat(row[yField]) || 0;
      map.set(xVal, (map.get(xVal) || 0) + yVal);
    });

    // Sort by value for better readability (except line/area — keep chronological)
    let entries = Array.from(map.entries());
    if (!['line', 'area'].includes(type)) {
      entries.sort((a, b) => b[1] - a[1]);
    }

    // Cap at 20 items for readability
    if (entries.length > 20) entries = entries.slice(0, 20);

    return {
      labels: entries.map(e => e[0]),
      values: entries.map(e => e[1]),
    };
  }

  // ── Chart.js Config Builder ────────────────────────────────────────────────
  function _buildChartConfig(type, data, xField, yField, meta) {
    const colors = _palette(data.labels.length);
    const accent = _tok('--smriti-color-brand-primary');
    const text2 = _tok('--smriti-color-text-secondary') || '#94a3b8';
    const border = _tok('--smriti-color-border-default') || '#334155';
    const bg = _tok('--smriti-color-bg-secondary') || '#1e293b';

    Chart.defaults.color = text2;
    Chart.defaults.borderColor = border;
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;

    const isCurrency = (meta.columns || []).some(c =>
      c.fieldname === yField && c.fieldtype === 'Currency'
    );

    const tooltipCallback = (ctx) => {
      const val = ctx.parsed.y !== undefined ? ctx.parsed.y : ctx.parsed;
      if (isCurrency) {
        const sym = (frappe.boot && frappe.boot.sysdefaults && frappe.boot.sysdefaults.currency_symbol) || '₹';
        return ` ${sym} ${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
      }
      return ` ${Number(val).toLocaleString('en-IN')}`;
    };

    const commonOpts = {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 400, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: type === 'pie' || type === 'donut', position: 'right' },
        tooltip: {
          backgroundColor: bg,
          titleColor: text2,
          bodyColor: text2,
          borderColor: border,
          borderWidth: 1,
          callbacks: { label: tooltipCallback },
        },
      },
      scales: {
        x: {
          grid: { color: border, lineWidth: 0.5 },
          ticks: { maxRotation: 45, color: text2 },
        },
        y: {
          grid: { color: border, lineWidth: 0.5 },
          ticks: {
            color: text2,
            callback: (val) => {
              if (isCurrency) {
                const sym = (frappe.boot && frappe.boot.sysdefaults && frappe.boot.sysdefaults.currency_symbol) || '₹';
                if (val >= 100000) return `${sym}${(val / 100000).toFixed(1)}L`;
                if (val >= 1000)   return `${sym}${(val / 1000).toFixed(1)}K`;
                return `${sym}${val}`;
              }
              return val;
            }
          },
          beginAtZero: true,
        },
      },
    };

    let chartType = type;
    let datasets = [];
    const isAreaOrLine = type === 'area' || type === 'line';

    if (type === 'pie' || type === 'donut') {
      chartType = 'doughnut';
      const cutout = type === 'donut' ? '60%' : '0%';
      datasets = [{
        data: data.values,
        backgroundColor: _palette(data.labels.length).map(c => c + 'cc'),
        borderColor: _palette(data.labels.length),
        borderWidth: 1.5,
      }];
      delete commonOpts.scales;
      commonOpts.cutout = cutout;
    } else if (type === 'stacked_bar') {
      chartType = 'bar';
      datasets = [{
        label: yField.replace(/_/g, ' '),
        data: data.values,
        backgroundColor: accent + 'cc',
        borderColor: accent,
        borderWidth: 1.5,
        borderRadius: 4,
      }];
      commonOpts.scales.x.stacked = true;
      commonOpts.scales.y.stacked = true;
    } else {
      datasets = [{
        label: yField.replace(/_/g, ' '),
        data: data.values,
        backgroundColor: isAreaOrLine
          ? accent + '22'
          : _palette(data.labels.length).map(c => c + 'cc'),
        borderColor: isAreaOrLine ? accent : _palette(data.labels.length),
        borderWidth: isAreaOrLine ? 2 : 1.5,
        borderRadius: type === 'bar' ? 4 : 0,
        fill: type === 'area',
        tension: isAreaOrLine ? 0.4 : 0,
        pointBackgroundColor: isAreaOrLine ? accent : undefined,
        pointRadius: isAreaOrLine ? 3 : undefined,
      }];
      chartType = type === 'area' ? 'line' : type;
    }

    // Attach meta for update()
    const cfg = {
      type: chartType,
      data: { labels: data.labels, datasets },
      options: commonOpts,
    };

    // Store fields for update()
    setTimeout(() => {
      if (chartInstance) {
        chartInstance._sasXField = xField;
        chartInstance._sasYField = yField;
        chartInstance._sasType = type;
      }
    }, 100);

    return cfg;
  }

  // ── Field Inference ────────────────────────────────────────────────────────
  function _inferXField(meta) {
    const cols = meta.columns || [];
    // Prefer date field
    const dateCol = cols.find(c => c.fieldtype === 'Date');
    if (dateCol) return dateCol.fieldname;
    // Fallback: first non-numeric
    const textCol = cols.find(c => !['Currency','Float','Int','Percent'].includes(c.fieldtype));
    return textCol ? textCol.fieldname : (cols[0] ? cols[0].fieldname : null);
  }

  function _inferYField(meta) {
    const cols = meta.columns || [];
    const numCol = cols.find(c => ['Currency','Float','Int'].includes(c.fieldtype));
    return numCol ? numCol.fieldname : null;
  }

  // ── Empty State ────────────────────────────────────────────────────────────
  function _showEmpty(canvas, msg) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = _tok('--smriti-color-text-muted') || '#475569';
    ctx.font = '13px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(msg || 'No data to chart', canvas.width / 2, canvas.height / 2);
  }

  return { render, update, setType, resize };

})();
