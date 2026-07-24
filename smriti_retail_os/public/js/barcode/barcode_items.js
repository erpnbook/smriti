/**
 * @file: smriti_retail_os/public/js/barcode/barcode_items.js
 * @description: Data loading layer for items lookup, autocomplete searches, and transaction checklists.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

// --- Live Autocomplete Audit Implementation ---
let currentFocus = -1;

function initAutocompleteSearch() {
    const styleInput = document.getElementById('flt-search');
    const autoList = document.getElementById('autocomplete-list');
    if (!styleInput || !autoList) return;

    // input handler with 300ms debounce
    styleInput.addEventListener('input', debounce(async (e) => {
        const txt = e.target.value.trim();
        if (!txt) {
            closeAutocomplete();
            return;
        }

        try {
            const results = await api('smriti_retail_os.barcode_api.search_barcode_items', { txt });
            showAutocomplete(results);
        } catch (err) {
            console.error('Autocomplete failed:', err);
        }
    }, 300));

    // Keyboard navigation
    styleInput.addEventListener('keydown', function(e) {
        let items = autoList.getElementsByClassName('autocomplete-item');
        if (!items || !items.length) return;

        if (e.keyCode === 40) { // Arrow Down
            currentFocus++;
            addActive(items);
            e.preventDefault();
        } else if (e.keyCode === 38) { // Arrow Up
            currentFocus--;
            addActive(items);
            e.preventDefault();
        } else if (e.keyCode === 13) { // Enter
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                items[currentFocus].click();
            } else if (items[0]) {
                items[0].click();
            }
        } else if (e.keyCode === 27) { // Escape
            closeAutocomplete();
        }
    });

    function addActive(items) {
        if (!items) return false;
        removeActive(items);
        if (currentFocus >= items.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = items.length - 1;
        items[currentFocus].classList.add('autocomplete-item-active');
        items[currentFocus].scrollIntoView({ block: 'nearest' });
    }

    function removeActive(items) {
        for (let i = 0; i < items.length; i++) {
            items[i].classList.remove('autocomplete-item-active');
        }
    }

    function showAutocomplete(results) {
        autoList.innerHTML = '';
        currentFocus = -1;

        if (!results || !results.length) {
            autoList.style.display = 'none';
            return;
        }

        results.forEach((item) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';

            const mainRow = document.createElement('div');
            mainRow.className = 'autocomplete-row-main';
            const styleSpan = document.createElement('span');
            styleSpan.textContent = item.style || 'N/A';
            const barcodeSpan = document.createElement('span');
            barcodeSpan.className = 'autocomplete-row-barcode';
            barcodeSpan.textContent = item.barcode || 'No Barcode';
            mainRow.appendChild(styleSpan);
            mainRow.appendChild(barcodeSpan);
            
            const subRow = document.createElement('div');
            subRow.className = 'autocomplete-row-sub';
            subRow.textContent = item.item_name || 'N/A';
            div.appendChild(mainRow);
            div.appendChild(subRow);

            div.addEventListener('click', async () => {
                styleInput.value = item.item_code;
                closeAutocomplete();
                
                try {
                    const loadedItems = await api('smriti_retail_os.barcode_api.get_items_for_printing', {
                        filters: JSON.stringify({ search_text: item.item_code })
                    });
                    if (loadedItems && loadedItems.length) {
                        addItemsToQueue(loadedItems);
                        toast(`Loaded item: ${item.item_code}`, 'success');
                    } else {
                        toast(`Failed to load details for: ${item.item_code}`, 'info');
                    }
                } catch (err) {
                    toast('Failed to load selected item: ' + err.message, 'error');
                }
            });

            autoList.appendChild(div);
        });

        autoList.style.display = 'block';
    }

    function closeAutocomplete() {
        autoList.innerHTML = '';
        autoList.style.display = 'none';
        currentFocus = -1;
    }

    document.addEventListener('click', (e) => {
        if (e.target !== styleInput && e.target !== autoList && !autoList.contains(e.target)) {
            closeAutocomplete();
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAutocompleteSearch);
} else {
    initAutocompleteSearch();
}

// Toggle advanced filters drawer
function toggleAdvancedFilters() {
    const drawer = document.getElementById('advanced-filters-drawer');
    const caret = document.getElementById('adv-filter-caret');
    if (drawer && caret) {
        if (drawer.classList.contains('open')) {
            drawer.classList.remove('open');
            caret.textContent = '▼';
        } else {
            drawer.classList.add('open');
            caret.textContent = '▲';
        }
    }
}

// Load manual search filters
async function loadManualItems() {
    const brand = document.getElementById('flt-brand').value;
    const category = document.getElementById('flt-category').value;
    const size = document.getElementById('flt-size').value;
    const search_text = document.getElementById('flt-search').value.trim();
    const dept = document.getElementById('flt-department').value;
    const gender = document.getElementById('flt-gender').value;
    const season = document.getElementById('flt-season').value;
    const collection = document.getElementById('flt-collection').value;
    const supplier = document.getElementById('flt-supplier').value;
    const purchase_class = document.getElementById('flt-purchase-class') ? document.getElementById('flt-purchase-class').value : '';
    const merchandise_cat = document.getElementById('flt-merchandise-cat') ? document.getElementById('flt-merchandise-cat').value : '';
    const sub_cat = document.getElementById('flt-sub-cat') ? document.getElementById('flt-sub-cat').value : '';
    const upper_mat = document.getElementById('flt-upper-material') ? document.getElementById('flt-upper-material').value : '';
    const outsole = document.getElementById('flt-outsole') ? document.getElementById('flt-outsole').value : '';
    const heel_type = document.getElementById('flt-heel-type') ? document.getElementById('flt-heel-type').value : '';

    if (!brand && !category && !size && !search_text && !dept && !gender && !season && !collection && !supplier && !purchase_class && !merchandise_cat && !sub_cat && !upper_mat && !outsole && !heel_type) {
        toast('Please specify at least one search filter or search keyword', 'info');
        return;
    }

    try {
        const filters = {
            brand: brand || null,
            item_group: category || null,
            custom_barcode_size: size || null,
            search_text: search_text || null,
            department: dept || null,
            gender: gender || null,
            season: season || null,
            collection: collection || null,
            supplier: supplier || null,
            purchase_class: purchase_class || null,
            merchandise_category: merchandise_cat || null,
            sub_category: sub_cat || null,
            upper_material: upper_mat || null,
            outsole: outsole || null,
            heel_type: heel_type || null
        };
        const items = await api('smriti_retail_os.barcode_api.get_items_for_printing', {
            filters: JSON.stringify(filters)
        });

        if (!items || !items.length) {
            toast('No items found matching the search criteria', 'info');
            return;
        }

        addItemsToQueue(items);
        toast(`Added ${items.length} items to print queue`, 'success');
    } catch(e) {
        toast('Search failed: ' + e.message, 'error');
    }
}

// Article Range Loader
async function loadRangeItems() {
    const from_article = document.getElementById('flt-from-article').value.trim();
    const to_article = document.getElementById('flt-to-article').value.trim();

    if (!from_article || !to_article) {
        toast('Please specify both From and To Article Numbers', 'info');
        return;
    }

    try {
        const items = await api('smriti_retail_os.barcode_api.get_items_by_range', {
            from_article,
            to_article
        });

        if (!items || !items.length) {
            toast('No items found in this article range', 'info');
            return;
        }

        addItemsToQueue(items);
        toast(`Loaded ${items.length} items from range ${from_article} to ${to_article}`, 'success');
    } catch(e) {
        toast('Range load failed: ' + e.message, 'error');
    }
}

// Barcode Number Range Loader
async function loadBarcodeRangeItems() {
    const from_barcode = document.getElementById('flt-from-barcode').value.trim();
    const to_barcode = document.getElementById('flt-to-barcode').value.trim();

    if (!from_barcode || !to_barcode) {
        toast('Please specify both From and To Barcode Numbers', 'info');
        return;
    }

    try {
        const items = await api('smriti_retail_os.barcode_api.get_items_by_barcode_range', {
            from_barcode,
            to_barcode
        });

        if (!items || !items.length) {
            toast('No items found in this barcode range', 'info');
            return;
        }

        addItemsToQueue(items);
        toast(`Loaded ${items.length} items from barcode range ${from_barcode} to ${to_barcode}`, 'success');
    } catch(e) {
        toast('Barcode range load failed: ' + e.message, 'error');
    }
}

// Load from transaction with checklist modal
async function loadTransactionItems() {
    const doctype = document.getElementById('tx-doctype').value;
    const name = document.getElementById('tx-name').value.trim();

    if (!name) {
        toast('Please enter a Transaction ID', 'info');
        return;
    }

    try {
        const checklist = await api('smriti_retail_os.barcode_api.get_transaction_items_checklist', {
            source_doctype: doctype,
            source_name: name
        });

        if (!checklist || !checklist.length) {
            toast('No items found in this transaction', 'info');
            return;
        }

        window.BarcodeStudioState.activeTxItems = checklist;
        populateTxChecklistUI();
        openModal('tx-items-modal');
    } catch(e) {
        toast('Failed to fetch transaction checklist: ' + e.message, 'error');
    }
}

function populateTxChecklistUI() {
    const tbody = document.getElementById('tx-items-tbody');
    if (!tbody) return;

    const activeTxItems = window.BarcodeStudioState.activeTxItems;
    tbody.innerHTML = activeTxItems.map((item, index) => {
        const barcodeBadge = item.has_barcode 
            ? `<span class="badge" style="background:#065f46; color:var(--smriti-color-status-success); font-weight:700; padding:2px 6px; border-radius:4px; font-size:10px;">Active Barcode</span>`
            : `<span class="badge" style="background:#7f1d1d; color:#f87171; font-weight:700; padding:2px 6px; border-radius:4px; font-size:10px;">Missing Barcode</span>`;
            
        const ageBadge = item.is_new
            ? `<span class="badge" style="background:#1e1b4b; color:var(--smriti-color-brand-light); font-weight:700; padding:2px 6px; border-radius:4px; font-size:10px;">New SKU</span>`
            : `<span class="badge" style="background:rgba(255,255,255,0.05); color:var(--text-muted); padding:2px 6px; border-radius:4px; font-size:10px;">Existing SKU</span>`;

        return `
            <tr>
                <td style="text-align:center;">
                    <input type="checkbox" class="tx-item-chk" data-idx="${index}" checked>
                </td>
                <td>
                    <div style="font-weight:600;">${esc(item.item_name)}</div>
                    <div style="margin-top:2px; font-family:monospace; font-size:0.75rem; color:var(--text-muted);">${esc(item.item_code)}</div>
                </td>
                <td>${parseInt(item.qty)}</td>
                <td style="text-align:center;">${barcodeBadge}</td>
                <td style="text-align:center;">${ageBadge}</td>
            </tr>
        `;
    }).join('');
    
    const chkAll = document.getElementById('chk-tx-all');
    if (chkAll) chkAll.checked = true;
}

function toggleTxAllCheck(checked) {
    const checkboxes = document.querySelectorAll('.tx-item-chk');
    checkboxes.forEach(cb => cb.checked = checked);
}

function toggleTxChecklist(mode) {
    const checkboxes = document.querySelectorAll('.tx-item-chk');
    const activeTxItems = window.BarcodeStudioState.activeTxItems;
    checkboxes.forEach(cb => {
        const idx = parseInt(cb.getAttribute('data-idx'));
        const item = activeTxItems[idx];
        if (mode === 'all') {
            cb.checked = true;
        } else if (mode === 'missing') {
            cb.checked = !item.has_barcode;
        } else if (mode === 'new') {
            cb.checked = item.is_new;
        }
    });
    
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    const chkAll = document.getElementById('chk-tx-all');
    if (chkAll) chkAll.checked = allChecked;
}

async function submitTxChecklist() {
    const checkboxes = document.querySelectorAll('.tx-item-chk');
    const checkedIdxs = Array.from(checkboxes).filter(cb => cb.checked).map(cb => parseInt(cb.getAttribute('data-idx')));
    const activeTxItems = window.BarcodeStudioState.activeTxItems;
    
    if (!checkedIdxs.length) {
        toast('Please select at least one item to load', 'info');
        return;
    }
    
    closeModal('tx-items-modal');
    
    const doctype = document.getElementById('tx-doctype').value;
    const name = document.getElementById('tx-name').value.trim();
    
    try {
        toast('Loading selected items details...', 'info');
        
        const promises = checkedIdxs.map(idx => {
            const item = activeTxItems[idx];
            return api('smriti_retail_os.barcode_api.expand_item_variants', {
                item_code: item.item_code,
                default_print_qty: item.qty
            });
        });
        
        const results = await Promise.all(promises);
        const allItems = results.flat();
        
        addItemsToQueue(allItems);
        toast(`Successfully loaded ${allItems.length} variant items from ${doctype} ${name}`, 'success');
    } catch(e) {
        toast('Failed to load transaction items details: ' + e.message, 'error');
    }
}

function openCSVImportModal() {
    openModal('csv-import-modal');
}

function toggleCSVSourceType(type) {
    const fileZone = document.getElementById('csv-file-zone');
    const textZone = document.getElementById('csv-text-zone');
    if (type === 'file') {
        if (fileZone) fileZone.style.display = 'block';
        if (textZone) textZone.style.display = 'none';
    } else {
        if (fileZone) fileZone.style.display = 'none';
        if (textZone) textZone.style.display = 'block';
    }
}

async function processCSVImport() {
    const sourceType = document.querySelector('input[name="csv-source-type"]:checked')?.value || 'file';
    const delimiter = document.getElementById('csv-delimiter')?.value || 'auto';
    const barcodeCol = parseInt(document.getElementById('csv-barcode-col')?.value || '0');
    const qtyCol = parseInt(document.getElementById('csv-qty-col')?.value || '1');

    let csvContent = "";

    if (sourceType === 'file') {
        const fileInput = document.getElementById('csv-file-input');
        if (!fileInput || !fileInput.files || !fileInput.files.length) {
            toast('Please select a CSV or TXT file to upload', 'info');
            return;
        }
        const file = fileInput.files[0];
        csvContent = await file.text();
    } else {
        const rawText = document.getElementById('csv-raw-text');
        csvContent = rawText ? rawText.value.trim() : "";
    }

    if (!csvContent) {
        toast('No content found to import. Please select a file or paste text.', 'info');
        return;
    }

    try {
        toast('Processing CSV / Text data and matching barcodes...', 'info');
        const items = await api('smriti_retail_os.barcode_api.load_items_from_csv_or_text', {
            csv_text: csvContent,
            delimiter: delimiter,
            barcode_col: barcodeCol,
            qty_col: qtyCol
        });

        if (!items || !items.length) {
            toast('No valid barcode items were recognized in the provided input.', 'warning');
            return;
        }

        addItemsToQueue(items);
        closeModal('csv-import-modal');
        toast(`Successfully imported ${items.length} item records into print worksheet!`, 'success');
    } catch (e) {
        console.error("CSV import failed:", e);
        toast('Failed to process CSV import: ' + e.message, 'error');
    }
}
