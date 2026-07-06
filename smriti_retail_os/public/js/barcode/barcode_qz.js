/**
 * @file: smriti_retail_os/public/js/barcode/barcode_qz.js
 * @description: QZ Tray WebSocket connector and printers scanner.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

function initQZ() {
    if (typeof qz === 'undefined') {
        updateQZStatus(false, "QZ library not loaded");
        return;
    }
    try {
        qz.security.setCertificatePromise((resolve) => resolve());
        qz.security.setSignaturePromise(() => (resolve) => resolve());
    } catch(e) {
        console.warn("QZ security configuration failed:", e);
    }
    checkQZConnection();
    setInterval(checkQZConnection, 5000);
}

async function checkQZConnection() {
    if (typeof qz === 'undefined') {
        updateQZStatus(false, "QZ library not loaded");
        return;
    }
    if (qz.websocket.isActive()) {
        updateQZStatus(true, "QZ Connected");
        return;
    }
    try {
        await qz.websocket.connect();
        updateQZStatus(true, "QZ Connected");
        await refreshQZPrinters();
    } catch (e) {
        updateQZStatus(false, "QZ Tray Not Running");
    }
}

function updateQZStatus(connected, text) {
    const dot = document.getElementById('qz-status-dot');
    const textEl = document.getElementById('qz-status-text');
    if (dot && textEl) {
        if (connected) {
            dot.style.backgroundColor = 'var(--success)';
            textEl.textContent = `🟢 ${text}`;
        } else {
            dot.style.backgroundColor = 'var(--danger)';
            textEl.textContent = `🔴 ${text}`;
        }
    }
    BarcodeEvents.emit(BarcodeEvents.QZ_STATUS_CHANGED, { connected, text });
}

async function refreshQZPrinters() {
    if (typeof qz === 'undefined' || !qz.websocket.isActive()) return;
    try {
        const printers = await qz.printers.find();
        window.BarcodeStudioState.qzPrinters = printers || [];
        populateQZPrintersDropdown();
    } catch(e) {
        console.error("Failed to fetch QZ printers:", e);
    }
}

function populateQZPrintersDropdown() {
    const usbSel = document.getElementById('cfg-usb-printer');
    if (!usbSel) return;
    const currentVal = usbSel.value;
    const qzPrinters = window.BarcodeStudioState.qzPrinters;
    if (!qzPrinters.length) {
        usbSel.innerHTML = '<option value="">-- No Local Printers Detected --</option>';
        return;
    }
    usbSel.innerHTML = qzPrinters.map(p => `<option value="${esc(p)}">${esc(p)}</option>`).join('');
    if (qzPrinters.includes(currentVal)) {
        usbSel.value = currentVal;
    }
}

function togglePrinterTypeFields(type) {
    const lanGroup = document.getElementById('lan-fields-group');
    const usbGroup = document.getElementById('usb-fields-group');
    if (type === 'LAN') {
        if (lanGroup) lanGroup.style.display = 'block';
        if (usbGroup) usbGroup.style.display = 'none';
    } else {
        if (lanGroup) lanGroup.style.display = 'none';
        if (usbGroup) usbGroup.style.display = 'block';
        checkQZConnection();
    }
}
