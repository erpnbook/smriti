'use strict';

// ── Constants & State ────────────────────────────────────────
const CSRF = window.CSRF || '{{ csrf_token }}';
const CASHIER = window.CASHIER || '{{ cashier }}';
let loggedUser = CASHIER;

const PRESETS = {
    footwear: ['36','37','38','39','40','41','42'],
    garment:  ['XS','S','M','L','XL','XXL','3XL'],
    kids:     ['18','20','22','24','26','28','30'],
};

let state = {
    sizeColumns:  [...PRESETS.footwear],
    rows:         [],
    taxType:      'intrastate',
    companyInfo:  null,
    customerInfo: null,
    savedInvName: null,
    docstatus:    0,
    allInvoices:  [],
};

// ── API Wrapper ──────────────────────────────────────────────
async function api(method, params = {}) {
    const r = await fetch(`/api/method/${method}`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': CSRF },
        body: JSON.stringify(params)
    });
    const d = await r.json();
    if (d.exc) throw new Error(d._error_message || d.exc || 'API error');
    return d.message;
}

// ── Toast ────────────────────────────────────────────────────
function toast(msg, type = 'success') {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    const icons = { success:'check_circle', error:'error', info:'info' };
    t.innerHTML = `<span class="material-symbols-outlined">${icons[type]||'info'}</span><span>${msg}</span>`;
    c.appendChild(t);
    setTimeout(() => t.remove(), 4000);
}

function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

function togglePanel(id, btn) {
    const el = document.getElementById(id);
    const isHidden = el.style.display === 'none';
    el.style.display = isHidden ? '' : 'none';
    if (btn) {
        const icon = btn.querySelector('.material-symbols-outlined');
        if (icon) {
            icon.textContent = isHidden ? 'expand_less' : 'expand_more';
        }
    }
}

// ── Company Init ─────────────────────────────────────────────
async function loadCompanyDetails() {
    try {
        const c = await api('smriti_retail_os.sizewise_invoice_api.get_company_details');
        state.companyInfo = c;
        document.getElementById('co-name').textContent = c.company_name;
        const addr = c.address;
        let metaLines = [];
        if (addr.line1) metaLines.push(addr.line1);
        if (addr.line2) metaLines.push(addr.line2);
        if (addr.city || addr.state) metaLines.push([addr.city, addr.state, addr.pincode].filter(Boolean).join(', '));
        if (c.phone) metaLines.push('📞 ' + c.phone);
        if (c.email) metaLines.push('✉ ' + c.email);
        if (c.pan)   metaLines.push('PAN: ' + c.pan);
        document.getElementById('co-meta').innerHTML = metaLines.join('<br>');
        document.getElementById('co-gstin').textContent = c.gstin ? `GSTIN: ${c.gstin}` : 'GSTIN: Not Configured';
        document.getElementById('co-sig-company').textContent = c.company_name;

        if (c.bank) {
            document.getElementById('bank-name').value  = c.bank.bank_name || '';
            document.getElementById('bank-acno').value  = c.bank.account_no || '';
            document.getElementById('bank-ifsc').value  = c.bank.ifsc || '';
        }

        // Print header
        if (document.getElementById('p-company-name')) {
            document.getElementById('p-company-name').textContent = c.company_name;
        }
        if (document.getElementById('p-company-meta')) {
            document.getElementById('p-company-meta').innerHTML = metaLines.join(' | ');
        }
    } catch(e) {
        console.error('Company details error:', e);
        toast('Could not load company details. Using defaults.', 'info');
    }
}

// ── States List ──────────────────────────────────────────────
async function loadStates() {
    try {
        const states = await api('smriti_retail_os.sizewise_invoice_api.get_states_list');
        const sel = document.getElementById('place-of-supply');
        states.forEach(s => {
            const opt = document.createElement('option');
            opt.value = `${s.code}-${s.name}`;
            opt.textContent = `${s.code} — ${s.name}`;
            sel.appendChild(opt);
        });
    } catch(e) {
        console.error('States list error:', e);
    }
}

// ── Customer Search ──────────────────────────────────────────
let _custTimer = null;
async function searchCustomers(q) {
    clearTimeout(_custTimer);
    const dd = document.getElementById('cust-dropdown');
    if (!q) { dd.classList.remove('open'); return; }
    _custTimer = setTimeout(async () => {
        try {
            const results = await api('smriti_retail_os.sizewise_invoice_api.search_customers', { query: q });
            dd.innerHTML = '';
            if (!results.length) {
                dd.innerHTML = '<div class="search-item" style="color:var(--muted);">No customers found</div>';
            } else {
                results.forEach(c => {
                    const d = document.createElement('div');
                    d.className = 'search-item';
                    d.innerHTML = `<strong>${c.customer_name}</strong><small>${c.tax_id || 'No GSTIN'} · ${c.mobile_no || ''}</small>`;
                    d.onclick = () => selectCustomer(c.name, c.customer_name);
                    dd.appendChild(d);
                });
            }
            dd.classList.add('open');
        } catch(e) { toast('Customer search failed', 'error'); }
    }, 280);
}

async function selectCustomer(name, displayName) {
    document.getElementById('cust-search').value = displayName;
    document.getElementById('cust-dropdown').classList.remove('open');
    try {
        const c = await api('smriti_retail_os.sizewise_invoice_api.get_customer_details', { customer: name });
        state.customerInfo = c;
        document.getElementById('buyer-gstin').value  = c.gstin || '';
        document.getElementById('buyer-mobile').value = c.mobile_no || '';
        const a = c.address || {};
        const addrStr = [a.line1, a.line2, a.city, a.state, a.pincode].filter(Boolean).join(', ');
        document.getElementById('buyer-addr').value = addrStr || '';
        
        // Auto-select place of supply based on customer GSTIN state code
        if (c.gstin && c.gstin.length >= 2) {
            const stateCode = c.gstin.substring(0, 2);
            const sel = document.getElementById('place-of-supply');
            for (let opt of sel.options) {
                if (opt.value.startsWith(stateCode + '-')) {
                    sel.value = opt.value;
                    break;
                }
            }
        }
        
        detectTaxType();
        updatePrintHeader();
    } catch(e) {
        toast('Could not fetch customer details: ' + e.message, 'error');
    }
}

let _articleTimer = null;
/* ── Article Search Dropdown — Body Portal Implementation ────────────────
   The dropdown is a single #grid-article-portal div appended to <body>.
   It is positioned using position:fixed based on the input's
   getBoundingClientRect(), so it escapes all overflow:auto/.hidden parents
   (including .grid-wrap, .panel, .panel-body) and always renders on top.
   Active row ID is tracked in _articlePortalRid so selectArticle() can close it.
── */
let _articlePortalRid = null;

function _getOrCreateArticlePortal() {
    let portal = document.getElementById('grid-article-portal');
    if (!portal) {
        portal = document.createElement('div');
        portal.id = 'grid-article-portal';
        document.body.appendChild(portal);
    }
    return portal;
}

function _positionArticlePortal(inputEl) {
    const portal = _getOrCreateArticlePortal();
    const rect = inputEl.getBoundingClientRect();
    // Default: open below the input
    let top = rect.bottom + 4;
    const portalHeight = Math.min(220, window.innerHeight - rect.bottom - 8);
    // If not enough space below, open above
    if (portalHeight < 80 && rect.top > 220) {
        top = rect.top - Math.min(220, rect.top - 8) - 4;
    }
    portal.style.top    = top + 'px';
    portal.style.left   = rect.left + 'px';
    portal.style.width  = Math.max(rect.width, 240) + 'px';
    portal.style.maxHeight = Math.min(220, window.innerHeight - top - 8) + 'px';
}

async function searchArticles(rid, q, inputEl) {
    clearTimeout(_articleTimer);
    const portal = _getOrCreateArticlePortal();
    if (!q) {
        portal.classList.remove('open');
        _articlePortalRid = null;
        return;
    }
    _articlePortalRid = rid;
    _positionArticlePortal(inputEl);
    _articleTimer = setTimeout(async () => {
        try {
            const results = await api('smriti_retail_os.sizewise_invoice_api.search_items', { query: q });
            portal.innerHTML = '';
            if (!results.length) {
                const noRes = document.createElement('div');
                noRes.className = 'search-item';
                noRes.style.color = 'var(--muted)';
                noRes.style.fontSize = '0.75rem';
                noRes.textContent = 'No items found';
                portal.appendChild(noRes);
            } else {
                results.forEach(item => {
                    const d = document.createElement('div');
                    d.className = 'search-item';
                    d.innerHTML = `<strong>${esc(item.name)}</strong> <small>${esc(item.item_name || '')}</small>`;
                    d.onmousedown = (e) => {
                        // Use mousedown so it fires before the input's blur
                        e.preventDefault();
                        selectArticle(rid, item, inputEl);
                    };
                    portal.appendChild(d);
                });
            }
            _positionArticlePortal(inputEl);
            portal.classList.add('open');
        } catch(e) { console.error(e); }
    }, 250);
}

function selectArticle(rid, item, inputEl) {
    const row = state.rows.find(r => r._id === rid);
    if (!row) return;
    row.article = item.name;
    row.item_code = item.name;
    row.hsn_code = item.gst_hsn_code || '';
    
    // Set custom_gst_percentage if it exists or default to 12
    if (item.custom_gst_percentage) {
        row.gst_pct = parseFloat(item.custom_gst_percentage) || 12;
    }
    
    // Map item group as category
    row.category = item.item_group || '';
    
    // Auto-fill inputs in the DOM
    const tr = document.getElementById(`row-${rid}`);
    if (tr) {
        const artInput = tr.querySelector('.article-input');
        if (artInput) artInput.value = item.name;
        
        const catInput = tr.querySelector('input[placeholder="Category…"]');
        if (catInput) catInput.value = item.item_group || '';
        
        const hsnInput = tr.querySelector('input[placeholder="HSN…"]');
        if (hsnInput) hsnInput.value = item.gst_hsn_code || '';
        
        const gstSelect = tr.querySelector('select');
        if (gstSelect) gstSelect.value = row.gst_pct;
    }
    
    // Close the portal dropdown
    const portal = document.getElementById('grid-article-portal');
    if (portal) portal.classList.remove('open');
    _articlePortalRid = null;
    
    recalculate();
    handleArticleOrColorChange(rid);
}

document.addEventListener('click', e => {
    // Close customer search dropdown
    if (!e.target.closest('.search-wrap')) {
        const custDd = document.getElementById('cust-dropdown');
        if (custDd) custDd.classList.remove('open');
    }
    // Close article portal if clicking outside the portal and outside any article input
    const portal = document.getElementById('grid-article-portal');
    if (portal && !e.target.closest('#grid-article-portal') && !e.target.closest('.article-input')) {
        portal.classList.remove('open');
        _articlePortalRid = null;
    }
});

