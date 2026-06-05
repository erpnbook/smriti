const CSRF_TOKEN = window.CSRF_TOKEN || '{{ csrf_token }}';
let loggedUser = window.loggedUser || '{{ cashier }}';

// ═══════════════════════════════════════════════════════════════════════════
//  SHARED UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

function api(method, params = {}) {
    return fetch(`/api/method/${method}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': CSRF_TOKEN
        },
        body: JSON.stringify(params)
    })
    .then(r => r.json())
    .then(d => {
        if (d.exc) throw new Error(d._error_message || d.exc);
        return d.message;
    });
}

function doLogout() {
    fetch('/api/method/logout', { credentials: 'include' })
    .then(() => { window.location.href = '/login'; });
}

function toast(msg, type = 'success') {
    const cont = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    const icon = type === 'success' ? 'check_circle' : type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'info';
    t.innerHTML = `<span class="material-symbols-outlined">${icon}</span> <span>${msg}</span>`;
    cont.appendChild(t);
    setTimeout(() => { t.remove(); }, 4500);
}

function openPopout(e, url) {
    e.preventDefault();
    e.stopPropagation();
    let popout_url = url;
    if (popout_url.indexOf('?') === -1) {
        popout_url += '?popout=true';
    }
    window.open(popout_url, "smriti-popout-window", "width=1200,height=800,resizable=yes,scrollbars=yes");
}

// ═══════════════════════════════════════════════════════════════════════════
//  TAB SYSTEM
// ═══════════════════════════════════════════════════════════════════════════

function switchTab(tabName) {
    document.querySelectorAll('.sim-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sim-panel').forEach(p => p.classList.remove('active'));
    const tab = document.querySelector(`.sim-tab[data-tab="${tabName}"]`);
    const panel = document.getElementById(`panel-${tabName}`);
    if (tab) tab.classList.add('active');
    if (panel) panel.classList.add('active');
}

// ═══════════════════════════════════════════════════════════════════════════
//  TAB 1: MANUAL STYLE CREATOR (existing code)
// ═══════════════════════════════════════════════════════════════════════════

// Track current dynamic sizes matrix
let sizesList = ['6', '7', '8', '9', '10', '11', '12'];
let sizesConfigData = {}; // Maps size label -> { active: boolean, barcode_mode: 'auto'|'manual', manual_barcode: string, existing: boolean, variant_code: string }
let dynamicSizeGroups = [];

async function loadDynamicSizeGroups() {
    try {
        const groups = await api('smriti_retail_os.master_api.get_size_groups');
        dynamicSizeGroups = groups || [];
        const selector = document.getElementById('size-group-selector');
        if (selector) {
            selector.innerHTML = '<option value="">Custom / Manual</option>' + 
                dynamicSizeGroups.map(g => `<option value="${g.id}">${g.label}</option>`).join('');
            
            // Set first group as default if available
            if (dynamicSizeGroups.length > 0) {
                selector.value = dynamicSizeGroups[0].id;
                changeSizeGroup(dynamicSizeGroups[0].id);
            }
        }
    } catch(e) {
        console.error("Failed to load dynamic size groups:", e);
    }
}

function changeSizeGroup(groupId) {
    if (!groupId) return;
    const group = dynamicSizeGroups.find(g => g.id === groupId);
    if (!group) return;
    
    // Check if there are active configurations that will be lost
    const activeCount = Object.values(sizesConfigData).filter(c => c.active).length;
    if (activeCount > 0 && !confirm(`Changing size group will clear active variants and manual barcodes. Proceed?`)) {
        // revert select value (not critical for preset override)
        return; 
    }
    
    sizesList = [...group.sizes];
    sizesConfigData = {};
    sizesList.forEach(sz => {
        sizesConfigData[sz] = { active: false, barcode_mode: 'auto', manual_barcode: '', existing: false, variant_code: '' };
    });
    renderPivotGrid();
}

function init() {
    const _sbu = document.getElementById('sb-user'); if (_sbu) _sbu.textContent = loggedUser.split('@')[0];
    const _sba = document.getElementById('sb-avatar'); if (_sba) _sba.textContent = loggedUser.charAt(0).toUpperCase();

    // Setup initial empty configuration mapping
    sizesList.forEach(sz => {
        sizesConfigData[sz] = { active: false, barcode_mode: 'auto', manual_barcode: '', existing: false, variant_code: '' };
    });

    renderPivotGrid();
    loadDynamicSizeGroups();

    // Check for query param redirect (from Item List edit)
    const urlParams = new URLSearchParams(window.location.search);
    const editArticle = urlParams.get('article_no') || urlParams.get('style');
    if (editArticle) {
        document.getElementById('style-code').value = editArticle;
        switchTab('manual');
        lookupStyle(editArticle);
    }
}

function renderPivotGrid() {
    const container = document.getElementById('size-pivot-container');
    container.innerHTML = '';

    sizesList.forEach(sz => {
        const conf = sizesConfigData[sz] || { active: false, barcode_mode: 'auto', manual_barcode: '', existing: false, variant_code: '' };
        const activeCls = conf.active ? 'active' : '';
        const checkedAttr = conf.active ? 'checked' : '';
        const autoActive = conf.barcode_mode === 'auto' ? 'active' : '';
        const manualActive = conf.barcode_mode === 'manual' ? 'active' : '';
        const isInputDisabled = conf.barcode_mode === 'auto' ? 'disabled' : '';

        const card = document.createElement('div');
        card.className = `size-card ${activeCls}`;
        card.id = `size-card-${sz}`;

        let barcodeDisplayHtml = '';
        if (conf.barcode_mode === 'auto') {
            barcodeDisplayHtml = `<div class="size-badge">🤖 AUTO-BARCODE</div>`;
        } else {
            barcodeDisplayHtml = `
                <input type="text" class="form-input" style="font-family:monospace; font-size:0.75rem; padding:6px; width:100%; text-align:center; background:var(--bg);"
                       value="${conf.manual_barcode || ''}" placeholder="Scan/Enter Barcode" ${isInputDisabled}
                       oninput="updateManualBarcode('${sz}', this.value)">`;
        }

        // Direct delete action for existing saved variants
        let footerHtml = '';
        if (conf.existing) {
            footerHtml = `
                <div class="size-card-footer">
                    <span style="font-size:0.68rem; color:var(--success); font-weight:700;">🟢 Active in DB</span>
                    <button class="size-btn-delete" onclick="triggerDeleteVariant('${conf.variant_code}', '${sz}')" title="Delete Variant from Database">
                        <span class="material-symbols-outlined">delete</span>
                    </button>
                </div>`;
        }

        card.innerHTML = `
            <div class="size-header">
                <span class="size-label">SIZE ${sz}</span>
                <input type="checkbox" class="size-active-chk" ${checkedAttr} onchange="toggleSizeActive('${sz}', this.checked)">
            </div>
            <div class="size-body">
                <div class="barcode-toggle-wrap">
                    <span>BARCODE</span>
                    <div class="toggle-btn-grp">
                        <button class="toggle-btn ${autoActive}" onclick="setSizeBarcodeMode('${sz}', 'auto')">Auto</button>
                        <button class="toggle-btn ${manualActive}" onclick="setSizeBarcodeMode('${sz}', 'manual')">Manual</button>
                    </div>
                </div>
                <div style="margin-top:6px;">${barcodeDisplayHtml}</div>
            </div>
            ${footerHtml}
        `;
        container.appendChild(card);
    });

    // Add interactive dynamic Custom Size card at the end
    const addCard = document.createElement('div');
    addCard.className = 'add-size-card';
    addCard.onclick = promptCustomSize;
    addCard.innerHTML = `
        <span class="material-symbols-outlined icon">add_circle</span>
        <span>Add Size Row</span>
    `;
    container.appendChild(addCard);
}

function toggleSizeActive(sz, val) {
    if (!sizesConfigData[sz]) return;
    sizesConfigData[sz].active = val;
    const card = document.getElementById(`size-card-${sz}`);
    if (card) {
        if (val) card.classList.add('active');
        else card.classList.remove('active');
    }
}

function setSizeBarcodeMode(sz, mode) {
    if (!sizesConfigData[sz]) return;
    sizesConfigData[sz].barcode_mode = mode;
    renderPivotGrid();
}

function updateManualBarcode(sz, value) {
    if (!sizesConfigData[sz]) return;
    sizesConfigData[sz].manual_barcode = value;
}

function promptCustomSize() {
    const val = prompt("Enter Custom Size (e.g. 5, 13, XXL):");
    if (!val) return;
    const cleanSize = val.trim().toUpperCase();
    if (sizesList.includes(cleanSize)) {
        toast(`Size ${cleanSize} is already in the matrix!`, 'warning');
        return;
    }
    sizesList.push(cleanSize);
    sizesConfigData[cleanSize] = { active: true, barcode_mode: 'auto', manual_barcode: '', existing: false, variant_code: '' };
    renderPivotGrid();
}

async function lookupStyle(articleNo) {
    if (!articleNo.trim()) return;
    try {
        toast('Fetching style info...', 'info');
        const res = await api('smriti_retail_os.item_master_api.get_style_details', {
            article_no: articleNo.trim()
        });

        const inputs = ['style-code', 'style-desc', 'style-color', 'style-brand', 'style-cost', 'style-mrp', 'style-vendor', 'style-hsn'];
        inputs.forEach(id => document.getElementById(id).classList.remove('retrieval-glowing'));

        if (res.exists) {
            toast('Existing Style details loaded successfully!', 'success');
            
            // Prefill base details
            document.getElementById('style-desc').value = res.description || '';
            document.getElementById('style-brand').value = res.brand || '';
            document.getElementById('style-group').value = res.item_group || 'Footwear';
            document.getElementById('style-cost').value = res.cost_price || 0;
            document.getElementById('style-mrp').value = res.mrp || 0;
            document.getElementById('style-gst').value = res.gst_percentage || '18';
            document.getElementById('style-hsn').value = res.hsn_code || '';
            document.getElementById('style-gender').value = res.gender || 'UNISEX';
            document.getElementById('style-pclass').value = res.purchase_class || 'FW';
            document.getElementById('style-vendor').value = res.vendor_code || '';
            document.getElementById('style-color').value = res.color || 'UNKNOWN';

            // Glow glowing green to indicate retrieval success
            inputs.forEach(id => document.getElementById(id).classList.add('retrieval-glowing'));

            // Pre-fill active sizes configuration mapping from DB
            const currentGrpId = document.getElementById('size-group-selector')?.value;
            const currentGrp = dynamicSizeGroups.find(g => g.id === currentGrpId);
            sizesList = currentGrp ? [...currentGrp.sizes] : ['6', '7', '8', '9', '10', '11', '12'];
            sizesConfigData = {};
            sizesList.forEach(sz => {
                sizesConfigData[sz] = { active: false, barcode_mode: 'auto', manual_barcode: '', existing: false, variant_code: '' };
            });

            if (res.sizes && res.sizes.length) {
                res.sizes.forEach(szRow => {
                    const szLabel = szRow.size;
                    if (!sizesList.includes(szLabel)) {
                        sizesList.push(szLabel);
                    }
                    sizesConfigData[szLabel] = {
                        active: true,
                        barcode_mode: 'manual',
                        manual_barcode: szRow.barcode,
                        existing: true,
                        variant_code: szRow.variant_code
                    };
                });
            }

            renderPivotGrid();
        } else {
            toast('New style code entered. Wizard configured for clean creation.', 'info');
        }
    } catch(e) {
        toast('Failed to query style: ' + e.message, 'error');
    }
}

async function triggerDeleteVariant(variantCode, size) {
    if (!confirm(`Are you absolutely sure you want to permanently delete variant "${variantCode}" (Size ${size})? This operation will remove all associated barcodes, price lists, and cannot be undone.`)) {
        return;
    }
    
    try {
        toast(`Purging variant ${variantCode} from database...`, 'info');
        const res = await api('smriti_retail_os.item_master_api.delete_size_variant', {
            variant_code: variantCode
        });
        
        toast(res.message || 'Variant deleted successfully.', 'success');
        
        // Remove from local config
        if (sizesConfigData[size]) {
            sizesConfigData[size] = { active: false, barcode_mode: 'auto', manual_barcode: '', existing: false, variant_code: '' };
        }
        
        renderPivotGrid();
    } catch(e) {
        toast('Failed to delete variant: ' + e.message, 'error');
    }
}

async function saveStyleMaster() {
    const article = document.getElementById('style-code').value.trim();
    const desc = document.getElementById('style-desc').value.trim();
    const color = document.getElementById('style-color').value.trim().toUpperCase();
    const mrp = parseFloat(document.getElementById('style-mrp').value) || 0;
    
    if (!article) { toast('Article/Style Code is required!', 'error'); return; }
    if (!desc) { toast('Style Description is required!', 'error'); return; }
    if (!color) { toast('Color is required!', 'error'); return; }
    if (mrp <= 0) { toast('Planned MRP must be greater than zero!', 'error'); return; }

    const base_details = {
        article_no: article,
        description: desc,
        color: color,
        brand: document.getElementById('style-brand').value.trim(),
        item_group: document.getElementById('style-group').value,
        cost_price: parseFloat(document.getElementById('style-cost').value) || 0,
        mrp: mrp,
        gst_percentage: document.getElementById('style-gst').value,
        hsn_code: document.getElementById('style-hsn').value.trim(),
        gender: document.getElementById('style-gender').value,
        purchase_class: document.getElementById('style-pclass').value,
        vendor_code: document.getElementById('style-vendor').value.trim(),
        product_tax_group: ''
    };

    // Construct configurations sizes payload
    const sizes_config = [];
    let hasActive = false;
    
    sizesList.forEach(sz => {
        const conf = sizesConfigData[sz];
        if (conf && conf.active) {
            hasActive = true;
            sizes_config.push({
                size: sz,
                active: true,
                barcode_mode: conf.barcode_mode,
                manual_barcode: conf.barcode_mode === 'manual' ? conf.manual_barcode : ''
            });
        }
    });

    if (!hasActive) {
        toast('Please activate at least one Size configuration in the matrix!', 'error');
        return;
    }

    try {
        toast('Saving Style & Variant Configurations...', 'info');
        const res = await api('smriti_retail_os.item_master_api.create_style_with_variants', {
            base_details: JSON.stringify(base_details),
            sizes_config: JSON.stringify(sizes_config)
        });

        toast(res.message || 'Style master saved successfully!', 'success');
        
        // Reload details
        await lookupStyle(article);
    } catch(e) {
        toast('Failed to save Style Master: ' + e.message, 'error');
    }
}

function clearWizard() {
    if (!confirm('Are you sure you want to clear the entire form?')) return;
    
    const inputs = ['style-code', 'style-desc', 'style-color', 'style-brand', 'style-vendor', 'style-hsn'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        el.value = '';
        el.classList.remove('retrieval-glowing');
    });
    
    document.getElementById('style-cost').value = 0;
    document.getElementById('style-mrp').value = 0;
    document.getElementById('style-gst').value = '18';
    document.getElementById('style-gender').value = 'UNISEX';
    document.getElementById('style-pclass').value = 'FW';
    document.getElementById('style-group').value = 'Footwear';

    const currentGrpId = document.getElementById('size-group-selector')?.value;
    const currentGrp = dynamicSizeGroups.find(g => g.id === currentGrpId);
    sizesList = currentGrp ? [...currentGrp.sizes] : ['6', '7', '8', '9', '10', '11', '12'];
    sizesConfigData = {};
    sizesList.forEach(sz => {
        sizesConfigData[sz] = { active: false, barcode_mode: 'auto', manual_barcode: '', existing: false, variant_code: '' };
    });

    renderPivotGrid();
    toast('Wizard cleared.', 'info');
}


// ═══════════════════════════════════════════════════════════════════════════
//  TAB 2: PASTE SIZE MATRIX (Excel Import)
// ═══════════════════════════════════════════════════════════════════════════

// ─── Column name aliases for intelligent auto-detection ───────────────────
const COL_ALIASES = {
    article:     ['ARTICLE', 'STYLE', 'STYLE CODE', 'ARTICLE NO', 'ARTICLE CODE', 'ART', 'ART NO', 'PRODUCT STYLE CODE'],
    color:       ['COLOR', 'COLOUR', 'CLR'],
    category:    ['CATOGARY', 'CATEGORY', 'CAT', 'DEPT', 'DEPARTMENT'],
    description: ['SUB - CATO', 'SUB-CATO', 'SUB CATO', 'DESCRIPTION', 'SUB-CATEGORY', 'SUB CATEGORY', 'DESC', 'ITEM DESCRIPTION', 'ITEM NAME'],
    mrp:         ['MRP', 'PLANNED MRP', 'SELLING PRICE', 'RATE', 'PRICE'],
    total_qty:   ['TTL QTY', 'TOTAL QTY', 'TOTAL', 'TTL', 'QTY'],
    hsn:         ['HSN', 'HSN CODE', 'HSN/SAC', 'HSN_CODE', 'GST HSN CODE'],
    gst:         ['GST', 'GST %', 'GST PERCENT', 'GST PERCENTAGE', 'PRODUCT TAX', 'TAX', 'TAX %'],
};

// Known size patterns — numeric sizes OR named sizes
const SIZE_PATTERNS = /^(\d{1,3}(\.\d)?|XXS|XS|S|M|L|XL|XXL|XXXL|2XL|3XL|4XL|5XL|FREE|F|UK\d+|EU\d+|US\d+)$/i;

let pastedData = {
    headers: [],          // raw header strings
    sizeColumns: [],      // indices that are size columns
    mappedColumns: {},    // { article: idx, color: idx, category: idx, description: idx, mrp: idx }
    rows: [],             // raw row arrays
    parsedStyles: [],     // structured styles for import
};

function focusPasteCapture() {
    const textarea = document.getElementById('sim-paste-capture');
    textarea.focus();
    document.getElementById('paste-zone').classList.add('active');
}

function handlePaste(e) {
    e.preventDefault();
    const clipText = (e.clipboardData || window.clipboardData).getData('text');
    if (!clipText || !clipText.trim()) {
        toast('Nothing pasted. Please copy cells from Excel first.', 'warning');
        return;
    }

    // Add scanning animation
    const zone = document.getElementById('paste-zone');
    zone.classList.add('scanning');
    setTimeout(() => zone.classList.remove('scanning'), 1500);

    parseTSV(clipText.trim());
}

function parseTSV(raw) {
    const lines = raw.split('\n').map(l => l.replace(/\r$/, ''));
    if (lines.length < 2) {
        toast('Need at least a header row and one data row.', 'error');
        return;
    }

    // Parse header
    const headers = lines[0].split('\t').map(h => h.trim());
    pastedData.headers = headers;

    // ─── Intelligent Column Detection ─────────────────────────────────
    pastedData.mappedColumns = {};
    pastedData.sizeColumns = [];

    headers.forEach((hdr, idx) => {
        const upper = hdr.toUpperCase().trim();

        // Check against known aliases
        let matched = false;
        for (const [key, aliases] of Object.entries(COL_ALIASES)) {
            if (aliases.includes(upper)) {
                pastedData.mappedColumns[key] = idx;
                matched = true;
                break;
            }
        }

        // If not matched to a known column, test for size pattern
        if (!matched && SIZE_PATTERNS.test(upper)) {
            pastedData.sizeColumns.push(idx);
        }
    });

    // Parse data rows
    pastedData.rows = [];
    for (let i = 1; i < lines.length; i++) {
        const cells = lines[i].split('\t').map(c => c.trim());
        if (cells.length < 2 || cells.every(c => !c)) continue; // skip blank rows
        pastedData.rows.push(cells);
    }

    if (pastedData.rows.length === 0) {
        toast('No data rows found after header. Check your selection.', 'error');
        return;
    }

    if (pastedData.sizeColumns.length === 0) {
        toast('No size columns detected! Headers should contain numeric sizes (36, 37...) or named sizes (S, M, L...)', 'warning');
    }

    // Build structured styles
    buildParsedStyles();

    // Render
    renderColumnMap();
    renderStatsBar();
    renderPreviewGrid();

    // Show controls
    document.getElementById('paste-column-map').style.display = 'block';
    document.getElementById('paste-stats-bar').style.display = 'flex';
    document.getElementById('paste-grid-wrapper').style.display = 'block';
    document.getElementById('paste-import-toolbar').style.display = 'flex';

    // Keep import DISABLED until verification passes
    const btn = document.getElementById('btn-do-import');
    btn.disabled = true;

    toast(`Parsed ${pastedData.rows.length} rows · ${pastedData.sizeColumns.length} size columns. Verifying values...`, 'info');

    // Show verify panel with spinner and run async verification
    const verifyPanel = document.getElementById('paste-verify-panel');
    verifyPanel.style.display = 'block';
    document.getElementById('verify-body').innerHTML = `
        <div class="verify-loading">
            <div class="verify-spinner"></div>
            Checking categories, colors and sub-categories against database...
        </div>`;
    document.getElementById('verify-badge').className = 'verify-badge-new';
    document.getElementById('verify-badge').textContent = 'Checking...';

    runVerification();
}

function buildParsedStyles() {
    const mc = pastedData.mappedColumns;
    const sc = pastedData.sizeColumns;
    const headers = pastedData.headers;

    pastedData.parsedStyles = [];

    pastedData.rows.forEach((cells, rowIdx) => {
        const article  = (mc.article !== undefined ? cells[mc.article] : '').trim();
        const color    = (mc.color !== undefined ? cells[mc.color] : 'UNKNOWN').trim().toUpperCase();
        const category = (mc.category !== undefined ? cells[mc.category] : '').trim();
        const desc     = (mc.description !== undefined ? cells[mc.description] : '').trim();
        const mrpStr   = (mc.mrp !== undefined ? cells[mc.mrp] : '0').trim();
        const mrp      = parseFloat(mrpStr.replace(/[^0-9.]/g, '')) || 0;

        const hsn      = (mc.hsn !== undefined ? cells[mc.hsn] : '').trim();
        
        // Safely parse GST percentage (supporting floats, 0%, and string values)
        const parsedGst = (mc.gst !== undefined ? parseFloat(cells[mc.gst]) : 18);
        const gst      = String(isNaN(parsedGst) ? 18 : parsedGst);

        if (!article) return; // skip rows without article

        // Build size configuration from size columns
        const sizesConfig = [];
        sc.forEach(colIdx => {
            const sizeLabel = headers[colIdx].trim();
            const rawQty = (cells[colIdx] || '0').trim();
            const qty = parseInt(rawQty, 10) || 0;
            if (qty > 0) {
                sizesConfig.push({
                    size: sizeLabel,
                    active: true,
                    qty: qty,
                });
            }
        });

        pastedData.parsedStyles.push({
            rowIdx: rowIdx,
            base_details: {
                article_no: article,
                description: desc || category || article,
                color: color,
                brand: '',
                item_group: category || 'Products',
                cost_price: 0,
                mrp: mrp,
                gst_percentage: gst || '18',
                hsn_code: hsn,
                gender: 'UNISEX',
                purchase_class: 'FW',
                vendor_code: '',
                product_tax_group: '',
                merchandise_category: category,
                sub_category: desc,
            },
            sizes_config: sizesConfig,
            activeSizeCount: sizesConfig.length,
            totalQty: sizesConfig.reduce((s, z) => s + z.qty, 0),
            isValid: !!article && mrp > 0 && sizesConfig.length > 0,
        });
    });
}

function renderColumnMap() {
    const list = document.getElementById('paste-col-map-list');
    list.innerHTML = '';
    const mc = pastedData.mappedColumns;
    const headers = pastedData.headers;

    // Mapped columns
    const keyLabels = {
        article: '📦 Article/Style',
        color: '🎨 Color',
        category: '📁 Category',
        description: '📝 Description',
        mrp: '💰 MRP',
        total_qty: '📊 Total Qty',
        hsn: '🏷️ HSN Code',
        gst: '📈 GST %',
    };

    for (const [key, idx] of Object.entries(mc)) {
        const tag = document.createElement('div');
        tag.className = 'sim-col-tag';
        tag.innerHTML = `<span class="col-from">${headers[idx]}</span> <span class="col-arrow">→</span> <span class="col-to">${keyLabels[key] || key}</span>`;
        list.appendChild(tag);
    }

    // Size columns
    pastedData.sizeColumns.forEach(idx => {
        const tag = document.createElement('div');
        tag.className = 'sim-col-tag';
        tag.innerHTML = `<span class="col-from">${headers[idx]}</span> <span class="col-arrow">→</span> <span class="col-to">📏 Size ${headers[idx]}</span>`;
        list.appendChild(tag);
    });
}

function renderStatsBar() {
    const bar = document.getElementById('paste-stats-bar');
    const validCount = pastedData.parsedStyles.filter(s => s.isValid).length;
    const invalidCount = pastedData.parsedStyles.filter(s => !s.isValid).length;
    const totalSizes = pastedData.parsedStyles.reduce((s, p) => s + p.activeSizeCount, 0);
    const totalQty = pastedData.parsedStyles.reduce((s, p) => s + p.totalQty, 0);

    bar.innerHTML = `
        <div class="sim-stat-chip"><span class="chip-dot blue"></span> Total Rows <span class="chip-val">${pastedData.rows.length}</span></div>
        <div class="sim-stat-chip"><span class="chip-dot green"></span> Valid Styles <span class="chip-val">${validCount}</span></div>
        ${invalidCount > 0 ? `<div class="sim-stat-chip"><span class="chip-dot red"></span> Invalid <span class="chip-val">${invalidCount}</span></div>` : ''}
        <div class="sim-stat-chip"><span class="chip-dot amber"></span> Size Variants <span class="chip-val">${totalSizes}</span></div>
        <div class="sim-stat-chip"><span class="chip-dot amber"></span> Total Qty <span class="chip-val">${totalQty}</span></div>
    `;

    // Update summary text
    document.getElementById('paste-summary-text').textContent = `${validCount} styles × ${pastedData.sizeColumns.length} size columns → ${totalSizes} variants to create`;
}

function renderPreviewGrid() {
    const headers = pastedData.headers;
    const sc = pastedData.sizeColumns;

    // Header row
    const headRow = document.getElementById('paste-grid-head');
    headRow.innerHTML = '<th>#</th><th>Status</th>';
    headers.forEach((hdr, idx) => {
        const isSizeCol = sc.includes(idx);
        headRow.innerHTML += `<th class="${isSizeCol ? 'size-col' : ''}">${hdr}</th>`;
    });
    headRow.innerHTML += '<th class="size-col">Active Sizes</th>';

    // Body rows
    const tbody = document.getElementById('paste-grid-body');
    tbody.innerHTML = '';

    pastedData.rows.forEach((cells, rowIdx) => {
        const style = pastedData.parsedStyles.find(s => s.rowIdx === rowIdx);
        const isValid = style ? style.isValid : false;
        const tr = document.createElement('tr');
        if (!isValid) tr.classList.add('row-error');

        // Row number
        let html = `<td style="color:var(--text-sub); font-weight:700; text-align:center;">${rowIdx + 1}</td>`;

        // Status badge
        if (isValid) {
            html += `<td><span class="row-status-badge valid">✓ Valid</span></td>`;
        } else {
            const reasons = [];
            if (style) {
                if (!style.base_details.article_no) reasons.push('No Article');
                if (style.base_details.mrp <= 0) reasons.push('No MRP');
                if (style.activeSizeCount === 0) reasons.push('No sizes');
            }
            html += `<td><span class="row-status-badge error">✗ ${reasons.join(', ') || 'Invalid'}</span></td>`;
        }

        // Data cells
        headers.forEach((hdr, idx) => {
            const val = cells[idx] || '';
            const isSizeCol = sc.includes(idx);
            if (isSizeCol) {
                const qty = parseInt(val, 10) || 0;
                const activeClass = qty > 0 ? 'active-size' : 'inactive-size';
                html += `<td class="size-cell ${activeClass}">${qty > 0 ? qty : '—'}</td>`;
            } else {
                html += `<td>${val}</td>`;
            }
        });

        // Active sizes summary
        if (style) {
            const badges = style.sizes_config.map(s => `<span class="sim-badge-size">${s.size}</span>`).join('');
            html += `<td>${badges || '<span style="color:var(--text-sub);">None</span>'}</td>`;
        } else {
            html += `<td>—</td>`;
        }

        tr.innerHTML = html;
        tbody.appendChild(tr);
    });
}

// ═══════════════════════════════════════════════════════════════════════════
//  PRE-IMPORT VERIFICATION — on-the-fly insert with spell correction
// ═══════════════════════════════════════════════════════════════════════════

let verificationCorrections = {}; // { 'cat:SANDAL': 'Footwear', 'clr:PISTA': 'PISTA', 'sub:MUEL': 'MUEL' }
let verificationPassed = false;

async function runVerification() {
    const validStyles = pastedData.parsedStyles.filter(s => s.isValid);
    if (validStyles.length === 0) {
        document.getElementById('paste-verify-panel').style.display = 'none';
        return;
    }
    verificationPassed = false;
    verificationCorrections = {};

    try {
        const payload = validStyles.map(s => ({ base_details: s.base_details, sizes_config: s.sizes_config }));
        const res = await api('smriti_retail_os.item_master_api.validate_pivot_values', {
            styles_json: JSON.stringify(payload)
        });
        renderVerificationPanel(res);
    } catch(e) {
        // If API fails, allow import anyway (don't block)
        document.getElementById('verify-body').innerHTML =
            `<div style="color:var(--warning); font-size:0.82rem;">⚠️ Verification check failed (${e.message}). You can still proceed with import.</div>`;
        document.getElementById('verify-badge').textContent = 'Skipped';
        _unlockImport();
    }
}

function renderVerificationPanel(res) {
    const newCats    = res.new_categories  || [];
    const newColors  = res.new_colors      || [];
    const newSubs    = res.new_sub_cats    || [];
    const existCats  = res.existing_categories || [];
    const existClrs  = res.existing_colors     || [];
    const existSubs  = res.existing_sub_cats   || [];
    const badge      = document.getElementById('verify-badge');
    const body       = document.getElementById('verify-body');

    const totalNew = newCats.length + newColors.length + newSubs.length;

    if (!res.has_issues) {
        badge.className   = 'verify-badge-ok';
        badge.textContent = 'All verified ✓';
        body.innerHTML    = `
            <div class="verify-ok-banner">
                <span class="material-symbols-outlined">check_circle</span>
                All categories, colors and sub-categories exist in the database. Ready to import!
            </div>`;
        verificationPassed = true;
        _unlockImport();
        return;
    }

    badge.className   = 'verify-badge-new';
    badge.textContent = `${totalNew} new value${totalNew > 1 ? 's' : ''} — review required`;

    // Build section HTML
    let html = '';

    if (newCats.length > 0) {
        html += _buildVerifySection(
            'folder', `Item Categories (${newCats.length} new — will be created as Item Groups)`,
            newCats, 'cat', existCats
        );
    }
    if (newColors.length > 0) {
        html += _buildVerifySection(
            'palette', `Colors (${newColors.length} new — will be added to Color attribute)`,
            newColors, 'clr', existClrs
        );
    }
    if (newSubs.length > 0) {
        html += _buildVerifySection(
            'label', `Sub-Categories (${newSubs.length} new — will be auto-created)`,
            newSubs, 'sub', existSubs
        );
    }

    // Confirm button row
    html += `
        <div class="verify-confirm-row">
            <button class="btn-verify-confirm" id="btn-verify-confirm" onclick="confirmAndApplyVerification()">
                <span class="material-symbols-outlined">check_circle</span>
                Confirm &amp; Enable Import
            </button>
            <span class="verify-hint">New values will be created automatically. Correct spellings above if needed.</span>
        </div>`;

    body.innerHTML = html;

    // Pre-populate corrections map with original values (default = create as-is)
    [...newCats, ...newColors, ...newSubs].forEach(item => {
        const prefix = newCats.includes(item) ? 'cat' : newColors.includes(item) ? 'clr' : 'sub';
        verificationCorrections[`${prefix}:${item.value}`] = item.value;
    });
}

function _buildVerifySection(icon, title, items, prefix, existingList) {
    const rows = items.map(item => {
        const key = `${prefix}:${item.value}`;
        const safeKey = key.replace(/[^a-zA-Z0-9_-]/g, '_');
        const suggestions = (item.suggestions && item.suggestions.length > 0)
            ? item.suggestions : existingList.slice(0, 8);
        const chipHtml = suggestions.length > 0
            ? `<div class="verify-suggestions">
                <span class="verify-suggest-label">Existing:</span>
                ${suggestions.slice(0, 8).map(s =>
                    `<button class="verify-suggest-chip" onclick="applyVerifySuggestion('${key}','${s.replace(/'/g,"\\'")}')"
                             title="Use '${s}' instead">${s}</button>`
                ).join('')}
               </div>`
            : '';
        return `
            <div class="verify-row state-new" id="vrow_${safeKey}">
                <div class="verify-dot dot-new" id="vdot_${safeKey}"></div>
                <div class="verify-value-col">
                    <div class="verify-orig-value">${item.value}</div>
                    <div class="verify-status-label lbl-new" id="vstatus_${safeKey}">🆕 Will be created</div>
                </div>
                <div class="verify-input-col">
                    <div class="verify-input-wrap">
                        <input class="verify-correction-input"
                               id="vinput_${safeKey}"
                               value="${item.value}"
                               placeholder="Correct spelling or leave as-is to create new..."
                               oninput="onVerifyInput('${key}', this.value)">
                    </div>
                    ${chipHtml}
                </div>
            </div>`;
    }).join('');
    return `
        <div class="verify-section">
            <div class="verify-section-title">
                <span class="material-symbols-outlined">${icon}</span>
                ${title}
            </div>
            ${rows}
        </div>`;
}

function onVerifyInput(key, rawValue) {
    const value = rawValue.trim();
    verificationCorrections[key] = value || key.split(':')[1];
    const safeKey = key.replace(/[^a-zA-Z0-9_-]/g, '_');
    const original = key.split(':').slice(1).join(':');
    const dot    = document.getElementById('vdot_' + safeKey);
    const status = document.getElementById('vstatus_' + safeKey);
    const row    = document.getElementById('vrow_' + safeKey);
    const input  = document.getElementById('vinput_' + safeKey);
    if (!dot) return;

    if (!value || value.toUpperCase() === original.toUpperCase()) {
        dot.className    = 'verify-dot dot-new';
        status.className = 'verify-status-label lbl-new';
        status.textContent = '🆕 Will be created';
        row.className    = 'verify-row state-new';
        input.classList.remove('input-corrected');
        verificationCorrections[key] = original;
    } else {
        dot.className    = 'verify-dot dot-corrected';
        status.className = 'verify-status-label lbl-corrected';
        status.textContent = `✏️ Will use: "${value}"`;
        row.className    = 'verify-row state-corrected';
        input.classList.add('input-corrected');
        verificationCorrections[key] = value;
    }
}

function applyVerifySuggestion(key, suggestion) {
    const safeKey = key.replace(/[^a-zA-Z0-9_-]/g, '_');
    const input = document.getElementById('vinput_' + safeKey);
    if (input) {
        input.value = suggestion;
        onVerifyInput(key, suggestion);
    }
}

function confirmAndApplyVerification() {
    // Collect final values from all inputs (in case user typed without triggering oninput)
    document.querySelectorAll('.verify-correction-input').forEach(inp => {
        const safeKey = inp.id.replace('vinput_', '');
        // Reverse-map safeKey back to original key by scanning verificationCorrections
        // Safe: just read the current value and update
        const currentVal = inp.value.trim();
        if (currentVal) {
            // Find the matching key (safeKey was built by replacing non-alnum with _)
            for (const k of Object.keys(verificationCorrections)) {
                if (k.replace(/[^a-zA-Z0-9_-]/g, '_') === safeKey) {
                    verificationCorrections[k] = currentVal;
                    break;
                }
            }
        }
    });

    // Apply corrections to pastedData.parsedStyles
    pastedData.parsedStyles.forEach(s => {
        if (!s.base_details) return;
        const catKey = 'cat:' + s.base_details.item_group;
        const clrKey = 'clr:' + s.base_details.color;
        const subKey = 'sub:' + s.base_details.sub_category;
        if (verificationCorrections[catKey]) s.base_details.item_group   = verificationCorrections[catKey];
        if (verificationCorrections[clrKey]) {
            s.base_details.color = verificationCorrections[clrKey].toUpperCase();
            // Also update sizes_config color if present
            s.sizes_config.forEach(sz => {
                if (!sz.color) sz.color = s.base_details.color;
            });
        }
        if (verificationCorrections[subKey]) s.base_details.sub_category = verificationCorrections[subKey];
    });

    // Re-render stats with corrected data
    renderStatsBar();

    // Show confirmed banner
    const confirmRow = document.querySelector('.verify-confirm-row');
    if (confirmRow) {
        confirmRow.innerHTML = `
            <div class="verify-ok-banner" style="flex:1;">
                <span class="material-symbols-outlined">check_circle</span>
                Verification confirmed! Corrections applied — Import is now enabled.
            </div>`;
    }

    verificationPassed = true;
    _unlockImport();
    toast('Verification confirmed! Click Import to proceed.', 'success');
}

function _unlockImport() {
    const btn = document.getElementById('btn-do-import');
    const validCount = pastedData.parsedStyles.filter(s => s.isValid).length;
    if (btn) btn.disabled = validCount === 0;
}

function clearPastePanel() {
    pastedData = { headers: [], sizeColumns: [], mappedColumns: {}, rows: [], parsedStyles: [] };
    verificationCorrections = {};
    verificationPassed = false;
    document.getElementById('paste-column-map').style.display = 'none';
    document.getElementById('paste-stats-bar').style.display = 'none';
    document.getElementById('paste-grid-wrapper').style.display = 'none';
    document.getElementById('paste-import-toolbar').style.display = 'none';
    document.getElementById('paste-verify-panel').style.display = 'none';
    document.getElementById('paste-progress-panel').classList.remove('active');
    document.getElementById('paste-grid-head').innerHTML = '';
    document.getElementById('paste-grid-body').innerHTML = '';
    document.getElementById('paste-zone').classList.remove('active', 'scanning');
    document.getElementById('sim-paste-capture').value = '';
    toast('Paste panel cleared. Ready for new data.', 'info');
}

async function executePivotImport() {
    const validStyles = pastedData.parsedStyles.filter(s => s.isValid);
    if (validStyles.length === 0) {
        toast('No valid styles to import!', 'error');
        return;
    }

    if (!verificationPassed) {
        toast('Please complete verification before importing.', 'warning');
        document.getElementById('paste-verify-panel').scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    if (!confirm(`This will import ${validStyles.length} style(s) and create size variant items with auto-generated EAN-13 barcodes.\n\nProceed?`)) {
        return;
    }

    const btn = document.getElementById('btn-do-import');
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined">hourglass_top</span> Importing...';

    const progressPanel = document.getElementById('paste-progress-panel');
    const progressBar = document.getElementById('paste-progress-bar');
    const progressLabel = document.getElementById('paste-progress-label');
    const progressDetail = document.getElementById('paste-progress-detail');
    progressPanel.classList.add('active');
    progressBar.style.width = '0%';
    progressLabel.textContent = `Importing ${validStyles.length} styles...`;
    progressDetail.textContent = 'Preparing payload...';

    try {
        // Build payload for backend
        const stylesPayload = validStyles.map(s => ({
            base_details: s.base_details,
            sizes_config: s.sizes_config,
        }));

        progressBar.style.width = '20%';
        progressDetail.textContent = 'Sending to server...';

        const res = await api('smriti_retail_os.item_master_api.import_pivot_item_master', {
            styles_json: JSON.stringify(stylesPayload)
        });

        progressBar.style.width = '100%';
        progressBar.style.background = 'linear-gradient(90deg, var(--success), #34d399)';

        const createdCount = res.created_count || 0;
        const updatedCount = res.updated_count || 0;
        const errorsCount = (res.errors || []).length;

        progressLabel.textContent = '✅ Import Complete!';
        progressDetail.textContent = `Created: ${createdCount} variants | Updated: ${updatedCount} | Errors: ${errorsCount}`;

        if (errorsCount > 0) {
            toast(`Import completed with ${errorsCount} error(s). Check console for details.`, 'warning');
            console.group(`❌ Import Errors (${errorsCount} rows failed):`);
            (res.errors || []).forEach(err => {
                console.error(`Row ${err.row_idx} | Article: ${err.article_no} | Error: ${err.error}`);
                if (err.detail) console.warn(err.detail);
            });
            console.groupEnd();

            // Show error list below progress bar
            const detail = document.getElementById('paste-progress-detail');
            const errorList = (res.errors || []).map(e =>
                `<div style="color:var(--danger); font-size:0.75rem; margin-top:4px;">
                    ✗ Row ${e.row_idx} | <b>${e.article_no || '?'}</b>: ${e.error}
                 </div>`
            ).join('');
            detail.innerHTML = `<div>${createdCount} created, ${updatedCount} updated, <span style="color:var(--danger)">${errorsCount} failed</span></div>${errorList}`;
        } else {
            toast(`Successfully imported ${createdCount} new variant(s) and updated ${updatedCount}!`, 'success');
        }

        btn.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Import Complete';

    } catch(e) {
        progressBar.style.width = '100%';
        progressBar.style.background = 'linear-gradient(90deg, var(--danger), #f87171)';
        progressLabel.textContent = '❌ Import Failed';
        progressDetail.textContent = e.message;
        toast('Import failed: ' + e.message, 'error');
        btn.disabled = false;
        btn.innerHTML = '<span class="material-symbols-outlined">cloud_upload</span> Retry Import';
    }
}


// ═══════════════════════════════════════════════════════════════════════════
//  ITEM LIST TAB — Load / Search / Edit / Delete
// ═══════════════════════════════════════════════════════════════════════════

let allItemListData = [];

async function loadItemList() {
    const tbody = document.getElementById('item-list-body');
    tbody.innerHTML = `<tr><td colspan="8" class="item-list-loading">
        <div class="spinner"></div>Loading items from database...
    </td></tr>`;

    try {
        // Fetch all template items (has_variants=1 means it's a style template)
        const items = await api('frappe.client.get_list', {
            doctype: 'Item',
            filters: { has_variants: 1 },
            fields: ['name', 'item_name', 'brand', 'item_group', 'description'],
            limit_page_length: 500,
            order_by: 'modified desc'
        });

        // For each template, get variant count and details
        allItemListData = [];
        for (const item of (items || [])) {
            // Get variant count
            const variants = await api('frappe.client.get_count', {
                doctype: 'Item',
                filters: { variant_of: item.name }
            });

            // Extract color from item name or attributes
            let color = '';
            let mrp = '';
            try {
                const details = await api('smriti_retail_os.item_master_api.get_style_details', {
                    article_no: item.name
                });
                color = details.color || '';
                mrp = details.mrp || '';
            } catch(e) { /* ignore */ }

            allItemListData.push({
                name: item.name,
                item_name: item.item_name || item.name,
                brand: item.brand || '',
                color: color,
                item_group: item.item_group || '',
                mrp: mrp,
                variant_count: variants || 0
            });
        }

        renderItemListTable(allItemListData);
    } catch(e) {
        tbody.innerHTML = `<tr><td colspan="8" class="item-list-empty">
            <span class="material-symbols-outlined">error</span>
            Failed to load items: ${e.message}
        </td></tr>`;
    }
}

function renderItemListTable(data) {
    const tbody = document.getElementById('item-list-body');
    const countEl = document.getElementById('item-list-count');

    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="item-list-empty">
            <span class="material-symbols-outlined">inventory_2</span>
            No items found.
        </td></tr>`;
        if (countEl) countEl.textContent = '0 items';
        return;
    }

    if (countEl) countEl.textContent = `${data.length} style${data.length !== 1 ? 's' : ''} found`;

    tbody.innerHTML = data.map(item => `
        <tr>
            <td class="item-code-cell">${escHtml(item.name)}</td>
            <td>${escHtml(item.item_name)}</td>
            <td>${escHtml(item.brand)}</td>
            <td>${escHtml(item.color)}</td>
            <td>${escHtml(item.item_group)}</td>
            <td>${item.mrp ? '₹' + Number(item.mrp).toLocaleString('en-IN') : '—'}</td>
            <td class="item-variants-cell">${item.variant_count} variant${item.variant_count !== 1 ? 's' : ''}</td>
            <td class="item-actions">
                <button class="btn-edit-item" onclick="editItem('${escAttr(item.name)}')" title="Edit this style">
                    <span class="material-symbols-outlined" style="font-size:16px;">edit</span> Edit
                </button>
                <button class="btn-delete-item" onclick="deleteItem('${escAttr(item.name)}', '${escAttr(item.item_name)}', ${item.variant_count})" title="Delete this style + all variants">
                    <span class="material-symbols-outlined" style="font-size:16px;">delete</span> Delete
                </button>
            </td>
        </tr>
    `).join('');
}

function escHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escAttr(str) {
    if (!str) return '';
    return String(str).replace(/\\/g,'\\\\').replace(/'/g,"\\'").replace(/"/g,'\\&quot;');
}

function filterItemList() {
    const q = (document.getElementById('item-list-search').value || '').toLowerCase().trim();
    if (!q) {
        renderItemListTable(allItemListData);
        return;
    }
    const filtered = allItemListData.filter(item =>
        (item.name || '').toLowerCase().includes(q) ||
        (item.item_name || '').toLowerCase().includes(q) ||
        (item.brand || '').toLowerCase().includes(q) ||
        (item.color || '').toLowerCase().includes(q) ||
        (item.item_group || '').toLowerCase().includes(q)
    );
    renderItemListTable(filtered);
}

function editItem(itemCode) {
    // Switch to Style Creator tab and load the item
    document.getElementById('style-code').value = itemCode;
    switchTab('manual');
    lookupStyle(itemCode);
    // Scroll to top
    document.querySelector('.content-area')?.scrollTo({ top: 0, behavior: 'smooth' });
    toast(`📝 Editing style "${itemCode}" — modify fields and click Save.`, 'info');
}

async function deleteItem(itemCode, itemName, variantCount) {
    const confirmed = confirm(
        `⚠️ Delete "${itemName}" (${itemCode})?\n\n` +
        `This action will:\n` +
        `• Delete the template item\n` +
        `• Delete ${variantCount} size variant(s)\n` +
        `• Delete all associated barcodes\n` +
        `• Delete all price lists\n\n` +
        `This CANNOT be undone!`
    );
    if (!confirmed) return;

    const reconfirm = confirm(`Last chance! Permanently delete "${itemCode}" and all its variants?`);
    if (!reconfirm) return;

    try {
        toast(`🗑️ Deleting ${itemCode} and ${variantCount} variant(s)...`, 'info');
        const result = await api(
            'smriti_retail_os.item_master_api.delete_style_and_variants',
            { style_code: itemCode }
        );
        toast(`✅ ${result.message || itemCode + ' deleted successfully'}`, 'success');
        // Refresh list
        loadItemList();
    } catch(e) {
        toast(`❌ Delete failed: ${e.message}`, 'error');
    }
}


// ═══════════════════════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════════════════════

window.onload = init;