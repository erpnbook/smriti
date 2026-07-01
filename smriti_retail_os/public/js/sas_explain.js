/**
 * sas_explain.js — SMRITI Analytics Studio Explain Panel
 * Opens a full Formula Explain modal for any column field.
 * Data from sas_api.sas_get_formula_explain().
 * Follows Rule 10: Explainability-First Development.
 */
'use strict';

window.SASExplain = (function () {

  const OVERLAY_ID = 'sas-explain-overlay';

  function open(fieldname) {
    const reportKey = SAS.getCurrentReport();
    if (!reportKey) return;

    const meta = SAS.getCurrentMeta();
    const col = (meta.columns || []).find(c => c.fieldname === fieldname);
    const label = col ? col.label : fieldname.replace(/_/g, ' ');

    // Show loading modal
    _renderLoading(label);
    _showOverlay();

    frappe.call({
      method: 'smriti_retail_os.analytics_studio.sas_api.sas_get_formula_explain',
      args: { report_key: reportKey, fieldname },
      callback: function (r) {
        const data = r.message || {};
        _renderExplain(data);
      },
      error: function () {
        _renderError(fieldname);
      }
    });
  }

  function close() {
    const overlay = document.getElementById(OVERLAY_ID);
    if (overlay) overlay.classList.remove('open');
  }

  // ── Render Helpers ──────────────────────────────────────────────────────────
  function _showOverlay() {
    const overlay = document.getElementById(OVERLAY_ID);
    if (overlay) overlay.classList.add('open');
  }

  function _renderLoading(label) {
    const modal = _getModal();
    modal.innerHTML = `
      <div class="sas-explain-header">
        <div class="sas-explain-icon">ⓘ</div>
        <div class="sas-explain-title">
          <h3>${label}</h3>
          <p>Loading explanation...</p>
        </div>
        <button class="sas-explain-close" onclick="SASExplain.close()">✕</button>
      </div>
      <div class="sas-explain-body" style="align-items:center;justify-content:center">
        <div class="sas-spinner"></div>
        <p style="color:var(--sas-text-3);margin-top:12px">Loading formula...</p>
      </div>
    `;
  }

  function _renderExplain(data) {
    const modal = _getModal();

    const label = data.label || data.fieldname;
    const formula = data.formula;
    const variables = data.variables || [];
    const example = data.worked_example;
    const meaning = data.business_meaning;
    const interpretation = data.interpretation;
    const action = data.recommended_action;
    const relKPIs = data.related_kpis || [];
    const relReports = data.related_reports || [];
    const source = data.data_source;
    const version = data.formula_version;
    const updatedAt = data.last_updated ? data.last_updated.substring(0, 10) : null;
    const approvedBy = data.approved_by;

    modal.innerHTML = `
      <div class="sas-explain-header">
        <div class="sas-explain-icon">ⓘ</div>
        <div class="sas-explain-title">
          <h3>${label}</h3>
          <p>SMRITI Explain — Formula Transparency</p>
        </div>
        <button class="sas-explain-close" onclick="SASExplain.close()">✕</button>
      </div>
      <div class="sas-explain-body">

        ${meaning ? `
        <div class="sas-explain-section">
          <h4>Business Meaning</h4>
          <p>${meaning}</p>
        </div>` : ''}

        ${formula ? `
        <div class="sas-explain-section">
          <h4>Formula</h4>
          <div class="sas-formula-block">${formula}</div>
        </div>` : ''}

        ${variables.length ? `
        <div class="sas-explain-section">
          <h4>Variables</h4>
          <div class="sas-explain-vars">
            ${variables.map(v => `
              <div class="sas-explain-var-item">
                <span class="sas-explain-var-name">${v.name || v}</span>
                <span class="sas-explain-var-desc">${v.description || v.source || ''}</span>
              </div>
            `).join('')}
          </div>
        </div>` : ''}

        ${example ? `
        <div class="sas-explain-section">
          <h4>Worked Example</h4>
          <div class="sas-formula-block" style="font-family:var(--sas-font);font-size:12px">${example}</div>
        </div>` : ''}

        ${interpretation ? `
        <div class="sas-explain-section">
          <h4>Interpretation Guide</h4>
          <div class="sas-interp-bands">
            ${_parseInterpretation(interpretation)}
          </div>
        </div>` : ''}

        ${action ? `
        <div class="sas-explain-section">
          <h4>Recommended Action</h4>
          <p>${action}</p>
        </div>` : ''}

        ${source ? `
        <div class="sas-explain-section">
          <h4>Data Source</h4>
          <p style="font-family:var(--sas-font-mono);font-size:12px">${source}</p>
        </div>` : ''}

        ${(relKPIs.length || relReports.length) ? `
        <div class="sas-explain-section">
          ${relKPIs.length ? `
            <h4>Related KPIs</h4>
            <div class="sas-explain-tags">
              ${relKPIs.map(k => `<span class="sas-explain-tag">${k}</span>`).join('')}
            </div>
          ` : ''}
          ${relReports.length ? `
            <h4 style="margin-top:12px">Related Reports</h4>
            <div class="sas-explain-tags">
              ${relReports.map(r => `
                <span class="sas-explain-tag" style="cursor:pointer;color:var(--sas-accent)"
                  onclick="SASExplain.close();SAS.loadReport('${r}')">
                  ${r.replace(/_/g, ' ')}
                </span>
              `).join('')}
            </div>
          ` : ''}
        </div>` : ''}

        <div class="sas-explain-section" style="border-top:1px solid var(--sas-border);padding-top:14px;margin-top:4px">
          <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:11px;color:var(--sas-text-3)">
            ${version ? `<span>Formula v${version}</span>` : ''}
            ${updatedAt ? `<span>Updated: ${updatedAt}</span>` : ''}
            ${approvedBy ? `<span>Approved by: ${approvedBy}</span>` : ''}
          </div>
        </div>

      </div>
    `;
  }

  function _renderError(fieldname) {
    const modal = _getModal();
    modal.innerHTML = `
      <div class="sas-explain-header">
        <div class="sas-explain-icon" style="color:var(--sas-danger)">⚠</div>
        <div class="sas-explain-title">
          <h3>${fieldname}</h3>
          <p>No explanation available</p>
        </div>
        <button class="sas-explain-close" onclick="SASExplain.close()">✕</button>
      </div>
      <div class="sas-explain-body" style="align-items:center;justify-content:center;color:var(--sas-text-3)">
        <p>No formula or business definition found for this field.<br>
        Add it to the SMRITI Formula Registry to enable Explain.</p>
      </div>
    `;
  }

  function _parseInterpretation(text) {
    // Try to parse band patterns like "< 20% = Critical | 20-30% = Monitor | > 30% = Healthy"
    const bands = text.split('|').map(b => b.trim());
    if (bands.length > 1) {
      return bands.map(band => {
        const isGood = /healthy|good|normal/i.test(band);
        const isBad  = /critical|danger|bad|poor/i.test(band);
        const isWarn = /monitor|warning|caution/i.test(band);
        const cls = isGood ? 'success' : isBad ? 'danger' : isWarn ? 'warning' : 'warning';
        const icon = isGood ? '✓' : isBad ? '✕' : '●';
        return `<div class="sas-interp-band ${cls}">${icon} ${band}</div>`;
      }).join('');
    }
    return `<p style="font-size:12px;color:var(--sas-text-2)">${text}</p>`;
  }

  function _getModal() {
    let modal = document.getElementById('sas-explain-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'sas-explain-modal';
      modal.className = 'sas-explain-modal';
      const overlay = document.getElementById(OVERLAY_ID);
      if (overlay) overlay.appendChild(modal);
    }
    return modal;
  }

  // ── Click-outside to close ──────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById(OVERLAY_ID);
    if (overlay) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) close();
      });
    }

    // Keyboard ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') close();
    });
  });

  return { open, close };

})();