// Reposition portal on scroll of the grid so it tracks the input
document.addEventListener('DOMContentLoaded', () => {
    const gridWrap = document.getElementById('grid-wrap');
    if (gridWrap) {
        gridWrap.addEventListener('scroll', () => {
            const portal = document.getElementById('grid-article-portal');
            if (portal && portal.classList.contains('open') && _articlePortalRid !== null) {
                const activeInput = document.querySelector(`#row-${_articlePortalRid} .article-input`);
                if (activeInput) {
                    _positionArticlePortal(activeInput);
                } else {
                    portal.classList.remove('open');
                    _articlePortalRid = null;
                }
            }
        });
    }
});

function detectTaxType() {
    if (!state.companyInfo || !state.customerInfo) return;
    const compState = state.companyInfo.state_code;
    const buyerGST  = state.customerInfo.gstin || '';
    const buyerState = buyerGST.substring(0, 2);
    const pos = document.getElementById('place-of-supply').value.split('-')[0] || buyerState;
    setTaxType(compState && pos && compState === pos ? 'intrastate' : 'interstate');
}

function setTaxType(type) {
    state.taxType = type;
    document.getElementById('toggle-intra').classList.toggle('active', type === 'intrastate');
    document.getElementById('toggle-inter').classList.toggle('active', type === 'interstate');
    // Update HSN table headers
    if (type === 'intrastate') {
        document.getElementById('tax-col-1').textContent = 'CGST %';
        document.getElementById('tax-col-1-amt').textContent = 'CGST Amt';
        document.getElementById('tax-col-2').textContent = 'SGST %';
        document.getElementById('tax-col-2-amt').textContent = 'SGST Amt';
        document.getElementById('tot-cgst-row').style.display = '';
        document.getElementById('tot-sgst-row').style.display = '';
        document.getElementById('tot-igst-row').style.display = 'none';
    } else {
        document.getElementById('tax-col-1').textContent = 'IGST %';
        document.getElementById('tax-col-1-amt').textContent = 'IGST Amt';
        document.getElementById('tax-col-2').textContent = '';
        document.getElementById('tax-col-2-amt').textContent = '';
        document.getElementById('tot-cgst-row').style.display = 'none';
        document.getElementById('tot-sgst-row').style.display = 'none';
        document.getElementById('tot-igst-row').style.display = '';
    }
    recalculate();
}

// ── Size Columns ─────────────────────────────────────────────
function renderSizeTags() {
    const c = document.getElementById('size-tags-container');
    c.innerHTML = '';
    state.sizeColumns.forEach((sz, i) => {
        const tag = document.createElement('div');
        tag.className = 'size-tag';
        tag.innerHTML = `${sz}<span class="rm" onclick="removeSize(${i})">×</span>`;
        c.appendChild(tag);
    });
    rebuildGrid();
}

function removeSize(idx) {
    if (state.sizeColumns.length <= 1) { toast('Must have at least one size column', 'error'); return; }
    const sz = state.sizeColumns[idx];
    state.sizeColumns.splice(idx, 1);
    state.rows.forEach(r => { delete r.sizes[sz]; });
    renderSizeTags();
}

function loadPreset(key) {
    if (!PRESETS[key]) return;
    state.sizeColumns = [...PRESETS[key]];
    renderSizeTags();
    toast(`Loaded ${key} preset: ${state.sizeColumns.join(', ')}`, 'info');
}

function openAddSizeModal() {
    document.getElementById('new-size-input').value = '';
    openModal('modal-add-size');
    setTimeout(() => document.getElementById('new-size-input').focus(), 150);
}

function addSizeFromModal() {
    const v = document.getElementById('new-size-input').value.trim().toUpperCase();
    if (!v) { toast('Enter a size label', 'error'); return; }
    if (state.sizeColumns.includes(v)) { toast('Size already exists', 'error'); return; }
    state.sizeColumns.push(v);
    state.sizeColumns.sort((a, b) => parseFloat(a) - parseFloat(b));
    closeModal('modal-add-size');
    renderSizeTags();
    toast(`Size "${v}" added`, 'success');
}

// ── Grid Rendering ───────────────────────────────────────────
function rebuildGrid() {
    renderGridHeader();
    renderGridBody();
    recalculate();
}

function renderGridHeader() {
    const thead = document.getElementById('grid-thead');
    const sizes = state.sizeColumns;
    thead.innerHTML = `<tr>
        <th class="sticky-col sticky-0">#</th>
        <th class="sticky-col sticky-1">Article / Style</th>
        <th class="sticky-col sticky-2">Color</th>
        <th class="sticky-col sticky-3">Category</th>
        <th class="sticky-col sticky-4">Sub-Category</th>
        ${sizes.map(s => `<th class="size-col">${s}</th>`).join('')}
        <th style="min-width:55px;text-align:center;">TTL QTY</th>
        <th style="min-width:80px;">MRP (₹)</th>
        <th style="min-width:90px;">Rate/Unit</th>
        <th style="min-width:70px;">Disc%</th>
        <th style="min-width:60px;">GST%</th>
        <th style="min-width:90px;">HSN Code</th>
        <th style="min-width:100px;">Row Amount</th>
        <th style="min-width:36px;"></th>
    </tr>`;
}

let rowIdCounter = 0;
function addRow(data = {}) {
    const id = data._id || ++rowIdCounter;
    if (data._id && data._id > rowIdCounter) {
        rowIdCounter = data._id;
    }
    const row = {
        _id: id,
        article:      data.article      || '',
        color:        data.color        || '',
        category:     data.category     || '',
        sub_category: data.sub_category || '',
        sizes:        {},
        mrp:          data.mrp          || '',
        rate:         data.rate         || '',
        discount_percentage: data.discount_percentage || 0,
        gst_pct:      data.gst_pct      || 12,
        hsn_code:     data.hsn_code     || '',
        item_code:    data.item_code    || '',
    };
    state.sizeColumns.forEach(sz => {
        row.sizes[sz] = data.sizes ? (data.sizes[sz] || 0) : 0;
    });
    state.rows.push(row);
    appendRowToDOM(row);
    updateRowCount();
}

function appendRowToDOM(row) {
    const tbody = document.getElementById('grid-tbody');
    const tr = document.createElement('tr');
    tr.id = `row-${row._id}`;
    tr.dataset.rid = row._id;
    const rowIdx = state.rows.findIndex(r => r._id === row._id) + 1;

    tr.innerHTML = `
        <td class="sticky-col sticky-0" style="color:var(--muted);font-size:0.78rem;padding:4px 6px;">${rowIdx}</td>
        <td class="sticky-col sticky-1">
            <input class="cell-input article-input" style="min-width:100px;" placeholder="Article/Style…" value="${esc(row.article)}" autocomplete="off"
                oninput="searchArticles(${row._id}, this.value, this); updateRowField(${row._id}, 'article', this.value)"
                onfocus="searchArticles(${row._id}, this.value, this)"
                onblur="setTimeout(()=>{ const p=document.getElementById('grid-article-portal'); if(p && !p.matches(':hover')){p.classList.remove('open');} }, 180)">
        </td>
        <td class="sticky-col sticky-2"><input class="cell-input" style="min-width:80px;" placeholder="Color…" value="${esc(row.color)}"
            oninput="updateRowField(${row._id},'color',this.value)"></td>
        <td class="sticky-col sticky-3"><input class="cell-input" style="min-width:90px;" placeholder="Category…" value="${esc(row.category)}"
            oninput="updateRowField(${row._id},'category',this.value)"></td>
        <td class="sticky-col sticky-4"><input class="cell-input" style="min-width:90px;" placeholder="Sub-Cat…" value="${esc(row.sub_category)}"
            oninput="updateRowField(${row._id},'sub_category',this.value)"></td>
        ${state.sizeColumns.map(sz => {
            const qty = parseFloat(row.sizes[sz]) || 0;
            const hasQtyClass = qty > 0 ? 'has-qty' : '';
            return `
            <td class="size-cell">
                <input class="size-input ${hasQtyClass}" type="number" min="0" placeholder="0" value="${row.sizes[sz] || ''}"
                    oninput="updateSize(${row._id},'${sz}',this.value,this)" onchange="this.value=this.value||''">
            </td>`;
        }).join('')}
        <td class="readonly-cell row-ttl" id="ttl-${row._id}">0</td>
        <td><input class="cell-input" type="number" min="0" style="min-width:72px;" placeholder="₹MRP" value="${row.mrp || ''}"
            oninput="updateRowField(${row._id},'mrp',this.value);recalculate()"></td>
        <td><input class="cell-input" type="number" min="0" style="min-width:80px;" placeholder="₹Rate" value="${row.rate || ''}"
            oninput="updateRowField(${row._id},'rate',this.value);recalculate()"></td>
        <td><input class="cell-input" type="number" min="0" max="100" step="0.01" style="min-width:65px;" placeholder="Disc%" value="${row.discount_percentage || ''}"
            oninput="updateRowField(${row._id},'discount_percentage',this.value);recalculate()"></td>
        <td>
            <select class="cell-input" style="min-width:60px;" onchange="updateRowField(${row._id},'gst_pct',this.value);recalculate()">
                ${[0,5,12,18,28].map(g => `<option value="${g}" ${g==row.gst_pct?'selected':''}>${g}%</option>`).join('')}
            </select>
        </td>
        <td><input class="cell-input" style="min-width:80px;" placeholder="HSN…" value="${esc(row.hsn_code)}"
            oninput="updateRowField(${row._id},'hsn_code',this.value)"></td>
        <td class="row-amt" id="amt-${row._id}">₹0.00</td>
        <td><span class="rm-row material-symbols-outlined" onclick="removeRow(${row._id})">delete</span></td>
    `;
    tbody.appendChild(tr);
    calcRowTotals(row._id);
}

function renderGridBody() {
    document.getElementById('grid-tbody').innerHTML = '';
    const savedRows = [...state.rows];
    state.rows = [];
    savedRows.forEach(r => addRow(r));
}

