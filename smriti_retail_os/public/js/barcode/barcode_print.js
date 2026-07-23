/**
 * @file: smriti_retail_os/public/js/barcode/barcode_print.js
 * @description: Prints dispatcher to LAN socket, local USB (via QZ Tray), or PRN download.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

let finalPrintCallback = null;

async function downloadPRN() {
    const checkedItems = window.BarcodeStudioState.printQueue.filter(q => q.selected);
    if (!checkedItems.length) {
        toast('No rows selected for printing!', 'error');
        return;
    }

    const template = document.getElementById('cfg-template').value;
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    
    if (template) {
        const found = printTemplatesList.find(t => t.name === template);
        if (found && !validateSandbox(found.raw_template || '')) {
            const proceed = confirm("Pre-Print Sanitizer Warning: Template has unknown variables. Print anyway?");
            if (!proceed) return;
        }
    }

    try {
        const prnContent = await api('smriti_retail_os.barcode_api.generate_prn', {
            items: JSON.stringify(checkedItems),
            template_name: template || null
        });

        if (!prnContent) {
            toast('Failed to generate PRN data. Verify template/item sizes.', 'error');
            return;
        }

        if (prnContent.fallback_used) {
            toast('Warning: Built-in default template was used as a fallback for some items.', 'warning');
        }

        const blob = new Blob([prnContent.prn || prnContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `smriti_barcodes_${new Date().toISOString().slice(0,10)}.prn`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        toast('PRN file downloaded successfully', 'success');
        
        logSessionPrint('LOCAL', `PRN DOWNLOADED (${checkedItems.length} lines)`, true);
        const jobRef = document.getElementById('tx-name').value.trim() || 'Manual PRN';
        const totalQty = checkedItems.reduce((acc, q) => acc + q.print_qty, 0);
        recordPrintJob(jobRef, totalQty);
        
    } catch(e) {
        toast('PRN generation error: ' + e.message, 'error');
    }
}

function triggerPrintConfirmation() {
    const checkedItems = window.BarcodeStudioState.printQueue.filter(q => q.selected);
    if (!checkedItems.length) {
        toast('No rows selected for printing!', 'error');
        return;
    }

    const printerType = document.getElementById('cfg-printer-type').value;
    const template = document.getElementById('cfg-template').value;
    const ip = document.getElementById('cfg-ip').value.trim();
    const port = parseInt(document.getElementById('cfg-port').value) || 9100;
    const usbPrinter = document.getElementById('cfg-usb-printer').value;
    
    const targetPrinter = printerType === 'LAN' ? `${ip}:${port}` : (usbPrinter || "Default USB Printer");
    const templateName = template || "Built-in Default";
    const totalQty = checkedItems.reduce((acc, q) => acc + q.print_qty, 0);
    
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    let templateLanguage = "ZPL";
    if (template) {
        const found = printTemplatesList.find(t => t.name === template);
        if (found) templateLanguage = found.printer_language;
    } else {
        const activeItem = window.BarcodeStudioState.printQueue.find(q => q.selected) || window.BarcodeStudioState.printQueue[0];
        if (activeItem && activeItem.label_size === "106x55") {
            templateLanguage = "TSPL";
        }
    }
    
    const capabilityPreset = document.getElementById('cfg-capability').value;
    let printerLanguage = window.BarcodeStudioState.activePrinterLanguage;
    if (capabilityPreset === "Custom Profile") {
        printerLanguage = document.getElementById('cfg-custom-lang').value;
    }
    
    const ct = document.getElementById('confirm-template-name');
    const cpt = document.getElementById('confirm-printer-target');
    const clc = document.getElementById('confirm-label-count');
    const cpi = document.getElementById('confirm-printer-interface');
    
    if (ct) ct.textContent = templateName;
    if (cpt) cpt.textContent = targetPrinter;
    if (clc) clc.textContent = totalQty;
    if (cpi) cpi.textContent = printerType === 'LAN' ? 'LAN (Direct Socket)' : 'USB / Local (QZ Tray)';
    
    const activeIdx = window.BarcodeStudioState.printQueue.findIndex(q => q.selected);
    const itemToPreview = activeIdx !== -1 ? window.BarcodeStudioState.printQueue[activeIdx] : checkedItems[0];
    drawLivePreview(itemToPreview);
    drawConfirmPreview(itemToPreview);
    
    const highVolWarning = document.getElementById('confirm-high-volume-warning');
    if (highVolWarning) {
        if (totalQty > 200) {
            highVolWarning.innerHTML = `
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px dashed var(--danger); padding: 12px; border-radius: var(--radius-sm); color: var(--danger); font-weight: 700; margin-bottom: 12px; font-size: 0.85rem; line-height: 1.4;">
                    <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                        <span class="material-symbols-outlined" style="font-size:18px;">warning</span> High Volume Print Job
                    </div>
                    You are about to print <strong>${totalQty} labels</strong>. Please check that printer media, ribbon, and calibration are aligned before proceeding.
                </div>
            `;
            highVolWarning.style.display = 'block';
        } else {
            highVolWarning.style.display = 'none';
        }
    }
    
    const confirmMismatch = document.getElementById('confirm-mismatch-warning');
    if (confirmMismatch) {
        if (templateLanguage !== printerLanguage) {
            confirmMismatch.innerHTML = `
                <div style="background: rgba(245, 158, 11, 0.15); border: 1px dashed var(--warning); padding: 12px; border-radius: var(--radius-sm); color: var(--accent); font-weight: 600; margin-bottom: 12px; font-size: 0.85rem; line-height: 1.4;">
                    <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                        <span class="material-symbols-outlined" style="font-size:18px;">warning_amber</span> Template / Printer Language Mismatch
                    </div>
                    Template uses <strong>${templateLanguage}</strong> but the selected printer is configured for <strong>${printerLanguage}</strong>. The output may not print correctly.
                </div>
            `;
            confirmMismatch.style.display = 'block';
        } else {
            confirmMismatch.style.display = 'none';
        }
    }
    
    finalPrintCallback = function() {
        if (printerType === 'LAN') {
            executeDirectLANPrint(checkedItems, template, ip, port, totalQty);
        } else {
            executeDirectUSBPrint(checkedItems, template, usbPrinter, totalQty);
        }
    };
    
    openModal('print-confirm-modal');
}

function executeFinalPrintRun() {
    closeModal('print-confirm-modal');
    if (finalPrintCallback) {
        finalPrintCallback();
    }
}

async function executeDirectLANPrint(checkedItems, template, ip, port, totalQty) {
    if (!ip) {
        toast('Network Printer IP address is required for LAN printing.', 'error');
        return;
    }
    
    try {
        toast('Generating ZPL/TSPL print commands...', 'info');
        const prnContent = await api('smriti_retail_os.barcode_api.generate_prn', {
            items: JSON.stringify(checkedItems),
            template_name: template || null
        });
        
        if (!prnContent) {
            throw new Error('No print payload generated.');
        }

        if (prnContent.fallback_used) {
            toast('Warning: Built-in default template was used as a fallback for some items.', 'warning');
        }

        toast(`Queueing print job (${totalQty} labels)...`, 'info');
        const res = await api('smriti_retail_os.barcode_api.enqueue_print_job', {
            template_name: template || 'Built-in Default',
            printer_ip: ip,
            printer_port: port,
            labels_count: totalQty,
            payload: prnContent.prn || prnContent
        });

        if (res && res.job_id) {
            toast(`Print job queued successfully: ${res.job_id}`, 'success');
            logSessionPrint(ip, `DIRECT LAN QUEUED (${res.job_id})`, true);
            
            const jobRef = document.getElementById('tx-name').value.trim() || 'LAN Direct';
            recordPrintJob(jobRef, totalQty);
            
            pollPrintJobStatus(res.job_id);
            refreshPrintJobsDashboard();
        } else {
            throw new Error('Failed to enqueue print job.');
        }
    } catch(e) {
        toast(e.message, 'error');
        logSessionPrint(ip, 'LAN DIRECT FAIL: ' + e.message, false);
    }
}

async function executeDirectUSBPrint(checkedItems, template, usbPrinter, totalQty) {
    if (typeof qz === 'undefined' || !qz.websocket.isActive()) {
        toast('QZ Tray is not running. Please start QZ Tray on this machine.', 'error');
        return;
    }
    
    if (!usbPrinter) {
        toast('Please select a USB/Local printer from the list.', 'error');
        return;
    }
    
    try {
        toast('Generating ZPL/TSPL print commands...', 'info');
        const prnContent = await api('smriti_retail_os.barcode_api.generate_prn', {
            items: JSON.stringify(checkedItems),
            template_name: template || null
        });
        
        if (!prnContent) {
            throw new Error('No print payload generated.');
        }
        
        if (prnContent.fallback_used) {
            toast('Warning: Built-in default template was used as a fallback for some items.', 'warning');
        }
        
        toast(`Sending print job to local printer '${usbPrinter}' via QZ Tray...`, 'info');
        const config = qz.configs.create(usbPrinter);
        
        await qz.print(config, [{
            type: 'raw',
            format: 'command',
            flavor: 'plain',
            data: prnContent.prn || prnContent
        }]);
        
        toast(`Successfully sent ${totalQty} labels to printer '${usbPrinter}'`, 'success');
        logSessionPrint(usbPrinter, `USB PRINT SUCCESS (${totalQty} labels)`, true);
        
        const jobRef = document.getElementById('tx-name').value.trim() || 'USB Direct';
        recordPrintJob(jobRef, totalQty);
        
        await api('smriti_retail_os.barcode_api.log_print_job', {
            template_name: template || 'Built-in Default',
            printer_ip: usbPrinter,
            labels_count: totalQty,
            success: 1,
            print_profile: document.getElementById('cfg-profile').value || null,
            details: JSON.stringify(checkedItems.map(i => ({ code: i.item_code, qty: i.print_qty })))
        });

        BarcodeEvents.emit(BarcodeEvents.PRINT_COMPLETED, { usbPrinter, totalQty });
    } catch(e) {
        toast('USB Print failed: ' + e.message, 'error');
        logSessionPrint(usbPrinter || 'USB', 'USB PRINT FAIL: ' + e.message, false);
        
        await api('smriti_retail_os.barcode_api.log_print_job', {
            template_name: template || 'Built-in Default',
            printer_ip: usbPrinter || 'USB',
            labels_count: totalQty,
            success: 0,
            error_message: e.message,
            print_profile: document.getElementById('cfg-profile').value || null,
            details: JSON.stringify(checkedItems.map(i => ({ code: i.item_code, qty: i.print_qty })))
        });
    }
}

function downloadPreviewPDF() {
    const confirmPreviewContainer = document.getElementById('confirm-preview-container');
    const labelHtml = confirmPreviewContainer ? confirmPreviewContainer.innerHTML : "";
    const popup = window.open('', '_blank', 'width=1000,height=700');
    popup.document.write(`
        <html>
        <head>
            <title>Print Label Preview</title>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: var(--smriti-color-text-primary);
                    color: #000000;
                    font-family: 'Inter', sans-serif;
                }
                .sim-label {
                    background: var(--smriti-color-text-primary) !important;
                    color: #000000 !important;
                    border: 1px dashed #000000 !important;
                    box-shadow: none !important;
                }
                .sim-sub-col {
                    background: var(--smriti-color-text-primary) !important;
                    color: #000000 !important;
                    border: 1px dashed #000000 !important;
                }
                .sim-barcode-img {
                    background: repeating-linear-gradient(90deg, #000000, #000000 2px, var(--smriti-color-text-primary) 2px, var(--smriti-color-text-primary) 5px) !important;
                }
                .sim-barcode-img.narrow {
                    background: repeating-linear-gradient(90deg, #000000, #000000 1px, var(--smriti-color-text-primary) 1px, var(--smriti-color-text-primary) 3px) !important;
                }
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
            </style>
        </head>
        <body>
            ${labelHtml}
            <script>
                window.onload = function() {
                    window.print();
                };
            <\/script>
        </body>
        </html>
    `);
    popup.document.close();
}

function openRawPRNModal() {
    openModal('raw-prn-modal');
}

function toggleRawPRNSourceType(type) {
    const fileZone = document.getElementById('raw-prn-file-zone');
    const textZone = document.getElementById('raw-prn-text-zone');
    if (type === 'file') {
        if (fileZone) fileZone.style.display = 'block';
        if (textZone) textZone.style.display = 'none';
    } else {
        if (fileZone) fileZone.style.display = 'none';
        if (textZone) textZone.style.display = 'block';
    }
}

async function processRawPRNPrint() {
    const sourceType = document.querySelector('input[name="raw-prn-source-type"]:checked')?.value || 'text';
    const targetMode = document.getElementById('raw-prn-target')?.value || 'LAN';
    const repeatCount = parseInt(document.getElementById('raw-prn-repeat')?.value || '1');

    let prnContent = "";

    if (sourceType === 'file') {
        const fileInput = document.getElementById('raw-prn-file-input');
        if (!fileInput || !fileInput.files || !fileInput.files.length) {
            toast('Please select a PRN, ZPL, or TSPL file to upload', 'info');
            return;
        }
        const file = fileInput.files[0];
        prnContent = await file.text();
    } else {
        const rawText = document.getElementById('raw-prn-text-input');
        prnContent = rawText ? rawText.value.trim() : "";
    }

    if (!prnContent) {
        toast('No PRN content found. Please paste raw PRN commands or upload a PRN file.', 'info');
        return;
    }

    let fullPayload = (prnContent.trim() + "\n").repeat(repeatCount);

    try {
        if (targetMode === 'FILE') {
            const blob = new Blob([fullPayload], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `raw_third_party_${new Date().getTime()}.prn`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            toast(`Downloaded raw PRN file (x${repeatCount} copies)`, 'success');
            closeModal('raw-prn-modal');
            return;
        }

        if (targetMode === 'USB') {
            if (typeof qz === 'undefined' || !qz.websocket.isActive()) {
                toast('QZ Tray is not connected on this machine. Please start QZ Tray software.', 'error');
                return;
            }
            const printerName = document.getElementById('cfg-usb-printer')?.value;
            if (!printerName) {
                toast('Please select a local USB printer from the sidebar printer settings.', 'info');
                return;
            }
            const config = qz.configs.create(printerName);
            await qz.print(config, [{ type: 'raw', format: 'command', data: fullPayload }]);
            toast(`Successfully sent raw PRN commands to USB printer [${printerName}]`, 'success');
            closeModal('raw-prn-modal');
            return;
        }

        if (targetMode === 'LAN') {
            const ip = document.getElementById('cfg-lan-ip')?.value?.trim();
            const port = document.getElementById('cfg-lan-port')?.value?.trim() || 9100;
            if (!ip) {
                toast('Please enter LAN Printer IP address in the sidebar printer settings.', 'info');
                return;
            }
            toast(`Sending raw PRN payload to printer at ${ip}:${port}...`, 'info');
            const res = await api('smriti_retail_os.barcode_api.send_raw_prn_to_network_printer', {
                raw_prn_text: prnContent,
                printer_ip: ip,
                printer_port: port,
                repeat_count: repeatCount
            });
            toast(res.message || 'Raw PRN sent to network printer successfully', 'success');
            closeModal('raw-prn-modal');
            return;
        }
    } catch (e) {
        console.error("Raw PRN print failed:", e);
        toast('Failed to print raw PRN: ' + e.message, 'error');
    }
}
