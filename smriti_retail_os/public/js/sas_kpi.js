/**
 * sas_kpi.js — SMRITI Analytics Studio KPI Cards
 * Renders animated KPI cards at the top of each report.
 * Values from sas_api.sas_get_kpi_summary().
 */
'use strict';

window.SASKpi = (function () {

  const CONTAINER_ID = 'sas-kpi-row';

  function _getCurrencySymbol() {
    return (window.frappe && frappe.boot && frappe.boot.sysdefaults &&
      frappe.boot.sysdefaults.currency_symbol) || '₹';
  }

  function _formatValue(value, fieldtype) {
    if (value === null || value === undefined) return '—';
    const sym = _getCurrencySymbol();
    if (fieldtype === 'Currency') {
      if (value >= 10000000) return `${sym} ${(value / 10000000).toFixed(2)} Cr`;
      if (value >= 100000)   return `${sym} ${(value / 100000).toFixed(2)} L`;
      if (value >= 1000)     return `${sym} ${(value / 1000).toFixed(1)} K`;
      return `${sym} ${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    }
    if (fieldtype === 'Percent') return `${Number(value).toFixed(2)}%`;
    if (fieldtype === 'Float')   return Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2 });
    if (fieldtype === 'Int')     return Number(value).toLocaleString('en-IN');
    // Counts (Data type)
    if (value >= 1000) return Number(value).toLocaleString('en-IN');
    return String(value);
  }

  function load(reportKey, filters, compareFilters) {
    const container = document.getElementById(CONTAINER_ID);
    if (!container) return;

    // Show shimmer while loading
    _showShimmer(container);

    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_get_kpi_summary',
      args: {
        report_key: reportKey,
        filters: JSON.stringify(filters || {}),
        compare_filters: compareFilters ? JSON.stringify(compareFilters) : null,
      },
      callback: function (r) {
        const cards = r.message || [];
        render(container, cards);
      },
      error: function () {
        container.innerHTML = '';
      }
    });
  }

  function render(container, cards) {
    container.innerHTML = '';

    if (!cards || cards.length === 0) {
      container.closest('.sas-kpi-row') && (container.closest('.sas-kpi-row').classList.add('hidden'));
      return;
    }

    cards.forEach((card, idx) => {
      const el = document.createElement('div');
      el.className = 'sas-kpi-card';
      el.style.animationDelay = `${idx * 60}ms`;
      el.style.animation = 'sas-fade-up 0.3s ease both';

      const formattedVal = _formatValue(card.value, card.fieldtype);
      const hasDelta = card.change_pct !== null && card.change_pct !== undefined;
      const dir = card.change_dir || 'neutral';
      const arrow = dir === 'up' ? '▲' : dir === 'down' ? '▼' : '—';
      const deltaHtml = hasDelta
        ? `<div class="sas-kpi-delta ${dir}">
             ${arrow} ${Math.abs(card.change_pct)}%
             <span style="font-weight:400;color:var(--sas-text-3)">vs prev</span>
           </div>`
        : `<div class="sas-kpi-delta neutral">—</div>`;

      el.innerHTML = `
        <div class="sas-kpi-label">${card.label}</div>
        <div class="sas-kpi-value" id="kpi-val-${card.fieldname}">${formattedVal}</div>
        ${deltaHtml}
      `;

      // Counter animation for numeric values
      if (typeof card.value === 'number' && card.value > 0) {
        _animateCounter(el.querySelector(`#kpi-val-${card.fieldname}`), card.value, card.fieldtype);
      }

      container.appendChild(el);
    });

    // Add CSS animation keyframes inline if not already injected
    _injectKeyframes();
  }

  function _animateCounter(el, targetVal, fieldtype) {
    if (!el) return;
    const duration = 800;
    const start = performance.now();

    function step(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = targetVal * eased;
      el.textContent = _formatValue(current, fieldtype);
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = _formatValue(targetVal, fieldtype);
    }
    requestAnimationFrame(step);
  }

  function _showShimmer(container) {
    container.innerHTML = '';
    for (let i = 0; i < 4; i++) {
      const shimmer = document.createElement('div');
      shimmer.className = 'sas-kpi-card';
      shimmer.style.cssText = 'min-width:160px;animation:sas-pulse 1.4s ease infinite';
      shimmer.innerHTML = `
        <div style="height:10px;border-radius:4px;background:var(--sas-border);width:60%;margin-bottom:10px"></div>
        <div style="height:24px;border-radius:4px;background:var(--sas-border);width:80%;margin-bottom:8px"></div>
        <div style="height:10px;border-radius:4px;background:var(--sas-border);width:40%"></div>
      `;
      container.appendChild(shimmer);
    }
  }

  function _injectKeyframes() {
    if (document.getElementById('sas-kpi-keyframes')) return;
    const style = document.createElement('style');
    style.id = 'sas-kpi-keyframes';
    style.textContent = `
      @keyframes sas-fade-up {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      @keyframes sas-pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.5; }
      }
    `;
    document.head.appendChild(style);
  }

  return { load, render };

})();