function esc(s) { return String(s || '').replace(/"/g, '&quot;'); }

function updateRowField(rid, field, val) {
    const row = state.rows.find(r => r._id === rid);
    if (!row) return;
    row[field] = val;

    // Auto-helper: If user updates MRP, auto-calculate the tax-exclusive Rate!
    if (field === 'mrp') {
        const mrp = parseFloat(val) || 0;
        const gst = parseFloat(row.gst_pct) || 12;
        const rate = parseFloat((mrp / (1 + (gst / 100))).toFixed(2));
        row.rate = rate;
        
        // Update the Rate input element on the screen dynamically
        const rowEl = document.getElementById(`row-${rid}`);
        if (rowEl) {
            const rateInput = rowEl.querySelector('input[placeholder="₹Rate"]');
            if (rateInput) rateInput.value = rate || '';
        }
    }
    
    // Auto-helper: If user updates GST%, auto-recalculate Rate from MRP if MRP exists!
    if (field === 'gst_pct') {
        const mrp = parseFloat(row.mrp) || 0;
        if (mrp > 0) {
            const gst = parseFloat(val) || 0;
            const rate = parseFloat((mrp / (1 + (gst / 100))).toFixed(2));
            row.rate = rate;
            const rowEl = document.getElementById(`row-${rid}`);
            if (rowEl) {
                const rateInput = rowEl.querySelector('input[placeholder="₹Rate"]');
                if (rateInput) rateInput.value = rate || '';
            }
        }
    }

    // Auto-population helper on article/color lookup
    if (field === 'article' || field === 'color') {
        handleArticleOrColorChange(rid);
    }

    // Recalculate row totals in the DOM dynamically
    calcRowTotals(rid);
}

function updateSize(rid, sz, val, el) {
    const row = state.rows.find(r => r._id === rid);
    const qty = parseFloat(val) || 0;
    if (row) { row.sizes[sz] = qty; }
    if (el) {
        el.classList.toggle('has-qty', qty > 0);
    }
    calcRowTotals(rid);
    recalculate();
}

function calcRowTotals(rid) {
    const row = state.rows.find(r => r._id === rid);
    if (!row) return;
    const ttl = state.sizeColumns.reduce((s, sz) => s + (parseFloat(row.sizes[sz]) || 0), 0);
    const rate = parseFloat(row.rate) || 0;
    const disc = parseFloat(row.discount_percentage) || 0;
    const amt  = ttl * rate * (1 - disc / 100);
    const ttlEl = document.getElementById(`ttl-${rid}`);
    const amtEl = document.getElementById(`amt-${rid}`);
    if (ttlEl) ttlEl.textContent = ttl;
    if (amtEl) amtEl.textContent = `₹${amt.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}`;
}

function removeRow(rid) {
    const idx = state.rows.findIndex(r => r._id === rid);
    if (idx !== -1) state.rows.splice(idx, 1);
    const tr = document.getElementById(`row-${rid}`);
    if (tr) tr.remove();
    updateRowCount();
    recalculate();
}


// ══════════════════════════════════════════════════════════════
// ── BARCODE SCAN FEATURE ──────────────────────────────────────
// ══════════════════════════════════════════════════════════════

// Buffer for keyboard-wedge HID scanners (fire chars rapidly → Enter)
let _scanBuffer = '';
let _scanBufTimer = null;
const SCAN_DEBOUNCE_MS = 80; // HID scanners complete in < 80ms per char

/**
 * Show feedback label beside the scan bar.
 * type: 'success' | 'danger' | 'muted'
 */
function showScanStatus(msg, type = 'muted') {
    const el = document.getElementById('scan-status-label');
    if (!el) return;
    el.textContent = msg;
    el.className = `scan-status-${type}`;
    clearTimeout(el._clearTimer);
    el._clearTimer = setTimeout(() => {
        el.textContent = '';
        el.className = 'scan-status-muted';
    }, 5000);
}

/**
 * Flash the scan bar input — green on success, red on error.
 */
function flashScanBar(success = true) {
    const inp = document.getElementById('scan-bar-input');
    if (!inp) return;
    const cls = success ? 'scan-flash' : 'scan-error-flash';
    inp.classList.remove('scan-flash', 'scan-error-flash');
    void inp.offsetWidth; // force reflow to restart animation
    inp.classList.add(cls);
    setTimeout(() => inp.classList.remove(cls), 400);
}

/**
 * Core: resolve barcode via API and apply to grid.
 */
async function processBarcode(barcode) {
    barcode = (barcode || '').trim();
    if (barcode.length < 2) return;

    showScanStatus('⏳ Resolving…', 'muted');

    let result;
    try {
        result = await api('smriti_retail_os.sizewise_invoice_api.resolve_barcode', { barcode });
    } catch (err) {
        flashScanBar(false);
        showScanStatus(`❌ API error`, 'danger');
        toast(`Barcode resolve error: ${err.message || err}`, 'error');
        return;
    }

    if (!result || result.error) {
        flashScanBar(false);
        const errMsg = result ? result.error : 'Not found';
        showScanStatus(`❌ ${errMsg}: ${barcode}`, 'danger');
        toast(`Barcode not found: ${barcode}`, 'error');
        return;
    }

    flashScanBar(true);
    applyScanToGrid(result);
}

/**
 * Apply a resolved barcode result to the sizewise grid.
 * Finds or creates the Article+Color row, then increments size qty.
 */
function applyScanToGrid(result) {
    const article      = (result.article      || '').trim();
    const color        = (result.color        || '').trim();
    const size         = result.size ? String(result.size).trim() : null;
    const mrp          = parseFloat(result.mrp)      || 0;
    const rate         = parseFloat(result.rate)     || 0;
    const gst_pct      = parseFloat(result.gst_pct)  || 12;
    const hsn_code     = result.hsn_code     || '';
    const category     = result.category     || '';
    const sub_category = result.sub_category || '';

    // 1. Find existing row for this article + color (case-insensitive)
    let row = state.rows.find(r =>
        r.article.trim().toUpperCase() === article.toUpperCase() &&
        r.color.trim().toUpperCase()   === color.toUpperCase()
    );

    // 2. Create new row if not found
    if (!row) {
        addRow({ article, color, category, sub_category, mrp, rate, gst_pct, hsn_code });
        row = state.rows[state.rows.length - 1];
        // Scroll grid to bottom so user sees the new row
        const gw = document.getElementById('grid-wrap');
        if (gw) gw.scrollTop = gw.scrollHeight;
    }

    // 3. Auto-add size column if not present
    if (size && !state.sizeColumns.includes(size)) {
        state.sizeColumns.push(size);
        state.sizeColumns.sort((a, b) => parseFloat(a) - parseFloat(b));
        renderGridHeader();
        renderGridBody();
        // Re-acquire row reference after full re-render
        row = state.rows.find(r =>
            r.article.trim().toUpperCase() === article.toUpperCase() &&
            r.color.trim().toUpperCase()   === color.toUpperCase()
        );
    }

    // 4. Increment qty for this size
    if (size && row) {
        const prevQty = parseFloat(row.sizes[size]) || 0;
        const newQty  = prevQty + 1;
        row.sizes[size] = newQty;

        // Update the DOM input cell for this size column
        const rowEl   = document.getElementById(`row-${row._id}`);
        if (rowEl) {
            const sizeIdx   = state.sizeColumns.indexOf(size);
            const sizeInputs = rowEl.querySelectorAll('.size-input');
            if (sizeInputs[sizeIdx]) {
                sizeInputs[sizeIdx].value = newQty;
                sizeInputs[sizeIdx].classList.add('has-qty');
                // Brief highlight animation on the cell
                sizeInputs[sizeIdx].style.boxShadow = '0 0 0 3px rgba(16,185,129,0.4)';
                setTimeout(() => {
                    if (sizeInputs[sizeIdx]) sizeInputs[sizeIdx].style.boxShadow = '';
                }, 800);
            }
        }

        calcRowTotals(row._id);
        recalculate();

        const label = `${article} ${color} Sz:${size}`;
        showScanStatus(`✅ ${label} → Qty ${newQty}`, 'success');
        toast(`${label} → Qty ${newQty}`, 'success');
    } else if (!size && row) {
        // Barcode resolved to a template/non-size item
        showScanStatus(`⚠ No size detected — row created: ${article} ${color}`, 'danger');
        toast(`No size attribute for: ${result.item_code}`, 'error');
    }
}

// ══════════════════════════════════════════════════════════════
// PDT IMPORT — File Upload, Column Mapping, Preview, Confirm
// ══════════════════════════════════════════════════════════════

/** State for current PDT import session */
let pdtState = {
    fileContent: null,   // base64 encoded file content
    fileType: null,      // 'csv' | 'tsv' | 'xlsx'
    fileName: null,
    allHeaders: [],      // all columns detected in file
    mapping: {},         // { barcode: 'BARCODE NO', price: 'MRP', ... }
    previewRows: [],     // resolved rows from backend
};

/** Triggers the hidden file input */
function triggerPdtUpload() {
    const input = document.getElementById('pdt-file-input');
    input.value = ''; // reset so same file can be re-selected
    input.click();
}

/** Reads file, calls backend to detect columns, opens mapping modal */
async function handlePdtUpload(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];

    // File size check (5MB)
    if (file.size > 5 * 1024 * 1024) {
        toast('PDT file too large. Maximum 5MB allowed.', 'error');
        return;
    }

    // Detect file type
    const ext = file.name.split('.').pop().toLowerCase();
    const typeMap = { csv: 'csv', tsv: 'tsv', txt: 'tsv', xlsx: 'xlsx' };
    const fileType = typeMap[ext] || 'csv';

    pdtState.fileName = file.name;
    pdtState.fileType = fileType;

    // Read file as base64
    const reader = new FileReader();
    reader.onload = async (e) => {
        const base64 = e.target.result.split(',')[1]; // strip data: prefix
        pdtState.fileContent = base64;

        try {
            toast('Detecting columns…', 'info');
            const result = await api(
                'smriti_retail_os.sizewise_invoice_api.get_pdt_column_map',
                { file_content: base64, file_type: fileType }
            );

            pdtState.allHeaders = result.headers || [];
            pdtState.mapping    = result.mapping  || {};

            renderPdtMappingForm();
            document.getElementById('pdt-file-name').textContent = file.name;
            closeModal('modal-pdt-preview');
            openModal('modal-pdt-mapping');
        } catch (err) {
            toast('Failed to read PDT file: ' + (err.message || err), 'error');
        }
    };
    reader.readAsDataURL(file);
}

/** Renders the column-mapping dropdowns inside the mapping modal */
function renderPdtMappingForm() {
    const FIELD_LABELS = [
        { key: 'barcode',  label: '🔖 Barcode',    required: true },
        { key: 'price',    label: '💰 Price / MRP', required: false },
        { key: 'discount', label: '🏷 Discount %',  required: false },
        { key: 'qty',      label: '📦 Quantity',    required: false },
        { key: 'tax',      label: '📊 GST %',       required: false },
    ];

    const container = document.getElementById('pdt-column-form');
    container.innerHTML = '';

    FIELD_LABELS.forEach(({ key, label, required }) => {
        const currentVal = pdtState.mapping[key] || '';
        const options = pdtState.allHeaders.map(h =>
            `<option value="${h}" ${h === currentVal ? 'selected' : ''}>${h}</option>`
        ).join('');

        const row = document.createElement('div');
        row.style.cssText = 'display:flex;align-items:center;gap:12px;';
        row.innerHTML = `
            <label style="min-width:130px;font-size:0.82rem;font-weight:500;">
                ${label}${required ? ' <span style="color:#ef4444;">*</span>' : ''}
            </label>
            <select id="pdt-map-${key}" style="flex:1;background:var(--card2);border:1px solid var(--border2);color:var(--text);border-radius:var(--radius-sm);padding:6px 10px;font-size:0.82rem;" onchange="onPdtMappingChange()">
                <option value="">— Not mapped (use Item Master) —</option>
                ${options}
            </select>
        `;
        container.appendChild(row);
    });

    onPdtMappingChange(); // initial validation
}

/** Enable/disable Preview button based on whether Barcode is mapped */
function onPdtMappingChange() {
    const barcodeVal = document.getElementById('pdt-map-barcode')?.value || '';
    const previewBtn = document.getElementById('pdt-preview-btn');
    if (previewBtn) previewBtn.disabled = !barcodeVal;
}

/** Gathers mapping, calls backend preview API, renders preview table */
async function previewPdtImport() {
    // Gather current mapping from selects
    const keys = ['barcode', 'price', 'discount', 'qty', 'tax'];
    const mapping = {};
    keys.forEach(k => {
        const el = document.getElementById(`pdt-map-${k}`);
        if (el && el.value) mapping[k] = el.value;
    });
    pdtState.mapping = mapping;

    if (!mapping.barcode) {
        toast('Barcode column must be mapped before preview.', 'error');
        return;
    }

    try {
        const previewBtn = document.getElementById('pdt-preview-btn');
        if (previewBtn) { previewBtn.disabled = true; previewBtn.textContent = 'Loading…'; }

        const rows = await api(
            'smriti_retail_os.sizewise_invoice_api.preview_pdt_import',
            {
                file_content: pdtState.fileContent,
                file_type:    pdtState.fileType,
                mapping:      mapping,
            }
        );

        pdtState.previewRows = rows || [];
        renderPdtPreviewTable(pdtState.previewRows);
        closeModal('modal-pdt-mapping');
        openModal('modal-pdt-preview');
    } catch (err) {
        toast('Preview failed: ' + (err.message || err), 'error');
    } finally {
        const previewBtn = document.getElementById('pdt-preview-btn');
        if (previewBtn) { previewBtn.disabled = false; previewBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:15px;">preview</span> Preview Import'; }
    }
}

/** Renders resolved rows into the preview table */
function renderPdtPreviewTable(rows) {
    const tbody = document.getElementById('pdt-preview-tbody');
    const srcIcon = { pdt: '†', item_master: '★', default: '○', not_found: '?' };
    const srcColor = { pdt: '#818cf8', item_master: '#fbbf24', default: '#6ee7b7', not_found: '#9ca3af' };

    let validCount = 0, errorCount = 0;

    tbody.innerHTML = rows.map((row, i) => {
        const hasError = !!row.error;
        if (hasError) errorCount++; else validCount++;

        const fmt = (val, src) => {
            const icon = srcIcon[src] || '';
            const color = srcColor[src] || 'inherit';
            const numVal = (val !== null && val !== undefined) ? Number(val).toFixed(2) : '—';
            return `${numVal} <span style="color:${color};font-size:0.7rem;">${icon}</span>`;
        };

        const statusCell = hasError
            ? `<span style="color:#ef4444;font-size:0.72rem;">❌ ${row.error}</span>`
            : `<span style="color:#10b981;font-size:0.72rem;">✓ OK</span>`;

        return `<tr style="border-bottom:1px solid var(--border);${hasError ? 'opacity:0.6;' : ''}">
            <td style="padding:6px 10px;color:var(--muted);">${i + 1}</td>
            <td style="padding:6px 10px;font-family:monospace;font-size:0.75rem;">${row.barcode}</td>
            <td style="padding:6px 10px;">${row.article || '—'}</td>
            <td style="padding:6px 10px;">${row.color || '—'}</td>
            <td style="padding:6px 10px;">${row.size || '—'}</td>
            <td style="padding:6px 10px;text-align:right;">${fmt(row.price, row._price_source)}</td>
            <td style="padding:6px 10px;text-align:right;">${fmt(row.discount, row._discount_source)}</td>
            <td style="padding:6px 10px;text-align:right;">${fmt(row.tax, row._tax_source)}</td>
            <td style="padding:6px 10px;text-align:right;font-weight:600;">${fmt(row.qty, row._qty_source)}</td>
            <td style="padding:6px 10px;">${statusCell}</td>
        </tr>`;
    }).join('');

    document.getElementById('pdt-preview-count').textContent  = rows.length;
    document.getElementById('pdt-preview-valid').textContent  = validCount;
    document.getElementById('pdt-preview-errors').textContent = errorCount;

    const confirmBtn = document.getElementById('pdt-confirm-btn');
    if (confirmBtn) confirmBtn.disabled = validCount === 0;
}

/** Iterates through valid preview rows and merges them into the grid via applyScanToGrid */
function confirmPdtImport() {
    const validRows = pdtState.previewRows.filter(r => !r.error && r.item_code);
    if (!validRows.length) {
        toast('No valid rows to import.', 'error');
        return;
    }

    let imported = 0;
    validRows.forEach(row => {
        // Build a result object compatible with applyScanToGrid
        const result = {
            item_code:    row.item_code,
            article:      row.article      || '',
            color:        row.color        || '',
            size:         row.size         || '',
            mrp:          row.price        || 0,
            rate:         row.rate         || 0,
            gst_pct:      row.tax          || 12,
            hsn_code:     row.hsn_code     || '',
            category:     row.category     || '',
            sub_category: row.sub_category || '',
        };

        // Apply qty — PDT rows may have qty > 1; call applyScanToGrid qty times
        const qty = Math.max(1, Math.round(parseFloat(row.qty) || 1));
        for (let i = 0; i < qty; i++) {
            applyScanToGrid(result);
        }
        imported++;
    });

    closeModal('modal-pdt-preview');
    toast(`✅ PDT Import complete — ${imported} item(s) merged into grid.`, 'success');

    // Reset state
    pdtState = { fileContent: null, fileType: null, fileName: null, allHeaders: [], mapping: {}, previewRows: [] };
}

// ── Scan Bar Input: Enter key handler ─────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const scanInput = document.getElementById('scan-bar-input');
    if (!scanInput) return;

    scanInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const val = scanInput.value.trim();
            if (val) {
                processBarcode(val);
                scanInput.value = '';
            }
        }
    });

    // Clicking outside scan bar removes focus gracefully
    scanInput.addEventListener('blur', () => {
        // Re-focus after short delay if nothing else was clicked
        // (helps with HID scanners that lose focus)
    });
});

