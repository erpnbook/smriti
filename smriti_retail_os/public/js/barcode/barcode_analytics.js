/**
 * @file: smriti_retail_os/public/js/barcode/barcode_analytics.js
 * @description: Analytics dashboards, print logs scanner, and version history.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: MIT
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

async function openAnalyticsModal() {
    openModal('analytics-modal');
    const tbody = document.getElementById('an-history-tbody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-sub);">Loading print analytics...</td></tr>';
    
    try {
        const stats = await api('smriti_retail_os.barcode_api.get_print_analytics');
        
        const tl = document.getElementById('an-total-labels');
        const sj = document.getElementById('an-success-jobs');
        const fj = document.getElementById('an-failed-jobs');
        const al = document.getElementById('an-avg-labels');
        const mt = document.getElementById('an-most-used-temp');
        const mp = document.getElementById('an-most-used-printer');
        
        if (tl) tl.textContent = stats.total_labels || 0;
        if (sj) sj.textContent = stats.success_jobs || 0;
        if (fj) fj.textContent = stats.failed_jobs || 0;
        
        const avg = stats.total_jobs > 0 ? Math.round(stats.total_labels / stats.total_jobs) : 0;
        if (al) al.textContent = avg;
        
        if (mt) mt.textContent = stats.top_template || 'None';
        if (mp) mp.textContent = stats.top_printer || 'None';
        
        if (tbody) {
            if (!stats.history || !stats.history.length) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">No print run history found</td></tr>';
                return;
            }
            
            tbody.innerHTML = stats.history.map(h => {
                const statusClass = h.status === 'Success' ? 'style="color:var(--success); font-weight:700;"' : 'style="color:var(--danger); font-weight:700;"';
                return `
                    <tr>
                        <td style="font-family:monospace; color:var(--text-muted);">${h.date}</td>
                        <td style="font-weight:600; color:var(--text);">${h.template}</td>
                        <td style="font-family:monospace;">${h.printer}</td>
                        <td style="text-align:center; font-weight:700; color:var(--accent);">${h.labels}</td>
                        <td style="text-align:center;" ${statusClass}>${h.status}</td>
                    </tr>
                `;
            }).join('');
        }
    } catch(e) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--danger);">Failed to load: ${e.message}</td></tr>`;
    }
}

// ── Token Help mapping cache-backed loader ──
async function loadTokenReference() {
    if (window.BarcodeStudioState.tokenReferenceCache) {
        populateTokenReferenceUI(window.BarcodeStudioState.tokenReferenceCache);
        return;
    }
    
    try {
        const ref = await api('smriti_retail_os.barcode_api.get_field_mapping_reference');
        window.BarcodeStudioState.tokenReferenceCache = ref;
        populateTokenReferenceUI(ref);
    } catch(e) {
        console.error('Failed to load token reference helper: ', e);
    }
}

function populateTokenReferenceUI(ref) {
    const tbody = document.getElementById('token-tbody');
    if (tbody) {
        tbody.innerHTML = ref.map(r => `
            <tr>
                <td><span class="token-badge" style="font-family:monospace; background:var(--barcode-brand-md); color:var(--primary-lt); padding:2px 6px; border-radius:4px; font-weight:600;">${r.placeholder}</span></td>
                <td>
                    <div style="font-weight:600;color:var(--text);">${r.item_master_field}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">${r.description}</div>
                </td>
                <td style="font-family:monospace;color:var(--primary-lt);">${r.example}</td>
            </tr>
        `).join('');
    }
}

function openTokenHelp() {
    openModal('token-modal');
}

async function loadVersionHistory(templateName) {
    const dropdown = document.getElementById('design-version-history');
    if (!dropdown) return;
    
    dropdown.innerHTML = '<option value="">-- Active (Latest) --</option>';
    if (!templateName) return;
    
    try {
        const versions = await api('smriti_retail_os.barcode_api.get_print_template_versions', {
            template_name: templateName
        });
        
        if (versions && versions.length > 0) {
            versions.forEach(v => {
                const opt = document.createElement('option');
                opt.value = v.version_number;
                let dtStr = '';
                if (v.change_timestamp) {
                    const dt = new Date(v.change_timestamp);
                    dtStr = dt.toLocaleDateString() + ' ' + dt.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                }
                opt.textContent = `v${v.version_number} (${dtStr} by ${v.changed_by || 'Unknown'})`;
                dropdown.appendChild(opt);
            });
        }
    } catch(e) {
        console.error("Failed to load version history", e);
    }
}

async function restoreVersionFromHistory(versionNumber) {
    if (!versionNumber) return;
    
    const confirmRestore = confirm(`Are you sure you want to restore version ${versionNumber}? Unsaved changes on the active template will be lost.`);
    if (!confirmRestore) {
        document.getElementById('design-version-history').value = '';
        return;
    }
    
    try {
        toast(`Restoring version ${versionNumber}...`, 'info');
        const name = document.getElementById('design-name').value.trim();
        const activeTemplateChecksum = window.BarcodeStudioState.activeTemplateChecksum;
        
        const res = await api('smriti_retail_os.barcode_api.restore_print_template_version', {
            template_name: name,
            version_number: versionNumber,
            expected_checksum: activeTemplateChecksum
        });
        
        window.BarcodeStudioState.printTemplatesList = res;
        populateTemplatesDropdown();
        
        const found = window.BarcodeStudioState.printTemplatesList.find(t => t.name === window.BarcodeStudioState.activeTemplateName);
        if (found) {
            document.getElementById('design-raw').value = found.raw_template || '';
            window.BarcodeStudioState.activeTemplateChecksum = found.template_checksum;
            window.BarcodeStudioState.canvasElements = parseLayoutJson(found.custom_visual_layout_json);
            
            try {
                window.BarcodeStudioState.designerMappings = found.custom_field_mappings_json ? JSON.parse(found.custom_field_mappings_json) : [];
            } catch(e) {
                window.BarcodeStudioState.designerMappings = [];
            }
            
            renderMappingTable();
            renderCanvas();
            updatePropertiesInspector();
            validateSandbox(found.raw_template || '');
            await loadVersionHistory(found.name);
        }
        
        toast(`Version ${versionNumber} restored successfully`, 'success');
        document.getElementById('design-version-history').value = '';
        
    } catch(e) {
        toast(e.message || e, 'error');
        document.getElementById('design-version-history').value = '';
    }
}
