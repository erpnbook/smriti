/**
 * @file: smriti_retail_os/public/js/barcode/barcode_init.js
 * @description: Application orchestrator, event wiring, and bootstrapping sequence.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

// ── Application Loader ──
async function init() {
    // Sync context variables with state namespace
    window.BarcodeStudioState.csrfToken = CSRF_TOKEN;
    window.BarcodeStudioState.cashier = loggedUser;

    const _sbu = document.getElementById('sb-user'); 
    if (_sbu && loggedUser) _sbu.textContent = loggedUser.split('@')[0];
    const _sba = document.getElementById('sb-avatar'); 
    if (_sba && loggedUser) _sba.textContent = loggedUser.charAt(0).toUpperCase();

    try {
        // Load Filters Data
        const filters = await api('smriti_retail_os.barcode_api.get_barcode_filters');
        
        // Brand selector
        const brandSel = document.getElementById('flt-brand');
        if (brandSel) {
            filters.brands.forEach(b => {
                const opt = document.createElement('option');
                opt.value = b;
                opt.textContent = b;
                brandSel.appendChild(opt);
            });
        }

        // Category selector
        const catSel = document.getElementById('flt-category');
        if (catSel) {
            filters.categories.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                catSel.appendChild(opt);
            });
        }

        // Size selector
        const sizeSel = document.getElementById('flt-size');
        if (sizeSel) {
            filters.sizes.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                sizeSel.appendChild(opt);
            });
        }
        window.BarcodeStudioState.sizeOptions = filters.sizes || [];

        // Department selector
        const deptSel = document.getElementById('flt-department');
        if (deptSel && filters.departments) {
            filters.departments.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                deptSel.appendChild(opt);
            });
        }

        // Gender selector
        const genderSel = document.getElementById('flt-gender');
        if (genderSel && filters.genders) {
            filters.genders.forEach(g => {
                const opt = document.createElement('option');
                opt.value = g;
                opt.textContent = g;
                genderSel.appendChild(opt);
            });
        }

        // Season selector
        const seasonSel = document.getElementById('flt-season');
        if (seasonSel && filters.seasons) {
            filters.seasons.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                seasonSel.appendChild(opt);
            });
        }

        // Collection selector
        const collSel = document.getElementById('flt-collection');
        if (collSel && filters.collections) {
            filters.collections.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                collSel.appendChild(opt);
            });
        }

        // Supplier selector
        const suppSel = document.getElementById('flt-supplier');
        if (suppSel && filters.suppliers) {
            filters.suppliers.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                suppSel.appendChild(opt);
            });
        }

        // Helper to populate generic select
        const populateSel = (id, list) => {
            const sel = document.getElementById(id);
            if (sel && list && Array.isArray(list)) {
                list.forEach(val => {
                    const opt = document.createElement('option');
                    opt.value = val;
                    opt.textContent = val;
                    sel.appendChild(opt);
                });
            }
        };

        populateSel('flt-purchase-class', filters.purchase_classes);
        populateSel('flt-merchandise-cat', filters.merchandise_categories);
        populateSel('flt-sub-cat', filters.sub_categories);
        populateSel('flt-upper-material', filters.upper_materials);
        populateSel('flt-outsole', filters.outsoles);
        populateSel('flt-heel-type', filters.heel_types);

        // Render Templates dropdown
        window.BarcodeStudioState.printTemplatesList = filters.print_templates || [];
        populateTemplatesDropdown();

        // Load print profiles
        await fetchPrintProfiles();

        // Load token reference (cache is populated here)
        loadTokenReference();
        
        // Initialize QZ Tray WebSocket
        initQZ();
        
        // Render initial structures
        renderQueue();
        renderRecentJobs();
        
        // Bind text-area validation in designer
        const designRaw = document.getElementById('design-raw');
        if (designRaw) {
            designRaw.addEventListener('input', function() {
                validateSandbox(this.value);
            });
        }

        // Fetch Company settings and pre-fill printer configuration
        try {
            const settings = await api('smriti_retail_os.company_api.get_company_settings');
            if (settings) {
                const ipInput = document.getElementById('cfg-ip');
                const portInput = document.getElementById('cfg-port');
                if (settings.default_printer_ip && ipInput) {
                    ipInput.value = settings.default_printer_ip;
                }
                if (settings.default_printer_port && portInput) {
                    portInput.value = settings.default_printer_port;
                }
                if (settings.default_printer_lang) {
                    window.BarcodeStudioState.activePrinterLanguage = settings.default_printer_lang;
                    const capabilitySelect = document.getElementById('cfg-capability');
                    if (window.BarcodeStudioState.activePrinterLanguage === "TSPL") {
                        if (capabilitySelect) capabilitySelect.value = "TSC TE244";
                        window.BarcodeStudioState.activeDPI = 203;
                    } else {
                        if (capabilitySelect) capabilitySelect.value = "Zebra GK420D";
                        window.BarcodeStudioState.activeDPI = 203;
                    }
                    checkPrinterTemplateMismatch();
                }
                if (settings.default_label_size) {
                    const custPreset = document.getElementById('cust-size-preset');
                    if (custPreset) custPreset.value = settings.default_label_size;
                    const fltSize = document.getElementById('flt-size');
                    if (fltSize) fltSize.value = settings.default_label_size;
                }
            }
        } catch (err) {
            console.error("Failed to load company settings for pre-fill", err);
        }

        // Initialize dashboard and auto-refresh loop
        refreshPrintJobsDashboard();
        initRealtime();
        setInterval(refreshPrintJobsDashboard, 5000);

    } catch(e) {
        console.error(e);
        toast('Failed to load barcode configuration data', 'error');
    }
}

function populateTemplatesDropdown() {
    const tempSel = document.getElementById('cfg-template');
    if (!tempSel) return;
    tempSel.innerHTML = '<option value="">Built-in Default</option>';
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    printTemplatesList.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.name;
        opt.textContent = `${t.template_name} (${t.label_size} - ${t.printer_language})`;
        tempSel.appendChild(opt);
    });
}

function selectPrintTemplate(val) {
    if (!val) {
        const sandboxStatus = document.getElementById('sandbox-status');
        if (sandboxStatus) {
            sandboxStatus.innerHTML = `<div style="color:var(--text-muted); display:flex; align-items:center; gap:4px;"><span class="material-symbols-outlined" style="font-size:16px;">help</span> Using built-in fallback template</div>`;
        }
        const activeItem = window.BarcodeStudioState.printQueue.find(q => q.selected) || window.BarcodeStudioState.printQueue[0];
        if (activeItem) {
            BarcodeEvents.emit(BarcodeEvents.PREVIEW_REFRESH, activeItem);
        }
        checkPrinterTemplateMismatch();
        return;
    }
    const found = window.BarcodeStudioState.printTemplatesList.find(t => t.name === val);
    if (found) {
        validateSandbox(found.raw_template || '');
        const activeItem = window.BarcodeStudioState.printQueue.find(q => q.selected) || window.BarcodeStudioState.printQueue[0];
        if (activeItem) {
            BarcodeEvents.emit(BarcodeEvents.PREVIEW_REFRESH, activeItem);
        }
        checkPrinterTemplateMismatch();
    }
}

// ── Printer Diagnostics ──
async function testConnection() {
    const ip = document.getElementById('cfg-ip').value.trim();
    const port = parseInt(document.getElementById('cfg-port').value) || 9100;

    if (!ip) {
        toast('Please enter the Printer IP address first.', 'error');
        return;
    }

    try {
        toast('Testing printer socket connection...', 'info');
        const res = await api('smriti_retail_os.barcode_api.test_printer_connection', {
            printer_ip: ip,
            printer_port: port
        });

        if (res && res.success) {
            const latencyStr = res.latency_ms !== null && res.latency_ms !== undefined ? ` (${res.latency_ms} ms)` : '';
            toast(`Connection successful!${latencyStr}`, 'success');
            logSessionPrint(ip, `PING SUCCESS${latencyStr}`, true);
        } else {
            toast(res.message, 'error');
            logSessionPrint(ip, 'PING FAIL: ' + res.message, false);
        }
    } catch(e) {
        toast(e.message, 'error');
        logSessionPrint(ip, 'PING ERROR: ' + e.message, false);
    }
}

async function sendTestLabel() {
    const ip = document.getElementById('cfg-ip').value.trim();
    const port = parseInt(document.getElementById('cfg-port').value) || 9100;

    if (!ip) {
        toast('Please enter the Printer IP address first.', 'error');
        return;
    }

    try {
        toast('Streaming raw diagnostic label...', 'info');
        const res = await api('smriti_retail_os.barcode_api.print_test_label', {
            printer_ip: ip,
            printer_port: port,
            printer_language: window.BarcodeStudioState.activePrinterLanguage
        });

        if (res && res.success) {
            toast(res.message, 'success');
            logSessionPrint(ip, 'TEST LABEL SENT', true);
        } else {
            toast(res.message, 'error');
            logSessionPrint(ip, 'TEST LABEL FAIL: ' + res.message, false);
        }
    } catch(e) {
        toast(e.message, 'error');
        logSessionPrint(ip, 'TEST LABEL ERROR: ' + e.message, false);
    }
}

function logSessionPrint(ip, action, success) {
    const list = document.getElementById('session-log-list');
    if (!list) return;
    const logs = list.querySelectorAll('.log-item');
    if (logs.length === 0 || list.innerHTML.includes('No print jobs')) {
        list.innerHTML = '';
    }
    
    if (logs.length >= 10) {
        logs[0].remove();
    }
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const div = document.createElement('div');
    div.className = `log-item ${success ? 'success' : 'error'}`;
    const leftSpan = document.createElement('span');
    leftSpan.textContent = `${time} - ${action}`;
    const rightSpan = document.createElement('span');
    rightSpan.style.fontSize = '10px';
    rightSpan.textContent = ip;
    div.appendChild(leftSpan);
    div.appendChild(document.createTextNode(' '));
    div.appendChild(rightSpan);
    list.appendChild(div);
    list.scrollTop = list.scrollHeight;
}

// ── Transaction Search Modal helper ──
async function openTxSearchModal() {
    openModal('tx-search-modal');
    const doctype = document.getElementById('tx-doctype').value;
    const tbody = document.getElementById('tx-search-tbody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-sub);">Loading records...</td></tr>';
    
    try {
        const txs = await api('smriti_retail_os.barcode_api.get_recent_transactions', {
            doctype: doctype,
            limit: 15
        });

        if (tbody) {
            if (!txs || !txs.length) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">No recent transactions found</td></tr>';
                return;
            }

            tbody.innerHTML = txs.map(t => `
                <tr>
                    <td style="font-family:monospace; font-weight:600; color:var(--primary-lt);">${esc(t.name)}</td>
                    <td>${esc(t.posting_date)}</td>
                    <td>${esc(t.extra_info || '-')}</td>
                    <td style="text-align:center; font-weight:600; color:var(--accent);">${esc(String(t.items_count))} lines</td>
                    <td style="text-align:right;">
                        <button class="topbtn" onclick="selectTxAndLoad('${esc(t.name)}')" style="padding:4px 8px; font-size:11px;">Load</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch(e) {
        if (tbody) {
            const errTr = document.createElement('tr');
            const errTd = document.createElement('td');
            errTd.colSpan = 5;
            errTd.style.cssText = 'text-align:center;color:var(--danger);';
            errTd.textContent = `Error: ${e.message}`;
            errTr.appendChild(errTd);
            tbody.innerHTML = '';
            tbody.appendChild(errTr);
        }
    }
}

function selectTxAndLoad(name) {
    const txNameInput = document.getElementById('tx-name');
    if (txNameInput) txNameInput.value = name;
    closeModal('tx-search-modal');
    loadTransactionItems();
}

function openAddCustomRowModal() {
    const custBarcode = document.getElementById('cust-barcode');
    if (custBarcode) {
        custBarcode.value = "99" + Math.floor(Math.random() * 100000000000);
    }
    openModal('custom-row-modal');
}

function submitCustomRow() {
    const name = document.getElementById('cust-name').value.trim();
    const style = document.getElementById('cust-style').value.trim() || "CUST-GEN";
    const barcode = document.getElementById('cust-barcode').value.trim();
    const brand = document.getElementById('cust-brand').value.trim() || "SMRITI";
    const mrp = parseFloat(document.getElementById('cust-mrp').value) || 0;
    const size = document.getElementById('cust-size').value.trim();
    const color = document.getElementById('cust-color').value.trim();
    const qty = parseInt(document.getElementById('cust-qty').value) || 1;
    const sizePreset = document.getElementById('cust-size-preset').value;

    if (!name) {
        toast('Item Name is required', 'error');
        return;
    }

    const it = {
        item_code: style + "-" + size,
        item_name: name,
        brand: brand,
        barcode: barcode,
        mrp: mrp,
        size: size,
        color: color,
        style: style,
        print_qty: qty,
        label_size: sizePreset
    };

    addItemsToQueue([it]);
    closeModal('custom-row-modal');
    toast('Custom generic row added to queue', 'success');
}

async function fetchPrintProfiles() {
    try {
        const profiles = await api('smriti_retail_os.barcode_api.get_print_profiles') || {};
        window.BarcodeStudioState.printProfilesObj = profiles;
        const profileSel = document.getElementById('cfg-profile');
        if (!profileSel) return;
        profileSel.innerHTML = '<option value="">-- Manual Selection --</option>';
        
        let hasDefault = false;
        let defaultKey = "";
        
        Object.keys(profiles).forEach(k => {
            const p = profiles[k];
            const opt = document.createElement('option');
            opt.value = p.profile_name;
            opt.textContent = p.is_default ? `⭐️ ${p.profile_name}` : p.profile_name;
            profileSel.appendChild(opt);
            
            if (p.is_default) {
                hasDefault = true;
                defaultKey = p.profile_name;
            }
        });
        
        if (hasDefault && defaultKey) {
            profileSel.value = defaultKey;
            applyPrintProfile(defaultKey);
        }
    } catch(e) {
        console.error('Failed to load print profiles:', e);
    }
}

function applyPrintProfile(profileName) {
    const profiles = window.BarcodeStudioState.printProfilesObj;
    if (!profileName || !profiles[profileName]) return;
    const p = profiles[profileName];
    
    const ipInput = document.getElementById('cfg-ip');
    const portInput = document.getElementById('cfg-port');
    const templateSelect = document.getElementById('cfg-template');
    const capabilitySelect = document.getElementById('cfg-capability');
    
    if (ipInput) ipInput.value = p.printer_ip || '';
    if (portInput) portInput.value = p.printer_port || 9100;
    if (templateSelect) templateSelect.value = p.template_name || '';
    if (capabilitySelect) {
        capabilitySelect.value = p.dpi === "300 DPI" ? "Citizen CL-E321" : "Zebra GK420D";
    }
    
    window.BarcodeStudioState.activeDPI = p.dpi === "300 DPI" ? 300 : 203;
    
    selectPrintTemplate(p.template_name);
    toast(`Applied print profile preset: ${p.profile_name}`, 'success');
}

function openProfileSaveModal() {
    const template = document.getElementById('cfg-template').value;
    const ip = document.getElementById('cfg-ip').value.trim();
    const port = document.getElementById('cfg-port').value.trim();
    const cap = document.getElementById('cfg-capability').value;

    if (!ip) {
        toast('Printer IP address is required to create a print profile.', 'error');
        return;
    }

    const ct = document.getElementById('lbl-cap-temp');
    const ci = document.getElementById('lbl-cap-ip');
    const cp = document.getElementById('lbl-cap-port');
    const cc = document.getElementById('lbl-cap-cap');
    
    if (ct) ct.textContent = template || 'Built-in Default';
    if (ci) ci.textContent = ip;
    if (cp) cp.textContent = port || '9100';
    if (cc) cc.textContent = cap;
    
    openModal('profile-save-modal');
}

async function submitSavePrintProfile() {
    const name = document.getElementById('profile-name-input').value.trim();
    const isDefault = document.getElementById('profile-default-chk').checked ? 1 : 0;
    
    const template = document.getElementById('cfg-template').value;
    const ip = document.getElementById('cfg-ip').value.trim();
    const port = parseInt(document.getElementById('cfg-port').value) || 9100;
    const cap = document.getElementById('cfg-capability').value;
    const dpi = cap.includes('300 DPI') ? '300 DPI' : '203 DPI';

    if (!name) {
        toast('Profile Name is required', 'error');
        return;
    }

    try {
        toast('Saving print profile to Company Settings...', 'info');
        await api('smriti_retail_os.barcode_api.save_print_profile', {
            profile_name: name,
            template_name: template || null,
            printer_ip: ip,
            printer_port: port,
            dpi: dpi,
            copies: 1,
            label_size: '50x25',
            is_default: isDefault
        });
        
        closeModal('profile-save-modal');
        toast(`Print profile ${name} saved successfully`, 'success');
        await fetchPrintProfiles();
    } catch(e) {
        toast(e.message, 'error');
    }
}

function applyPrinterCapability(capabilityName) {
    const customGroup = document.getElementById('custom-capability-group');
    if (capabilityName === "Custom Profile") {
        if (customGroup) customGroup.style.display = 'flex';
        applyCustomCapabilities();
        return;
    }
    
    if (customGroup) customGroup.style.display = 'none';
    
    const capabilities = window.BarcodeStudioState.printerCapabilities;
    if (capabilities[capabilityName]) {
        window.BarcodeStudioState.activePrinterLanguage = capabilities[capabilityName].language;
        window.BarcodeStudioState.activeDPI = capabilities[capabilityName].dpi;
    }
    
    const activeItem = window.BarcodeStudioState.printQueue.find(q => q.selected) || window.BarcodeStudioState.printQueue[0];
    if (activeItem) {
        BarcodeEvents.emit(BarcodeEvents.PREVIEW_REFRESH, activeItem);
    }
    
    checkPrinterTemplateMismatch();
}

function applyCustomCapabilities() {
    const customLang = document.getElementById('cfg-custom-lang');
    const customDpi = document.getElementById('cfg-custom-dpi');
    
    if (customLang) window.BarcodeStudioState.activePrinterLanguage = customLang.value;
    if (customDpi) window.BarcodeStudioState.activeDPI = parseInt(customDpi.value) || 203;
    
    const activeItem = window.BarcodeStudioState.printQueue.find(q => q.selected) || window.BarcodeStudioState.printQueue[0];
    if (activeItem) {
        BarcodeEvents.emit(BarcodeEvents.PREVIEW_REFRESH, activeItem);
    }
    
    checkPrinterTemplateMismatch();
}

function checkPrinterTemplateMismatch() {
    const templateSelect = document.getElementById('cfg-template');
    const selectedTemplateVal = templateSelect ? templateSelect.value : "";
    let templateLanguage = "ZPL";
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    
    if (selectedTemplateVal) {
        const found = printTemplatesList.find(t => t.name === selectedTemplateVal);
        if (found) {
            templateLanguage = found.printer_language;
        }
    } else {
        const activeItem = window.BarcodeStudioState.printQueue.find(q => q.selected) || window.BarcodeStudioState.printQueue[0];
        if (activeItem && activeItem.label_size === "106x55") {
            templateLanguage = "TSPL";
        } else {
            templateLanguage = "ZPL";
        }
    }
    
    const capabilityPreset = document.getElementById('cfg-capability').value;
    let printerLanguage = window.BarcodeStudioState.activePrinterLanguage;
    if (capabilityPreset === "Custom Profile") {
        const customLang = document.getElementById('cfg-custom-lang');
        if (customLang) printerLanguage = customLang.value;
    }
    
    const warningBanner = document.getElementById('language-mismatch-warning');
    const tmplLangEl = document.getElementById('mismatch-template-lang');
    const prnLangEl = document.getElementById('mismatch-printer-lang');
    
    if (!warningBanner || !tmplLangEl || !prnLangEl) return;
    
    if (templateLanguage !== printerLanguage) {
        tmplLangEl.textContent = templateLanguage;
        prnLangEl.textContent = printerLanguage;
        warningBanner.style.display = 'block';
    } else {
        warningBanner.style.display = 'none';
    }
}

// ── Sandbox validation ──
function validateSandbox(templateText) {
    const sandboxStatus = document.getElementById('sandbox-status');
    const matches = templateText.match(/\{[^}]+\}/g) || [];
    const variables = matches.map(m => m.slice(1, -1).trim());
    
    let standardVars = [
        "barcode", "item_code", "item_name", "brand", "mrp", "size", "color", "style", "pkd_date",
        "gender", "heel_type", "outsole", "upper_material", "merchandise_category", "sub_category", "purchase_class"
    ];

    const cache = window.BarcodeStudioState.tokenReferenceCache;
    if (cache && Array.isArray(cache)) {
        standardVars = cache.map(ref => ref.placeholder.replace('{', '').replace('}', ''));
    }
    
    const activeTemplateId = document.getElementById('cfg-template').value;
    const found = window.BarcodeStudioState.printTemplatesList.find(t => t.name === activeTemplateId);
    let activeMappings = [];
    if (found && found.custom_field_mappings_json) {
        try {
            activeMappings = JSON.parse(found.custom_field_mappings_json);
        } catch(e) {}
    }
    
    const allCustomVars = [
        ...window.BarcodeStudioState.designerMappings.map(m => m.label_field),
        ...activeMappings.map(m => m.label_field)
    ].map(v => v ? v.trim() : "").filter(Boolean);
    
    const errors = [];
    const duplicates = [];
    const seen = {};
    
    variables.forEach(v => {
        if (seen[v]) {
            if (!duplicates.includes(v)) duplicates.push(v);
        }
        seen[v] = true;
        
        if (!standardVars.includes(v) && !allCustomVars.includes(v)) {
            errors.push(v);
        }
    });

    const designerIndicator = document.getElementById('designer-sandbox-status');
    
    let html = '';
    if (errors.length > 0) {
        html = `<div style="color:var(--danger); display:flex; align-items:center; gap:4px; font-weight:600;"><span class="material-symbols-outlined" style="font-size:16px;">error</span> Unknown/Unmapped: ${errors.join(', ')}</div>`;
    } else if (duplicates.length > 0) {
        html = `<div style="color:var(--warning); display:flex; align-items:center; gap:4px;"><span class="material-symbols-outlined" style="font-size:16px;">warning</span> Duplicates: ${duplicates.join(', ')}</div>`;
    } else {
        html = `<div style="color:var(--success); display:flex; align-items:center; gap:4px; font-weight:600;"><span class="material-symbols-outlined" style="font-size:16px;">check_circle</span> Pre-Print Sanitizer: Validated</div>`;
    }
    
    if (sandboxStatus) sandboxStatus.innerHTML = html;
    if (designerIndicator) designerIndicator.innerHTML = html;
    
    return errors.length === 0;
}

// ── reprint recent jobs ──
function recordPrintJob(jobRef, totalQty) {
    let jobs = [];
    try {
        jobs = JSON.parse(localStorage.getItem('smriti_recent_jobs')) || [];
    } catch(e) {}
    
    const newJob = {
        id: 'job_' + Date.now(),
        ref: jobRef || 'Manual Print',
        date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + new Date().toLocaleDateString([], { month: 'short', day: 'numeric' }),
        total_qty: totalQty,
        items: JSON.parse(JSON.stringify(window.BarcodeStudioState.printQueue))
    };
    
    jobs.unshift(newJob);
    jobs = jobs.slice(0, 5);
    localStorage.setItem('smriti_recent_jobs', JSON.stringify(jobs));
    renderRecentJobs();
}

function renderRecentJobs() {
    const listEl = document.getElementById('recent-jobs-list');
    if (!listEl) return;
    
    let jobs = [];
    try {
        jobs = JSON.parse(localStorage.getItem('smriti_recent_jobs')) || [];
    } catch(e) {}
    
    if (!jobs.length) {
        listEl.innerHTML = `<div style="color:var(--text-sub); text-align:center; padding: 10px; font-size: 0.8rem;">No recent jobs</div>`;
        return;
    }
    
    listEl.innerHTML = jobs.map(j => `
        <div style="display:flex; justify-content:space-between; align-items:center; background:var(--barcode-overlay-md); border:1px solid var(--border); border-radius:var(--radius-sm); padding:8px 10px; font-size:0.8rem;">
            <div>
                <div style="font-weight:600; color:var(--text);">${esc(j.ref)}</div>
                <div style="font-size:0.7rem; color:var(--text-muted); margin-top:2px;">${esc(j.date)} &bull; ${j.total_qty} Labels</div>
            </div>
            <button class="topbtn" onclick="reprintJob('${j.id}')" style="padding:4px 8px; font-size:10px;">Reprint</button>
        </div>
    `).join('');
}

function reprintJob(jobId) {
    let jobs = [];
    try {
        jobs = JSON.parse(localStorage.getItem('smriti_recent_jobs')) || [];
    } catch(e) {}
    
    const job = jobs.find(j => j.id === jobId);
    if (job && job.items) {
        window.BarcodeStudioState.printQueue = JSON.parse(JSON.stringify(job.items));
        renderQueue();
        toast(`Reloaded job: ${job.ref} (${job.total_qty} Labels)`, 'success');
    }
}

// Window load hook
window.onload = init;