// ── Global keyboard-wedge listener (HID USB / Bluetooth scanners) ──
// Most HID scanners work as a keyboard: fire chars very fast + Enter.
// This listener captures barcode characters when NO input is focused.
(function initHIDScanListener() {
    document.addEventListener('keydown', (e) => {
        const active = document.activeElement;
        const tag    = active ? active.tagName.toUpperCase() : '';

        // If user is typing in any input/textarea/select, don't intercept
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return;
        // If a modal is open, don't intercept
        if (document.querySelector('.modal.open')) return;

        if (e.key === 'Enter') {
            if (_scanBuffer.length >= 3) {
                processBarcode(_scanBuffer.trim());
            }
            _scanBuffer = '';
            clearTimeout(_scanBufTimer);
        } else if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
            _scanBuffer += e.key;
            clearTimeout(_scanBufTimer);
            // Auto-flush if scanner takes too long (safety net)
            _scanBufTimer = setTimeout(() => { _scanBuffer = ''; }, 600);
        }
    });
})();

// ── END BARCODE SCAN FEATURE ──────────────────────────────────

function clearGrid() {
    if (!state.rows.length || confirm('Clear all rows?')) {
        state.rows = [];
        document.getElementById('grid-tbody').innerHTML = '';
        rowIdCounter = 0;
        updateRowCount();
        recalculate();
    }
}

function updateRowCount() {
    document.getElementById('grid-row-count').textContent = `— ${state.rows.length} rows`;
}

// ── Recalculate Totals ────────────────────────────────────────
function recalculate() {
    let totalQty = 0, totalTaxable = 0, totalTax = 0;
    const hsnMap = {}; // key: hsn+gst_pct

    state.rows.forEach(row => {
        const qty = state.sizeColumns.reduce((s, sz) => s + (parseFloat(row.sizes[sz]) || 0), 0);
        const rate    = parseFloat(row.rate)    || 0;
        const disc    = parseFloat(row.discount_percentage) || 0;
        const gstPct  = parseFloat(row.gst_pct) || 0;
        const hsn     = row.hsn_code || 'N/A';
        const taxable = qty * rate * (1 - disc / 100);
        const tax     = taxable * gstPct / 100;

        totalQty     += qty;
        totalTaxable += taxable;
        totalTax     += tax;

        const key = `${hsn}|${gstPct}`;
        if (!hsnMap[key]) hsnMap[key] = { hsn, gstPct, taxable:0, tax:0, cat:row.category || '' };
        hsnMap[key].taxable += taxable;
        hsnMap[key].tax     += tax;
    });

    const grandExact  = totalTaxable + totalTax;
    const grandRounded = Math.round(grandExact);
    const roundoff    = grandRounded - grandExact;

    // Update totals panel
    document.getElementById('tot-qty').textContent      = totalQty;
    document.getElementById('tot-rows').textContent     = state.rows.length;
    document.getElementById('tot-taxable').textContent  = fmtINR(totalTaxable);
    document.getElementById('tot-roundoff').textContent = fmtINR(roundoff);
    document.getElementById('tot-grand').textContent    = fmtINR(grandRounded);

    if (state.taxType === 'intrastate') {
        const half = totalTax / 2;
        document.getElementById('tot-cgst').textContent = fmtINR(half);
        document.getElementById('tot-sgst').textContent = fmtINR(half);
    } else {
        document.getElementById('tot-igst').textContent = fmtINR(totalTax);
    }

    // Amount in words
    document.getElementById('amount-words').textContent = numberToWords(grandRounded);

    // HSN Table
    renderHSNTable(hsnMap);

    // Print header
    updatePrintHeader(grandRounded);
}

function fmtINR(n) {
    const abs = Math.abs(n);
    const sign = n < 0 ? '-' : '';
    return sign + '₹' + abs.toLocaleString('en-IN', { minimumFractionDigits:2, maximumFractionDigits:2 });
}

function renderHSNTable(hsnMap) {
    const tbody = document.getElementById('hsn-tbody');
    const tfoot = document.getElementById('hsn-tfoot');
    const isIntra = state.taxType === 'intrastate';
    tbody.innerHTML = '';
    let totTaxable = 0, totTax = 0;

    Object.values(hsnMap).forEach(h => {
        const half = h.tax / 2;
        const halfPct = h.gstPct / 2;
        totTaxable += h.taxable;
        totTax     += h.tax;
        const tr = document.createElement('tr');
        tr.innerHTML = isIntra
            ? `<td>${h.hsn}</td><td>${h.cat}</td><td style="text-align:right;">${fmtINR(h.taxable)}</td>
               <td style="text-align:center;">${halfPct}%</td><td style="text-align:right;">${fmtINR(half)}</td>
               <td style="text-align:center;">${halfPct}%</td><td style="text-align:right;">${fmtINR(half)}</td>
               <td style="text-align:right;">${fmtINR(h.tax)}</td>`
            : `<td>${h.hsn}</td><td>${h.cat}</td><td style="text-align:right;">${fmtINR(h.taxable)}</td>
               <td style="text-align:center;">${h.gstPct}%</td><td style="text-align:right;">${fmtINR(h.tax)}</td>
               <td></td><td></td>
               <td style="text-align:right;">${fmtINR(h.tax)}</td>`;
        tbody.appendChild(tr);
    });

    tfoot.innerHTML = isIntra
        ? `<tr><td colspan="2"><strong>Total</strong></td>
           <td style="text-align:right;">${fmtINR(totTaxable)}</td>
           <td></td><td style="text-align:right;">${fmtINR(totTax/2)}</td>
           <td></td><td style="text-align:right;">${fmtINR(totTax/2)}</td>
           <td style="text-align:right;">${fmtINR(totTax)}</td></tr>`
        : `<tr><td colspan="2"><strong>Total</strong></td>
           <td style="text-align:right;">${fmtINR(totTaxable)}</td>
           <td></td><td style="text-align:right;">${fmtINR(totTax)}</td>
           <td></td><td></td>
           <td style="text-align:right;">${fmtINR(totTax)}</td></tr>`;
}

