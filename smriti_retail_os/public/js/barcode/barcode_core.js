/**
 * @file: smriti_retail_os/public/js/barcode/barcode_core.js
 * @description: Core helper library, state namespace, and pub/sub event bus for Barcode Studio.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

// ── Event Bus with Constants ──
const BarcodeEvents = {
    // Event Names
    QUEUE_UPDATED: 'queue-updated',
    PREVIEW_REFRESH: 'preview-refresh',
    PRINT_COMPLETED: 'print-completed',
    QZ_STATUS_CHANGED: 'qz-status-changed',
    TEMPLATE_CHANGED: 'template-changed',
    JOB_STATUS_CHANGED: 'job-status-changed',

    events: {},
    on(event, callback) {
        if (!this.events[event]) this.events[event] = [];
        this.events[event].push(callback);
    },
    off(event, callback) {
        if (!this.events[event]) return;
        this.events[event] = this.events[event].filter(cb => cb !== callback);
    },
    emit(event, data) {
        if (!this.events[event]) return;
        this.events[event].forEach(callback => {
            try {
                callback(data);
            } catch(e) {
                console.error(`Error in event handler for ${event}:`, e);
            }
        });
    }
};
window.BarcodeEvents = BarcodeEvents;

// ── Frozen Capabilities Configuration ──
const PRINTER_CAPABILITIES = {
    "TSC TE244": { language: "TSPL", dpi: 203 },
    "TVS LP46": { language: "TSPL", dpi: 203 },
    "Zebra GK420D": { language: "ZPL", dpi: 203 },
    "Zebra ZD230": { language: "ZPL", dpi: 203 },
    "Citizen CL-E321": { language: "ZPL", dpi: 300 },
    "TSC MH241": { language: "TSPL", dpi: 300 }
};
Object.freeze(PRINTER_CAPABILITIES);

// ── Global State Namespace Object ──
window.BarcodeStudioState = {
    csrfToken: '',
    cashier: '',
    printQueue: [],
    sizeOptions: [],
    printTemplatesList: [],
    printProfilesObj: {},
    activePrinterLanguage: "ZPL",
    activeDPI: 203,
    qzPrinters: [],
    activeQtyRule: 'piece',
    activeZoom: 100,
    activePreviewDPI: 203,
    activeShowMargins: true,
    designerMappings: [],
    canvasElements: [],
    selectedElementId: null,
    undoStack: [],
    redoStack: [],
    activeTemplateChecksum: null,
    activeTemplateName: null,
    activeTxItems: [],
    socket: null,
    tokenReferenceCache: null,
    printerCapabilities: PRINTER_CAPABILITIES
};

// ── REST API Fetch Helper ──
function api(method, params = {}) {
    const csrfToken = window.BarcodeStudioState.csrfToken;
    return fetch(`/api/method/${method}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'x-frappe-csrf-token': csrfToken
        },
        body: JSON.stringify(params)
    })
    .then(r => {
        if (!r.ok) {
            return r.json().then(d => {
                throw new Error(d._error_message || d.exception || d.exc || `HTTP error! status: ${r.status}`);
            }).catch(() => {
                throw new Error(`HTTP error! status: ${r.status}`);
            });
        }
        return r.json();
    })
    .then(d => {
        if (d.exc) throw new Error(d._error_message || d.exc);
        return d.message;
    });
}

// ── XSS Guard ──
function esc(s) {
    if (s === null || s === undefined) return '';
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// ── Toast Alerts ──
function toast(msg, type = 'success') {
    const cont = document.getElementById('toast-container');
    if (!cont) return;
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    const icon = type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info';
    
    const iconEl = document.createElement('span');
    iconEl.className = 'material-symbols-outlined';
    iconEl.textContent = icon;
    
    const msgEl = document.createElement('span');
    msgEl.textContent = msg;
    
    t.appendChild(iconEl);
    t.appendChild(document.createTextNode(' '));
    t.appendChild(msgEl);
    cont.appendChild(t);
    setTimeout(() => { t.remove(); }, 4000);
}

// ── Modal State Control ──
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('open');
        modal.style.display = 'flex';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('open');
        modal.style.display = 'none';
    }
}

// ── Debouncer ──
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
