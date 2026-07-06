/**
 * @file: smriti_retail_os/public/js/barcode/barcode_queue.js
 * @description: Worksheet table queue management and bulk actions.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

function addItemsToQueue(items) {
    const printQueue = window.BarcodeStudioState.printQueue;
    items.forEach(it => {
        const existing = printQueue.find(q => q.item_code === it.item_code);
        if (existing) {
            existing.qty = (existing.qty || 1) + (it.qty || 1);
        } else {
            printQueue.push({
                ...it,
                qty: it.qty || 1,
                selected: true
            });
        }
    });
    
    // Recalculate print quantities under active rule
    updateQtyRule(window.BarcodeStudioState.activeQtyRule);
}

function updateQtyRule(rule) {
    window.BarcodeStudioState.activeQtyRule = rule;
    const printQueue = window.BarcodeStudioState.printQueue;
    printQueue.forEach(item => {
        if (rule === 'carton') {
            if (item.pack_size && item.pack_size > 0) {
                item.print_qty = Math.ceil((item.qty || 1) / item.pack_size);
                item.show_pack_warning = false;
            } else {
                item.print_qty = 1;
                item.show_pack_warning = true;
            }
        } else {
            item.print_qty = item.qty || 1;
            item.show_pack_warning = false;
        }
    });
    renderQueue();
}

function renderQueue() {
    const printQueue = window.BarcodeStudioState.printQueue;
    const placeholder = document.getElementById('table-placeholder');
    const wrap = document.getElementById('table-wrap');
    const actions = document.getElementById('action-buttons');
    const stickyToolbar = document.getElementById('sticky-worksheet-toolbar');
    const bulkToolbar = document.getElementById('bulk-toolbar');
    const tbody = document.getElementById('barcode-tbody');

    const hasItems = printQueue.length > 0;

    if (hasItems) {
        if (placeholder) placeholder.style.display = 'none';
        if (wrap) wrap.style.display = 'flex';
    } else {
        if (placeholder) placeholder.style.display = 'flex';
        if (wrap) wrap.style.display = 'none';
    }

    if (actions) {
        actions.style.display = 'flex';
        const clearAllBtn = document.getElementById('btn-header-clear-all');
        const downloadPrnBtn = document.getElementById('btn-header-download-prn');
        if (clearAllBtn) clearAllBtn.style.display = hasItems ? 'inline-flex' : 'none';
        if (downloadPrnBtn) downloadPrnBtn.style.display = hasItems ? 'inline-flex' : 'none';
    }

    if (stickyToolbar) {
        stickyToolbar.style.display = 'flex';
        const selectAllBtn = document.getElementById('btn-toolbar-select-all');
        const loadVariantsBtn = document.getElementById('btn-toolbar-load-variants');
        const setLabelsBtn = document.getElementById('btn-toolbar-set-labels');
        const previewBtn = document.getElementById('btn-toolbar-preview');
        const printBtn = document.getElementById('btn-toolbar-print');
        const qtyRuleSelect = document.getElementById('cfg-qty-rule');

        if (selectAllBtn) selectAllBtn.disabled = !hasItems;
        if (loadVariantsBtn) loadVariantsBtn.disabled = !hasItems;
        if (setLabelsBtn) setLabelsBtn.disabled = !hasItems;
        if (previewBtn) previewBtn.disabled = !hasItems;
        if (printBtn) printBtn.disabled = !hasItems;
        if (qtyRuleSelect) qtyRuleSelect.disabled = !hasItems;
    }

    if (!hasItems) {
        if (bulkToolbar) bulkToolbar.style.display = 'none';
        BarcodeEvents.emit(BarcodeEvents.QUEUE_UPDATED);
        return;
    }
    
    // Update bulk toolbar visibility
    const checkedCount = printQueue.filter(q => q.selected).length;
    if (bulkToolbar) {
        if (checkedCount > 0) {
            bulkToolbar.style.display = 'flex';
            const countEl = document.getElementById('bulk-selected-count');
            if (countEl) countEl.textContent = `${checkedCount} item(s) selected`;
        } else {
            bulkToolbar.style.display = 'none';
        }
    }

    if (tbody) {
        tbody.innerHTML = printQueue.map((item, index) => {
            const isChecked = item.selected ? 'checked' : '';
            const rowClass = item.selected ? 'selected' : '';

            return `
                <tr class="${rowClass}" onclick="selectRowIndex(${index}, event)">
                    <td style="text-align:center;" onclick="event.stopPropagation()">
                        <input type="checkbox" class="grid-select-chk" ${isChecked} onchange="toggleSelectRow(${index}, this.checked, event)">
                    </td>
                    <td style="font-family:monospace; font-weight:600; color:var(--text);">${esc(item.item_code)}</td>
                    <td style="font-weight:500;">${esc(item.item_name)}</td>
                    <td>${esc(item.color || 'N/A')}</td>
                    <td><span class="item-code-badge" style="background:rgba(99,102,241,0.1); color:var(--primary-lt); font-weight:600;">${esc(item.size || 'N/A')}</span></td>
                    <td style="font-family:monospace; color:var(--primary-lt); font-weight:600;">${esc(item.barcode)}</td>
                    <td style="font-weight:700; color:var(--success);">Rs. ${parseInt(item.mrp)}</td>
                    <td style="text-align:center;">${item.qty !== undefined ? parseInt(item.qty) : 1}</td>
                    <td style="text-align:center;" onclick="event.stopPropagation()">
                        <div style="display:flex; align-items:center; justify-content:center; gap:4px;">
                            <input type="number" class="tbl-input qty-input" value="${item.print_qty}" min="1" onchange="updateQty(${index}, this.value)" style="width:70px; text-align:center;">
                            ${item.show_pack_warning ? `<span class="material-symbols-outlined" style="color:var(--warning); font-size:16px; cursor:help;" title="Pack Size Missing: Using 1 Label">warning</span>` : ''}
                        </div>
                    </td>
                    <td style="text-align:right;" onclick="event.stopPropagation()">
                        <button class="btn-del-row" onclick="removeRow(${index})" title="Delete row">
                            <span class="material-symbols-outlined" style="font-size:16px;">delete</span>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    BarcodeEvents.emit(BarcodeEvents.QUEUE_UPDATED);
}

function selectRowIndex(idx, event) {
    const printQueue = window.BarcodeStudioState.printQueue;
    BarcodeEvents.emit(BarcodeEvents.PREVIEW_REFRESH, printQueue[idx]);
}

function toggleSelectRow(idx, checked, event) {
    window.BarcodeStudioState.printQueue[idx].selected = checked;
    renderQueue();
}

function toggleSelectAll(checked) {
    window.BarcodeStudioState.printQueue.forEach(q => q.selected = checked);
    renderQueue();
}

function updateQty(idx, val) {
    const printQueue = window.BarcodeStudioState.printQueue;
    const qty = parseInt(val) || 1;
    printQueue[idx].print_qty = qty;
    printQueue[idx].qty = qty * (printQueue[idx].pack_size || 1); // keep reference quantity aligned
    
    // Trigger preview update
    const activeItem = printQueue[idx];
    BarcodeEvents.emit(BarcodeEvents.PREVIEW_REFRESH, activeItem);
}

function updateSize(idx, val) {
    const printQueue = window.BarcodeStudioState.printQueue;
    printQueue[idx].label_size = val;
    const activeItem = printQueue[idx];
    BarcodeEvents.emit(BarcodeEvents.PREVIEW_REFRESH, activeItem);
}

function removeRow(idx) {
    window.BarcodeStudioState.printQueue.splice(idx, 1);
    renderQueue();
}

// Bulk Actions
function clearQueue() {
    window.BarcodeStudioState.printQueue = [];
    const chkAll = document.getElementById('smriti-chk-all');
    if (chkAll) chkAll.checked = false;
    renderQueue();
    toast('Print queue cleared', 'success');
}

function bulkDelete() {
    window.BarcodeStudioState.printQueue = window.BarcodeStudioState.printQueue.filter(q => !q.selected);
    const chkAll = document.getElementById('smriti-chk-all');
    if (chkAll) chkAll.checked = false;
    renderQueue();
    toast('Selected items deleted from worksheet', 'success');
}

function bulkSetQty() {
    const qtyStr = prompt("Enter print quantity for all selected items:");
    const qty = parseInt(qtyStr);
    if (isNaN(qty) || qty < 1) {
        if (qtyStr !== null) toast("Invalid print quantity entered", "error");
        return;
    }
    window.BarcodeStudioState.printQueue.forEach(q => {
        if (q.selected) q.print_qty = qty;
    });
    renderQueue();
    toast(`Set print quantity to ${qty} for selected items`, 'success');
}

function bulkSetSize() {
    const selectedSize = prompt("Enter custom label size (e.g. 50x25, 50x30, 75x50, 100x50):", "50x25");
    if (!selectedSize) return;
    const allowed = ["50x25", "50x30", "75x50", "100x50", "106x55"];
    if (!allowed.includes(selectedSize)) {
        toast("Invalid size format! Choose 50x25, 50x30, 75x50, or 100x50", "error");
        return;
    }
    window.BarcodeStudioState.printQueue.forEach(q => {
        if (q.selected) q.label_size = selectedSize;
    });
    renderQueue();
    toast(`Set label size to ${selectedSize} for selected items`, 'success');
}

async function triggerLoadVariants() {
    let printQueue = window.BarcodeStudioState.printQueue;
    const selectedIdxs = printQueue.map((item, idx) => item.selected ? idx : -1).filter(idx => idx !== -1);
    if (!selectedIdxs.length) {
        toast('Please select at least one item in the worksheet to expand variants', 'info');
        return;
    }
    
    try {
        toast('Expanding selected items to variants...', 'info');
        const expandedQueue = [];
        
        for (let i = 0; i < printQueue.length; i++) {
            const item = printQueue[i];
            if (item.selected) {
                const variants = await api('smriti_retail_os.barcode_api.expand_item_variants', {
                    item_code: item.item_code,
                    default_print_qty: item.qty || 1
                });
                variants.forEach(v => {
                    expandedQueue.push({
                        ...v,
                        selected: true
                    });
                });
            } else {
                expandedQueue.push(item);
            }
        }
        
        window.BarcodeStudioState.printQueue = expandedQueue;
        updateQtyRule(window.BarcodeStudioState.activeQtyRule);
        toast('Expanded selected style templates to variants', 'success');
    } catch(e) {
        toast('Variant expansion failed: ' + e.message, 'error');
    }
}

function triggerSetLabels() {
    const printQueue = window.BarcodeStudioState.printQueue;
    const selectedIdxs = printQueue.map((item, idx) => item.selected ? idx : -1).filter(idx => idx !== -1);
    if (!selectedIdxs.length) {
        toast('Please select at least one item in the worksheet to set labels', 'info');
        return;
    }
    
    const inputVal = prompt('Enter print labels quantity for selected items:');
    if (inputVal === null) return;
    const qty = parseInt(inputVal);
    if (isNaN(qty) || qty <= 0) {
        toast('Please enter a valid positive number', 'error');
        return;
    }
    
    selectedIdxs.forEach(idx => {
        printQueue[idx].print_qty = qty;
        printQueue[idx].qty = qty * (printQueue[idx].pack_size || 1);
    });
    renderQueue();
    toast(`Set labels count to ${qty} for ${selectedIdxs.length} item(s)`, 'success');
}