// ── Amount in Words (Indian) ─────────────────────────────────
function numberToWords(n) {
    const ones = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine',
        'Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen'];
    const tens = ['','','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety'];
    function convert(x) {
        if (x === 0) return '';
        if (x < 20)  return ones[x] + ' ';
        if (x < 100) return tens[Math.floor(x/10)] + (x%10 ? ' '+ones[x%10] : '') + ' ';
        if (x < 1000)    return ones[Math.floor(x/100)] + ' Hundred ' + convert(x%100);
        if (x < 100000)  return convert(Math.floor(x/1000)) + 'Thousand ' + convert(x%1000);
        if (x < 10000000)return convert(Math.floor(x/100000)) + 'Lakh ' + convert(x%100000);
        return convert(Math.floor(x/10000000)) + 'Crore ' + convert(x%10000000);
    }
    const i = Math.floor(n);
    const p = Math.round((n - i) * 100);
    let w = 'INR ';
    w += i > 0 ? convert(i).trim() : 'Zero';
    if (p > 0) w += ' and ' + convert(p).trim() + ' Paise';
    return w + ' Only';
}

// ── Auto-Population from Item Master on Article/Color Lookup ──────────
let _lookupTimers = {};
function handleArticleOrColorChange(rid, debounce = true) {
    if (!debounce) {
        return executeLookup(rid);
    }
    clearTimeout(_lookupTimers[rid]);
    return new Promise((resolve) => {
        _lookupTimers[rid] = setTimeout(async () => {
            await executeLookup(rid);
            resolve();
        }, 300);
    });
}

async function executeLookup(rid) {
    const row = state.rows.find(r => r._id === rid);
    if (!row || !row.article) return;
    
    try {
        const details = await api('smriti_retail_os.sizewise_invoice_api.get_item_details_by_article', {
            article: row.article,
            color: row.color
        });
        
        if (details && details.article) {
            // Update row state
            row.category     = details.category     || row.category;
            row.sub_category = details.sub_category || row.sub_category;
            row.hsn_code     = details.hsn_code     || row.hsn_code;
            row.mrp          = details.mrp          || row.mrp;
            row.gst_pct      = details.gst_pct      || row.gst_pct;
            row.rate         = details.rate         || row.rate;
            
            // Update input values in the DOM
            const tr = document.getElementById(`row-${rid}`);
            if (tr) {
                const catInput = tr.querySelector('input[placeholder="Category…"]');
                if (catInput) catInput.value = row.category;
                
                const subInput = tr.querySelector('input[placeholder="Sub-Cat…"]');
                if (subInput) subInput.value = row.sub_category;
                
                const hsnInput = tr.querySelector('input[placeholder="HSN…"]');
                if (hsnInput) hsnInput.value = row.hsn_code;
                
                const mrpInput = tr.querySelector('input[placeholder="₹MRP"]');
                if (mrpInput) mrpInput.value = row.mrp || '';
                
                const rateInput = tr.querySelector('input[placeholder="₹Rate"]');
                if (rateInput) rateInput.value = row.rate || '';
                
                const gstSelect = tr.querySelector('select');
                if (gstSelect) gstSelect.value = row.gst_pct;
            }
            
            calcRowTotals(rid);
            recalculate();
        }
    } catch (e) {
        console.error('Auto-population from Item Master failed:', e);
    }
}

// ── Smart Excel Paste Importer ────────────────────────────────
async function importExcelFromTextArea() {
    const text = document.getElementById('excel-paste-text').value;
    if (!text.trim()) { toast('Please paste some Excel data first', 'error'); return; }
    
    closeModal('modal-excel-paste');
    document.getElementById('excel-paste-text').value = '';
    
    try {
        const lines = text.split('\n').map(l => l.replace(/\r$/, '')).filter(l => l.trim());
        if (lines.length === 0) { toast('No data found', 'error'); return; }

        const COL_ALIASES = {
            article:     ['ARTICLE', 'STYLE', 'STYLE CODE', 'ARTICLE NO', 'ARTICLE CODE', 'ART', 'ART NO', 'PRODUCT STYLE CODE'],
            color:       ['COLOR', 'COLOUR', 'CLR'],
            category:    ['CATOGARY', 'CATEGORY', 'CAT', 'DEPT', 'DEPARTMENT'],
            sub_category:['SUB-CATEGORY', 'SUB CATEGORY', 'SUB - CATO', 'SUB-CATO', 'SUB CATO', 'DESCRIPTION', 'DESC', 'ITEM DESCRIPTION', 'ITEM NAME'],
            mrp:         ['MRP', 'PLANNED MRP'],
            rate:        ['RATE', 'UNIT RATE', 'SELLING PRICE', 'PRICE', 'TAXABLE RATE', 'TAXABLE VALUE'],
            discount:    ['DISCOUNT', 'DISC', 'DISCOUNT%', 'DISCOUNT PCT', 'DISC %', 'DISC%', 'LINE DISCOUNT', 'DISCOUNT_PERCENTAGE'],
            gst_pct:     ['GST%', 'GST', 'TAX%', 'GST PCT', 'GST PERCENTAGE', 'TAX RATE'],
            hsn_code:    ['HSN CODE', 'HSN', 'HSN/SAC', 'HSN_CODE']
        };

        const SIZE_PATTERNS = /^(\d{1,3}(\.\d)?|XXS|XS|S|M|L|XL|XXL|XXXL|2XL|3XL|4XL|5XL|FREE|F|UK\d+|EU\d+|US\d+)$/i;

        const firstRowCells = lines[0].split('\t').map(c => c.trim().toUpperCase());
        let hasHeader = false;
        let mappedColumns = {};
        let sizeColumns = {}; // szLabel -> colIdx

        firstRowCells.forEach((cell, idx) => {
            for (const [key, aliases] of Object.entries(COL_ALIASES)) {
                if (aliases.includes(cell)) {
                    mappedColumns[key] = idx;
                    hasHeader = true;
                }
            }
            if (state.sizeColumns.includes(cell) || SIZE_PATTERNS.test(cell)) {
                sizeColumns[cell] = idx;
                hasHeader = true;
            }
        });

        let startLineIdx = 0;
        let added = 0;

        if (hasHeader) {
            startLineIdx = 1;
            const matchedSizes = Object.keys(sizeColumns);
            if (matchedSizes.length > 0) {
                const newSizes = [...state.sizeColumns];
                matchedSizes.forEach(s => {
                    if (!newSizes.includes(s)) newSizes.push(s);
                });
                state.sizeColumns = newSizes;
                state.sizeColumns.sort((a, b) => parseFloat(a) - parseFloat(b));
                renderSizeTags();
            }
        } else {
            mappedColumns = { article: 0, color: 1, category: 2, sub_category: 3 };
            state.sizeColumns.forEach((sz, idx) => { sizeColumns[sz] = 4 + idx; });
            const base = 4 + state.sizeColumns.length;
            mappedColumns.mrp = base;
            mappedColumns.rate = base + 1;
            mappedColumns.gst_pct = base + 2;
            mappedColumns.hsn_code = base + 3;
        }

        let pendingAutoCompletes = [];

        for (let i = startLineIdx; i < lines.length; i++) {
            const cells = lines[i].split('\t').map(c => c.trim());
            if (cells.length < 2 || cells.every(c => !c)) continue;

            const article = (mappedColumns.article !== undefined ? cells[mappedColumns.article] : '').trim();
            const color = (mappedColumns.color !== undefined ? cells[mappedColumns.color] : '').trim().toUpperCase();
            
            const rowData = {
                article:      article,
                color:        color,
                category:     (mappedColumns.category !== undefined ? cells[mappedColumns.category] : '').trim(),
                sub_category: (mappedColumns.sub_category !== undefined ? cells[mappedColumns.sub_category] : '').trim(),
                sizes:        {},
                mrp:          0,
                rate:         0,
                discount_percentage: 0,
                gst_pct:      12,
                hsn_code:     ''
            };

            state.sizeColumns.forEach(sz => {
                const colIdx = sizeColumns[sz];
                rowData.sizes[sz] = colIdx !== undefined ? (parseFloat(cells[colIdx]) || 0) : 0;
            });

            const parseNum = (val) => parseFloat(String(val || '').replace(/[^0-9.]/g, '')) || 0;
            
            if (mappedColumns.mrp !== undefined) rowData.mrp = parseNum(cells[mappedColumns.mrp]);
            if (mappedColumns.rate !== undefined) rowData.rate = parseNum(cells[mappedColumns.rate]);
            if (mappedColumns.discount !== undefined) rowData.discount_percentage = parseNum(cells[mappedColumns.discount]);
            if (mappedColumns.gst_pct !== undefined) {
                const gp = parseNum(cells[mappedColumns.gst_pct]);
                rowData.gst_pct = [0, 5, 12, 18, 28].includes(gp) ? gp : 12;
            }
            if (mappedColumns.hsn_code !== undefined) rowData.hsn_code = (cells[mappedColumns.hsn_code] || '').trim();

            if (rowData.rate === 0 && rowData.mrp > 0) {
                rowData.rate = parseFloat((rowData.mrp / (1 + (rowData.gst_pct / 100))).toFixed(2));
            }

            const currentCounter = ++rowIdCounter;
            rowData._id = currentCounter;
            
            addRow(rowData);
            added++;

            if (article) {
                pendingAutoCompletes.push(handleArticleOrColorChange(currentCounter, false));
            }
        }

        if (added > 0) {
            if (pendingAutoCompletes.length > 0) {
                await Promise.all(pendingAutoCompletes);
            }
            recalculate();
            toast(`Successfully imported ${added} rows and auto-completed details from Item Master!`, 'success');
        } else {
            toast('No valid rows found', 'error');
        }
    } catch(e) {
        console.error(e);
        toast('Failed to parse Excel import: ' + e.message, 'error');
    }
}

// ── Client-Side OCR Data Extraction Logic (Tesseract.js) ───────────
let ocrExtractedRows = [];

function handleOcrFileSelect(e) {
    if (e.target.files && e.target.files[0]) {
        processOcrImage(e.target.files[0]);
    }
}

async function processOcrImage(file) {
    const wrap = document.getElementById('ocr-progress-wrap');
    const label = document.getElementById('ocr-progress-label');
    const pct = document.getElementById('ocr-progress-pct');
    const fill = document.getElementById('ocr-progress-fill');
    const review = document.getElementById('ocr-review-container');
    const applyBtn = document.getElementById('ocr-apply-btn');

    wrap.style.display = 'block';
    review.style.display = 'none';
    applyBtn.disabled = true;
    label.textContent = 'Initializing Tesseract Web Worker...';
    pct.textContent = '0%';
    fill.style.width = '0%';

    try {
        const result = await Tesseract.recognize(
            file,
            'eng',
            {
                logger: m => {
                    if (m.status === 'recognizing text') {
                        const progress = Math.round(m.progress * 100);
                        label.textContent = 'Scanning image & extracting text lines...';
                        pct.textContent = `${progress}%`;
                        fill.style.width = `${progress}%`;
                    }
                }
            }
        );

        label.textContent = 'OCR completed successfully!';
        pct.textContent = '100%';
        fill.style.width = '100%';
        
        parseOcrText(result.data.text);
    } catch (err) {
        console.error(err);
        label.textContent = 'OCR Failed: ' + err.message;
        toast('OCR processing failed', 'error');
    }
}

function parseOcrText(text) {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 2);
    ocrExtractedRows = [];

    const COLOR_KEYWORDS = ['BLACK', 'BEIGE', 'CREAM', 'WHITE', 'RED', 'BLUE', 'YELLOW', 'GREEN', 'GREY', 'GRAY', 'PINK', 'PISTA', 'TAN', 'GOLD', 'SILVER', 'BROWN'];
    const sizes = [...state.sizeColumns];

    lines.forEach(line => {
        const words = line.toUpperCase().split(/[\s|,\t]+/);
        if (words.length < 2) return;

        let article = '';
        let color = '';
        let category = '';
        let rowSizes = {};

        const artMatch = line.match(/\b(10\d{3}|20\d{3}|200\d{2}|209\d)\b/);
        if (artMatch) {
            article = artMatch[1];
        }

        if (line.includes('SANDAL')) category = 'SANDAL';
        else if (line.includes('CHAPPAL')) category = 'CHAPPAL';
        else if (line.includes('SHOE')) category = 'SHOE';

        for (let kw of COLOR_KEYWORDS) {
            if (line.includes(kw)) {
                color = kw;
                break;
            }
        }

        let numberTokens = words.map(w => parseFloat(w)).filter(n => !isNaN(n));
        numberTokens = numberTokens.filter(n => n !== parseFloat(article) && n !== 1899 && n !== 1499 && n !== 1399 && n !== 1999);

        if (numberTokens.length > 0) {
            sizes.forEach((sz, idx) => {
                rowSizes[sz] = numberTokens[idx] !== undefined ? numberTokens[idx] : 0;
            });

            const totalQty = Object.values(rowSizes).reduce((a, b) => a + b, 0);
            if (totalQty > 0 || category || article) {
                ocrExtractedRows.push({
                    article: article,
                    color: color,
                    category: category || (article ? 'SANDAL' : ''),
                    sub_category: line.includes('MUEL') ? 'MUEL' : (line.includes('BURMY') ? 'BURMY' : ''),
                    sizes: rowSizes
                });
            }
        }
    });

    renderOcrReview();
}

function renderOcrReview() {
    const tbody = document.getElementById('ocr-review-tbody');
    const container = document.getElementById('ocr-review-container');
    const applyBtn = document.getElementById('ocr-apply-btn');

    tbody.innerHTML = '';
    if (ocrExtractedRows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px;">
            ⚠️ Could not automatically detect a structured grid. Try selecting a clearer screenshot or adding rows manually.
        </td></tr>`;
        container.style.display = 'block';
        applyBtn.disabled = true;
        return;
    }

    ocrExtractedRows.forEach((row, idx) => {
        const tr = document.createElement('tr');
        const sizePreviewHtml = Object.entries(row.sizes)
            .map(([sz, qty]) => `<span style="display:inline-block;padding:2px 6px;margin:2px;background:var(--card2);border-radius:4px;font-weight:${qty>0?'bold':'normal'};color:${qty>0?'var(--primary-lt)':'var(--muted)'};">${sz}: ${qty}</span>`)
            .join(' ');

        tr.innerHTML = `
            <td><input class="cell-input" value="${row.article}" style="border:1px solid var(--border);border-radius:4px;padding:3px 6px;" oninput="ocrExtractedRows[${idx}].article=this.value"></td>
            <td><input class="cell-input" value="${row.color}" style="border:1px solid var(--border);border-radius:4px;padding:3px 6px;" oninput="ocrExtractedRows[${idx}].color=this.value"></td>
            <td><input class="cell-input" value="${row.category}" style="border:1px solid var(--border);border-radius:4px;padding:3px 6px;" oninput="ocrExtractedRows[${idx}].category=this.value"></td>
            <td style="line-height:1.6;">${sizePreviewHtml}</td>
        `;
        tbody.appendChild(tr);
    });

    container.style.display = 'block';
    applyBtn.disabled = false;
}

async function applyOcrReviewToGrid() {
    closeModal('modal-ocr-upload');
    document.getElementById('ocr-progress-wrap').style.display = 'none';
    document.getElementById('ocr-review-container').style.display = 'none';

    let pendingAutoCompletes = [];

    ocrExtractedRows.forEach(row => {
        const currentCounter = ++rowIdCounter;
        row._id = currentCounter;
        
        addRow({
            _id:          currentCounter,
            article:      row.article,
            color:        row.color,
            category:     row.category,
            sub_category: row.sub_category,
            sizes:        row.sizes
        });

        if (row.article) {
            pendingAutoCompletes.push(handleArticleOrColorChange(currentCounter, false));
        }
    });

    if (pendingAutoCompletes.length > 0) {
        await Promise.all(pendingAutoCompletes);
    }

    recalculate();
    toast(`Successfully extracted and applied ${ocrExtractedRows.length} rows to the invoice matrix!`, 'success');
}

// ── Save / Submit Invoice ────────────────────────────────────
async function saveInvoice(andSubmit = false) {
    const customer = state.customerInfo?.customer;
    const custSearch = document.getElementById('cust-search').value.trim();
    if (!customer && !custSearch) { toast('Please select a customer', 'error'); return; }
    if (!state.rows.length) { toast('Please add at least one item row', 'error'); return; }

    const hasQty = state.rows.some(r =>
        state.sizeColumns.some(sz => (parseFloat(r.sizes[sz]) || 0) > 0)
    );
    if (!hasQty) { toast('Enter quantities in at least one size column', 'error'); return; }

    const btn = document.getElementById(andSubmit ? 'btn-submit' : 'btn-save');
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined" style="animation:spin 1s linear infinite;">refresh</span> ${andSubmit ? 'Submitting…' : 'Saving…'}`;

    const payload = {
        invoice_name:    state.savedInvName || null,
        invoice_date:    document.getElementById('inv-date').value,
        customer:        customer || custSearch,
        place_of_supply: document.getElementById('place-of-supply').value,
        tax_type:        state.taxType,
        eway_bill_no:    document.getElementById('eway-bill').value,
        vehicle_no:      document.getElementById('vehicle-no').value,
        transport_mode:  document.getElementById('transport-mode').value,
        terms:           document.getElementById('terms').value,
        size_columns:    state.sizeColumns,
        rows:            state.rows,
    };

    try {
        const result = await api('smriti_retail_os.sizewise_invoice_api.save_sizewise_invoice', { payload: JSON.stringify(payload) });
        state.savedInvName = result.name;
        state.docstatus = 0;
        document.getElementById('inv-number').value = result.name;
        document.getElementById('inv-status-badge').innerHTML = `<span class="status-badge status-draft">Draft</span>`;
        history.replaceState({}, '', `?invoice=${result.name}`);
        toast(`Invoice ${result.name} saved!`, 'success');

        if (andSubmit) {
            const r2 = await api('smriti_retail_os.sizewise_invoice_api.submit_sizewise_invoice', { invoice_name: result.name });
            state.docstatus = 1;
            document.getElementById('inv-status-badge').innerHTML = `<span class="status-badge status-submit">Submitted</span>`;
            setReadOnly(true);
            toast(`Invoice ${result.name} submitted!`, 'success');
        }
    } catch(e) {
        toast('Save failed: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = andSubmit
            ? `<span class="material-symbols-outlined">check_circle</span> Save & Submit`
            : `<span class="material-symbols-outlined">save</span> Save Draft`;
    }
}

function setReadOnly(on) {
    document.querySelectorAll('.cell-input, .size-input, .form-control:not(.form-readonly)').forEach(el => {
        el.disabled = on;
    });
    document.getElementById('btn-save').disabled   = on;
    document.getElementById('btn-submit').disabled = on;
}

// ── Invoice Drawer ────────────────────────────────────────────
async function openDrawer() {
    document.getElementById('inv-drawer').classList.add('open');
    const listEl = document.getElementById('drawer-list');
    listEl.innerHTML = '<div style="color:var(--muted);text-align:center;padding:30px;">Loading…</div>';
    try {
        state.allInvoices = await api('smriti_retail_os.sizewise_invoice_api.list_sizewise_invoices');
        renderDrawerList(state.allInvoices);
    } catch(e) {
        listEl.innerHTML = '<div style="color:var(--danger);padding:20px;">Error loading invoices</div>';
    }
}

function closeDrawer() { document.getElementById('inv-drawer').classList.remove('open'); }

function renderDrawerList(invs) {
    const el = document.getElementById('drawer-list');
    if (!invs.length) { el.innerHTML = '<div style="color:var(--muted);text-align:center;padding:30px;">No sizewise invoices found.</div>'; return; }
    el.innerHTML = '';
    invs.forEach(inv => {
        const statusMap = { 0:'Draft', 1:'Submitted', 2:'Cancelled' };
        const cssMap    = { 0:'status-draft', 1:'status-submit', 2:'status-cancel' };
        const d = document.createElement('div');
        d.className = 'inv-row';
        d.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="inv-num">${inv.name}</div>
                <span class="status-badge ${cssMap[inv.docstatus]||''}">${statusMap[inv.docstatus]||'?'}</span>
            </div>
            <div class="inv-meta">${inv.customer} · ${inv.posting_date} · ₹${parseFloat(inv.grand_total||0).toLocaleString('en-IN',{minimumFractionDigits:2})}</div>`;
        d.onclick = () => { closeDrawer(); loadInvoice(inv.name); };
        el.appendChild(d);
    });
}

function filterDrawerList(q) {
    const filtered = state.allInvoices.filter(i =>
        i.name.toLowerCase().includes(q.toLowerCase()) ||
        i.customer.toLowerCase().includes(q.toLowerCase())
    );
    renderDrawerList(filtered);
}

async function loadInvoice(name) {
    toast('Loading invoice…', 'info');
    try {
        const data = await api('smriti_retail_os.sizewise_invoice_api.get_sizewise_invoice', { invoice_name: name });
        resetForm(true);
        state.savedInvName = data.invoice_name;
        state.docstatus    = data.docstatus;
        state.taxType      = data.tax_type || 'intrastate';
        state.sizeColumns  = data.size_columns || [...PRESETS.footwear];

        document.getElementById('inv-number').value = data.invoice_name;
        document.getElementById('inv-date').value   = data.invoice_date;
        document.getElementById('cust-search').value = data.customer;
        document.getElementById('eway-bill').value  = data.eway_bill_no || '';
        document.getElementById('vehicle-no').value = data.vehicle_no || '';
        document.getElementById('transport-mode').value = data.transport_mode || 'Road';
        document.getElementById('terms').value      = data.terms || '';
        document.getElementById('place-of-supply').value = data.place_of_supply || '';
        setTaxType(data.tax_type || 'intrastate');

        const statusMap = { 0:'Draft', 1:'Submitted', 2:'Cancelled' };
        const cssMap    = { 0:'status-draft', 1:'status-submit', 2:'status-cancel' };
        document.getElementById('inv-status-badge').innerHTML =
            `<span class="status-badge ${cssMap[data.docstatus]||''}">${statusMap[data.docstatus]||'?'}</span>`;

        // Fetch customer details
        try {
            const c = await api('smriti_retail_os.sizewise_invoice_api.get_customer_details', { customer: data.customer });
            state.customerInfo = c;
            document.getElementById('buyer-gstin').value  = c.gstin || '';
            document.getElementById('buyer-mobile').value = c.mobile_no || '';
            const a = c.address || {};
            document.getElementById('buyer-addr').value  = [a.line1, a.line2, a.city, a.state, a.pincode].filter(Boolean).join(', ');
        } catch(_) {}

        // Load rows into grid
        renderSizeTags();
        (data.rows || []).forEach(r => addRow(r));
        recalculate();
        if (data.docstatus !== 0) setReadOnly(true);
        toast(`Loaded invoice ${name}`, 'success');
    } catch(e) {
        toast('Could not load invoice: ' + e.message, 'error');
    }
}

function loadInvoiceFromModal() {
    const name = document.getElementById('load-inv-input').value.trim();
    if (!name) return;
    closeModal('modal-load-inv');
    loadInvoice(name);
}

// ── Reset Form ────────────────────────────────────────────────
function resetForm(silent = false) {
    if (!silent && state.rows.length > 0 && !confirm('Start a new invoice? Unsaved changes will be lost.')) return;
    state.rows       = [];
    state.taxType    = 'intrastate';
    state.customerInfo = null;
    state.savedInvName = null;
    state.docstatus  = 0;
    state.sizeColumns = [...PRESETS.footwear];
    rowIdCounter = 0;

    ['inv-number','cust-search','buyer-gstin','buyer-mobile','buyer-addr',
     'eway-bill','vehicle-no'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    document.getElementById('inv-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('place-of-supply').value = '';
    document.getElementById('transport-mode').value  = 'Road';
    document.getElementById('inv-status-badge').innerHTML = '';
    setTaxType('intrastate');
    renderSizeTags();
    updateRowCount();
    recalculate();
    setReadOnly(false);
    if (!silent) toast('New invoice started', 'info');
}

// ── Print Header Updater ──────────────────────────────────────
function updatePrintHeader(grand = 0) {
    const invNo   = document.getElementById('inv-number').value || '—';
    const invDate = document.getElementById('inv-date').value   || '—';
    const buyer   = document.getElementById('cust-search').value || '—';
    const bGSTIN  = document.getElementById('buyer-gstin').value || '—';
    const bAddr   = document.getElementById('buyer-addr').value  || '—';
    const pos     = document.getElementById('place-of-supply').value || '—';

    // Backwards compatibility if old elements are accessed
    const phNoDate = document.getElementById('ph-inv-no-date');
    if (phNoDate) phNoDate.innerHTML = `Invoice No: <strong>${invNo}</strong><br>Date: ${invDate}`;
    const phBuyer = document.getElementById('ph-buyer-info');
    if (phBuyer) phBuyer.innerHTML = `<strong>${buyer}</strong><br>GSTIN: ${bGSTIN}<br>${bAddr}`;
    const phDetails = document.getElementById('ph-inv-details');
    if (phDetails) phDetails.innerHTML = `Place of Supply: ${pos}<br>Tax Type: ${state.taxType === 'intrastate' ? 'CGST + SGST' : 'IGST'}<br>Grand Total: ₹${parseFloat(grand||0).toLocaleString('en-IN',{minimumFractionDigits:2})}`;

    // Update new dedicated print layout
    try {
        populatePrintLayout(grand);
    } catch(e) {
        console.error("Error populating print layout:", e);
    }
}

function populatePrintLayout(grand = 0) {
    const c = state.companyInfo || {};
    const cAddr = c.address || {};
    
    // 1. Company Info
    document.getElementById('p-company-name').textContent = c.company_name || 'TATTLY THREADS';
    let metaLines = [];
    if (cAddr.line1) metaLines.push(cAddr.line1);
    if (cAddr.line2) metaLines.push(cAddr.line2);
    if (cAddr.city || cAddr.state) metaLines.push([cAddr.city, cAddr.state, cAddr.pincode].filter(Boolean).join(', '));
    if (c.phone) metaLines.push('Phone: ' + c.phone);
    if (c.email) metaLines.push('Email: ' + c.email);
    if (c.gstin) metaLines.push('GSTIN: ' + c.gstin);
    if (c.pan) metaLines.push('PAN: ' + c.pan);
    if (c.state_code) metaLines.push('State: ' + c.state_code + (cAddr.state ? ' - ' + cAddr.state : ''));
    document.getElementById('p-company-meta').innerHTML = metaLines.join('<br>');
    
    // Logo
    const logoImg = document.getElementById('p-logo-img');
    if (c.company_logo) {
        logoImg.src = c.company_logo;
        logoImg.style.display = 'block';
    } else {
        logoImg.style.display = 'none';
    }
    
    // 2. Bill To & Ship To
    const buyer = document.getElementById('cust-search').value || '—';
    const bGSTIN = document.getElementById('buyer-gstin').value || '—';
    const bAddr = document.getElementById('buyer-addr').value || '—';
    const pos = document.getElementById('place-of-supply').value || '—';
    
    let stateName = '—';
    if (pos && pos !== '—') {
        const parts = pos.split('-');
        stateName = (parts.length > 1 ? parts[1] : parts[0]).toUpperCase();
    }
    
    const cPAN = (bGSTIN && bGSTIN.length === 15) ? bGSTIN.substring(2, 12) : '—';
    document.getElementById('p-bill-to').innerHTML = `<strong>${buyer}</strong><br>GSTIN: ${bGSTIN}<br>PAN: ${cPAN}<br>${bAddr}<br>State: ${stateName}`;
    
    const shipTo = document.getElementById('ship-to').value || '';
    if (shipTo) {
        document.getElementById('p-ship-to').innerHTML = `<strong>${buyer}</strong><br>PAN: ${cPAN}<br>${shipTo}<br>State: ${stateName}`;
    } else {
        document.getElementById('p-ship-to').innerHTML = `<strong>${buyer}</strong><br>PAN: ${cPAN}<br>${bAddr}<br>State: ${stateName}`;
    }
    
    // 3. Invoice Details
    const invNo = document.getElementById('inv-number').value || '—';
    const invDate = document.getElementById('inv-date').value || '—';
    const transMode = document.getElementById('transport-mode').value || '—';
    const eway = document.getElementById('eway-bill').value || '';
    const vehicle = document.getElementById('vehicle-no').value || '';
    
    let formattedDate = '—';
    if (invDate && invDate !== '—') {
        const parts = invDate.split('-');
        if (parts.length === 3) {
            formattedDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
        } else {
            formattedDate = invDate;
        }
    }
    
    document.getElementById('p-inv-no').textContent = invNo;
    document.getElementById('p-inv-date').textContent = formattedDate;
    document.getElementById('p-place-supply').textContent = pos.toUpperCase();
    document.getElementById('p-trans-mode').textContent = transMode;
    document.getElementById('p-eway-bill').textContent = eway || '—';
    document.getElementById('p-vehicle-no').textContent = vehicle || '—';
    
    // 4. Summary & Words
    document.getElementById('p-words').textContent = numberToWords(grand);
    document.getElementById('p-terms').innerHTML = (document.getElementById('terms').value || '—').replace(/\n/g, '<br>');
    
    // Bank Pay To & QR Code
    const bankName = document.getElementById('bank-name').value || '';
    const bankAc = document.getElementById('bank-acno').value || '';
    const bankIFSC = document.getElementById('bank-ifsc').value || '';
    const bankBranch = document.getElementById('bank-branch').value || '';
    
    if (bankName || bankAc) {
        const branchStr = bankBranch ? bankBranch.toUpperCase() : 'WARDHMAN NAGAR NAGPUR';
        document.getElementById('p-bank-name-branch').innerHTML = `Bank Name: ${bankName.toUpperCase()},<br>${branchStr}`;
        
        document.getElementById('p-bank-details-block').innerHTML = `
            <br>
            Bank Account No.: ${bankAc}<br>
            Bank IFSC code: ${bankIFSC}<br>
            Account Holder's Name: ${(c.company_name || 'TATTLY THREADS').toUpperCase()}
        `;
        
        if (document.getElementById('p-payto')) {
            document.getElementById('p-payto').innerHTML = `Bank Name: <strong>${bankName}</strong><br>Account No.: <strong>${bankAc}</strong><br>IFSC: <strong>${bankIFSC}</strong>`;
        }
        
        // UPI QR Code
        const upiId = c.phone ? `${c.phone}@upi` : "9604990390@upi";
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(`upi://pay?pa=${upiId}&pn=${c.company_name || 'TATTLY THREADS'}&am=${grand}&cu=INR`)}`;
        document.getElementById('p-qr-img').src = qrUrl;
        document.getElementById('p-qr-container').style.display = 'block';
    } else {
        document.getElementById('p-bank-name-branch').textContent = 'Bank details not configured';
        document.getElementById('p-bank-details-block').textContent = '';
        document.getElementById('p-qr-container').style.display = 'none';
    }
    
    // 5. Totals
    let totalTaxable = 0, totalTax = 0, totalQty = 0;
    state.rows.forEach(row => {
        const qty = state.sizeColumns.reduce((s, sz) => s + (parseFloat(row.sizes[sz]) || 0), 0);
        const rate = parseFloat(row.rate) || 0;
        const disc = parseFloat(row.discount_percentage) || 0;
        const gstPct = parseFloat(row.gst_pct) || 0;
        totalQty += qty;
        
        const lineTaxable = qty * rate * (1 - disc / 100);
        totalTaxable += lineTaxable;
        totalTax += lineTaxable * gstPct / 100;
    });
    const roundoff = grand - (totalTaxable + totalTax);
    
    document.getElementById('p-subtotal').textContent = fmtINR(totalTaxable);
    document.getElementById('p-roundoff').textContent = fmtINR(roundoff);
    document.getElementById('p-grand-total').textContent = fmtINR(grand);
    document.getElementById('p-balance').textContent = fmtINR(grand);
    
    if (state.taxType === 'intrastate') {
        const half = totalTax / 2;
        document.getElementById('p-cgst').textContent = fmtINR(half);
        document.getElementById('p-sgst').textContent = fmtINR(half);
        document.getElementById('p-cgst-row').style.display = '';
        document.getElementById('p-sgst-row').style.display = '';
        document.getElementById('p-igst-row').style.display = 'none';
    } else {
        document.getElementById('p-igst').textContent = fmtINR(totalTax);
        document.getElementById('p-cgst-row').style.display = 'none';
        document.getElementById('p-sgst-row').style.display = 'none';
        document.getElementById('p-igst-row').style.display = '';
    }
    
    // 6. Item Table Population
    const pTable = document.getElementById('p-item-table');
    const sizes = state.sizeColumns;
    
    // Header
    let headHtml = `<tr>
        <th>#</th>
        <th class="text-left">Item Name</th>
        <th>HSN</th>
        <th>MRP</th>
        ${sizes.map(s => `<th>${s}</th>`).join('')}
        <th>Qty</th>
        <th>Price/Unit</th>
        <th>Disc</th>
        <th>GST</th>
        <th>Amount</th>
    </tr>`;
    
    // Body
    let bodyHtml = '';
    let validRowIndex = 1;
    state.rows.forEach(row => {
        const qty = sizes.reduce((s, sz) => s + (parseFloat(row.sizes[sz]) || 0), 0);
        if (qty <= 0) return;
        
        const rate = parseFloat(row.rate) || 0;
        const mrp = parseFloat(row.mrp) || 0;
        const disc = parseFloat(row.discount_percentage) || 0;
        const gstPct = parseFloat(row.gst_pct) || 0;
        const hsn = row.hsn_code || '';
        const hsn4 = hsn.substring(0, 4);
        const amt = qty * rate * (1 - disc / 100);
        
        bodyHtml += `<tr>
            <td>${validRowIndex++}</td>
            <td class="text-left"><strong>${row.article} - ${(row.color || '').toUpperCase()}</strong></td>
            <td>${hsn4}</td>
            <td>${mrp.toFixed(2)}</td>
            ${sizes.map(s => `<td>${parseInt(row.sizes[s]) || ''}</td>`).join('')}
            <td class="bold">${qty} Prs</td>
            <td>${rate.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
            <td>${disc > 0 ? disc.toFixed(2) + '%' : '—'}</td>
            <td>${gstPct}%</td>
            <td class="bold">${amt.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
        </tr>`;
    });
    
    // Footer totals row
    let footHtml = `<tr>
        <td colspan="4" class="bold text-right" style="text-transform:uppercase;">Total</td>
        ${sizes.map(s => {
            const szQty = state.rows.reduce((sum, r) => sum + (parseInt(r.sizes[s]) || 0), 0);
            return `<td class="bold">${szQty || ''}</td>`;
        }).join('')}
        <td class="bold">${totalQty} Prs</td>
        <td></td>
        <td></td>
        <td class="bold">₹${totalTax.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
        <td class="bold">₹${totalTaxable.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
    </tr>`;
    
    pTable.querySelector('thead').innerHTML = headHtml;
    pTable.querySelector('tbody').innerHTML = bodyHtml;
    
    let tfoot = pTable.querySelector('tfoot');
    if (!tfoot) {
        tfoot = document.createElement('tfoot');
        pTable.appendChild(tfoot);
    }
    tfoot.innerHTML = footHtml;

    // 7. HSN Summary Table Population
    const hsnMap = {};
    state.rows.forEach(row => {
        const qty = sizes.reduce((s, sz) => s + (parseFloat(row.sizes[sz]) || 0), 0);
        if (qty <= 0) return;
        const rate = parseFloat(row.rate) || 0;
        const disc = parseFloat(row.discount_percentage) || 0;
        const gstPct = parseFloat(row.gst_pct) || 0;
        const hsn = (row.hsn_code || 'N/A').substring(0, 4);
        const lineTaxable = qty * rate * (1 - disc / 100);
        const lineTax = lineTaxable * gstPct / 100;
        
        const key = `${hsn}|${gstPct}`;
        if (!hsnMap[key]) hsnMap[key] = { hsn, gstPct, taxable: 0, tax: 0 };
        hsnMap[key].taxable += lineTaxable;
        hsnMap[key].tax += lineTax;
    });

    const isIntra = state.taxType === 'intrastate';
    
    // Toggle table headers
    document.getElementById('p-hsn-cgst-hdr').style.display = isIntra ? '' : 'none';
    document.getElementById('p-hsn-cgst-amt-hdr').style.display = isIntra ? '' : 'none';
    document.getElementById('p-hsn-sgst-hdr').style.display = isIntra ? '' : 'none';
    document.getElementById('p-hsn-sgst-amt-hdr').style.display = isIntra ? '' : 'none';
    document.getElementById('p-hsn-igst-hdr').style.display = isIntra ? 'none' : '';
    document.getElementById('p-hsn-igst-amt-hdr').style.display = isIntra ? 'none' : '';
    
    let hsnBody = '';
    let hsnTotalTaxable = 0, hsnTotalTax = 0;
    
    Object.values(hsnMap).forEach(m => {
        hsnTotalTaxable += m.taxable;
        hsnTotalTax += m.tax;
        
        hsnBody += `<tr>
            <td class="bold">${m.hsn}</td>
            <td class="text-right">₹${m.taxable.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
            ${isIntra ? `
                <td>${(m.gstPct/2).toFixed(1)}%</td>
                <td class="text-right">₹${(m.tax/2).toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
                <td>${(m.gstPct/2).toFixed(1)}%</td>
                <td class="text-right">₹${(m.tax/2).toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
            ` : `
                <td>${m.gstPct.toFixed(1)}%</td>
                <td class="text-right">₹${m.tax.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
            `}
            <td class="bold text-right">₹${m.tax.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
        </tr>`;
    });
    
    let hsnFoot = `<tr>
        <td class="bold">Total</td>
        <td class="bold text-right">₹${hsnTotalTaxable.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
        ${isIntra ? `
            <td></td>
            <td class="bold text-right">₹${(hsnTotalTax/2).toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
            <td></td>
            <td class="bold text-right">₹${(hsnTotalTax/2).toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
        ` : `
            <td></td>
            <td class="bold text-right">₹${hsnTotalTax.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
        `}
        <td class="bold text-right">₹${hsnTotalTax.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
    </tr>`;
    
    document.getElementById('p-hsn-table').querySelector('tbody').innerHTML = hsnBody;
    
    let hsnTfoot = document.getElementById('p-hsn-table').querySelector('tfoot');
    if (!hsnTfoot) {
        hsnTfoot = document.createElement('tfoot');
        document.getElementById('p-hsn-table').appendChild(hsnTfoot);
    }
    hsnTfoot.innerHTML = hsnFoot;
}


async function loadDynamicSizeGroups() {
    try {
        const res = await fetch('/api/method/smriti_retail_os.master_api.get_size_groups', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': CSRF }
        });
        const data = await res.json();
        const groups = data.message || [];
        if (groups.length > 0) {
            // Overwrite/extend PRESETS
            groups.forEach(g => {
                PRESETS[g.id] = g.sizes;
            });
            // Update container buttons
            const container = document.getElementById('preset-buttons-container');
            if (container) {
                let btnHtml = '';
                groups.forEach(g => {
                    let emoji = '📏';
                    const lid = g.id.toLowerCase();
                    if (lid.includes('foot') || lid.includes('shoe')) emoji = '👟';
                    else if (lid.includes('garment') || lid.includes('wear') || lid.includes('shirt') || lid.includes('pant')) emoji = '👕';
                    else if (lid.includes('kid')) emoji = '🧒';
                    btnHtml += `<button class="btn btn-ghost" style="padding:5px 12px;font-size:0.8rem;" onclick="loadPreset('${g.id}')">${emoji} ${g.label}</button> `;
                });
                btnHtml += `<button class="btn btn-ghost" style="padding:5px 12px;font-size:0.8rem;" onclick="openAddSizeModal()">
                                <span class="material-symbols-outlined" style="font-size:15px;">add</span> Add Size
                            </button>`;
                container.innerHTML = btnHtml;
            }
            // Set initial to first preset if we are creating a new invoice (not loading saved one)
            const urlParams = new URLSearchParams(window.location.search);
            if (!urlParams.get('invoice')) {
                state.sizeColumns = [...groups[0].sizes];
            }
        }
    } catch(e) {
        console.error("Failed to load dynamic size groups:", e);
    }
}

// ── Init ──────────────────────────────────────────────────────
async function init() {
    document.getElementById('inv-date').value = new Date().toISOString().split('T')[0];
    await Promise.all([loadCompanyDetails(), loadStates(), loadDynamicSizeGroups()]);
    renderSizeTags();
    recalculate();

    // Check URL for invoice name
    const urlParams = new URLSearchParams(window.location.search);
    const invName   = urlParams.get('invoice');
    if (invName) { await loadInvoice(invName); }
    else { addRow(); addRow(); addRow(); } // Start with 3 empty rows

    // Add CSS spin keyframe
    const st = document.createElement('style');
    st.textContent = '@keyframes spin { from{transform:rotate(0)} to{transform:rotate(360deg)} }';
    document.head.appendChild(st);
}

function exportInvoiceToPDF() {
    const element = document.getElementById('print-layout');
    if (!element) {
        toast('Print layout not found', 'error');
        return;
    }
    
    // Temporarily make print layout visible for the PDF generator
    const originalDisplay = element.style.display;
    element.style.display = 'block';
    element.style.width = '210mm'; // Standard A4 width
    element.style.padding = '10mm';
    element.style.background = '#ffffff';
    
    // Force native system fonts for rendering
    element.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
    
    const invNo = document.getElementById('inv-number').value || 'Invoice';
    
    const opt = {
        margin:       0,
        filename:     `${invNo}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { 
            scale: 2, 
            useCORS: true,
            logging: false,
            letterRendering: true
        },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    toast('Generating PDF…', 'info');
    
    html2pdf().set(opt).from(element).save().then(() => {
        // Restore original state
        element.style.display = originalDisplay;
        element.style.width = '';
        element.style.padding = '';
        element.style.background = '';
        element.style.fontFamily = '';
        toast('PDF exported successfully!', 'success');
    }).catch(err => {
        console.error("PDF generation error:", err);
        element.style.display = originalDisplay;
        element.style.width = '';
        element.style.padding = '';
        element.style.background = '';
        element.style.fontFamily = '';
        toast('Failed to export PDF: ' + err.message, 'error');
    });
}

window.onload = init;