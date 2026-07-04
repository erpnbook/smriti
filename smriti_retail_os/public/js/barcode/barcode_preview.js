/**
 * @file: smriti_retail_os/public/js/barcode/barcode_preview.js
 * @description: Visual label renderer and client-side design safety analyzer.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: MIT
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

// ── Event Registrations ──
BarcodeEvents.on(BarcodeEvents.QUEUE_UPDATED, () => {
    const printQueue = window.BarcodeStudioState.printQueue;
    const activeIdx = printQueue.findIndex(q => q.selected);
    if (activeIdx !== -1) {
        drawLivePreview(printQueue[activeIdx]);
        updateTokenMappingUI(printQueue[activeIdx]);
    } else if (printQueue.length > 0) {
        drawLivePreview(printQueue[0]);
        updateTokenMappingUI(printQueue[0]);
    } else {
        drawLivePreview(null);
        updateTokenMappingUI(null);
    }
});

BarcodeEvents.on(BarcodeEvents.PREVIEW_REFRESH, (item) => {
    drawLivePreview(item);
    updateTokenMappingUI(item);
});

// ── Preview Control State Operations ──
function updateZoom(val) {
    window.BarcodeStudioState.activeZoom = parseInt(val) || 100;
    const z1 = document.getElementById('preview-zoom');
    const z2 = document.getElementById('confirm-zoom');
    if (z1) z1.value = window.BarcodeStudioState.activeZoom;
    if (z2) z2.value = window.BarcodeStudioState.activeZoom;
    
    refreshActivePreview();
}

function updatePreviewDPI(val) {
    window.BarcodeStudioState.activePreviewDPI = parseInt(val) || 203;
    const d1 = document.getElementById('preview-dpi');
    const d2 = document.getElementById('confirm-dpi');
    if (d1) d1.value = window.BarcodeStudioState.activePreviewDPI;
    if (d2) d2.value = window.BarcodeStudioState.activePreviewDPI;
    
    refreshActivePreview();
}

function updateShowMargins(val) {
    window.BarcodeStudioState.activeShowMargins = !!val;
    const m1 = document.getElementById('preview-show-margins');
    const m2 = document.getElementById('confirm-show-margins');
    if (m1) m1.checked = window.BarcodeStudioState.activeShowMargins;
    if (m2) m2.checked = window.BarcodeStudioState.activeShowMargins;
    
    refreshActivePreview();
}

function refreshActivePreview() {
    const printQueue = window.BarcodeStudioState.printQueue;
    const activeItem = printQueue.find(q => q.selected) || printQueue[0];
    if (activeItem) {
        drawLivePreview(activeItem);
        drawConfirmPreview(activeItem);
    }
}

// ── Token Substitution with Local Cache ──
function resolveTokens(contentStr, item) {
    if (!contentStr) return "";
    let res = contentStr;
    const defaults = {
        barcode: item.barcode || "8901234567890",
        item_code: item.item_code || "ITEM-12345",
        item_name: item.item_name || "Sample Item Name Description",
        brand: item.brand || "SMRITI",
        mrp: String(parseInt(item.mrp || 499)),
        size: item.size || "8",
        color: item.color || "BLACK",
        style: item.style || "STYLE",
        pkd_date: item.pkd_date || "06/26"
    };

    const cache = window.BarcodeStudioState.tokenReferenceCache;
    if (cache && Array.isArray(cache)) {
        cache.forEach(ref => {
            const cleanPlaceholder = ref.placeholder.replace('{', '').replace('}', '');
            let val = item[ref.erp_field] || defaults[cleanPlaceholder];
            if (val === undefined || val === null) val = "";
            res = res.replace(new RegExp(`{${cleanPlaceholder}}`, 'g'), String(val));
        });
    }

    for (const [k, v] of Object.entries(defaults)) {
        res = res.replace(new RegExp(`{${k}}`, 'g'), v);
    }
    return res;
}

// ── Visual Helper Functions ──
function getTextWidth(text, fontSize) {
    try {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        context.font = `bold ${fontSize}px Courier New`;
        return context.measureText(text).width;
    } catch(e) {
        return text.length * fontSize * 0.6;
    }
}

function generateBarcodeSVG(x, y, w, h, value) {
    let html = `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="var(--smriti-color-text-primary)" />`;
    const barsCount = 40;
    const barW = w / (barsCount * 1.5);
    let curX = x + (w - (barsCount * 1.5 * barW)) / 2;
    
    html += `<g fill="#000000">`;
    for (let i = 0; i < barsCount; i++) {
        const isBar = (i % 3 !== 0) && (i % 8 !== 5);
        if (isBar) {
            html += `<rect x="${curX}" y="${y}" width="${barW}" height="${h * 0.85}" />`;
        }
        curX += barW * 1.5;
    }
    html += `</g>`;
    
    const textLabel = value || "1234567890123";
    html += `<text x="${x + w/2}" y="${y + h - 2}" font-size="${Math.max(6, h * 0.12)}px" font-family="monospace" text-anchor="middle" fill="#000000">${textLabel}</text>`;
    return html;
}

function generateQRCodeSVG(x, y, w, h, value) {
    const size = Math.min(w, h);
    const grid = 15;
    const mod = size / grid;
    const ox = x + (w - size) / 2;
    const oy = y + (h - size) / 2;
    
    let html = `<rect x="${ox}" y="${oy}" width="${size}" height="${size}" fill="var(--smriti-color-text-primary)" />`;
    html += `<g fill="#000000">`;
    
    html += `<rect x="${ox}" y="${oy}" width="${mod * 5}" height="${mod * 5}" />`;
    html += `<rect x="${ox + mod}" y="${oy + mod}" width="${mod * 3}" height="${mod * 3}" fill="var(--smriti-color-text-primary)" />`;
    html += `<rect x="${ox + mod * 2}" y="${oy + mod * 2}" width="${mod}" height="${mod}" />`;
    
    html += `<rect x="${ox + size - mod * 5}" y="${oy}" width="${mod * 5}" height="${mod * 5}" />`;
    html += `<rect x="${ox + size - mod * 4}" y="${oy + mod}" width="${mod * 3}" height="${mod * 3}" fill="var(--smriti-color-text-primary)" />`;
    html += `<rect x="${ox + size - mod * 3}" y="${oy + mod * 2}" width="${mod}" height="${mod}" />`;
    
    html += `<rect x="${ox}" y="${oy + size - mod * 5}" width="${mod * 5}" height="${mod * 5}" />`;
    html += `<rect x="${ox + mod}" y="${oy + size - mod * 4}" width="${mod * 3}" height="${mod * 3}" fill="var(--smriti-color-text-primary)" />`;
    html += `<rect x="${ox + mod * 2}" y="${oy + size - mod * 3}" width="${mod}" height="${mod}" />`;
    
    for (let r = 0; r < grid; r++) {
        for (let c = 0; c < grid; c++) {
            if (r < 5 && c < 5) continue;
            if (r < 5 && c >= grid - 5) continue;
            if (r >= grid - 5 && c < 5) continue;
            
            const draw = ((r * c) % 3 === 0) || ((r + c) % 5 === 2);
            if (draw) {
                html += `<rect x="${ox + c * mod}" y="${oy + r * mod}" width="${mod}" height="${mod}" />`;
            }
        }
    }
    html += `</g>`;
    return html;
}

function checkElementCollision(a, b) {
    return (a.x < b.x + b.w) &&
           (a.x + a.w > b.x) &&
           (a.y < b.y + b.h) &&
           (a.y + a.h > b.y);
}

// ── Layout Diagnostics engine ──
function validateLayoutDiagnostics(item, elements, labelSize, dpi) {
    let parts = (labelSize || "50x25").split('x');
    let lw = parseFloat(parts[0]) || 50;
    let lh = parseFloat(parts[1]) || 25;
    
    let diagnostics = [];
    const SAFE_MARGIN_MM = 1.5;

    function estimateTextWidthMM(text, heightMM) {
        return text.length * 1.8;
    }

    elements.forEach(elem => {
        let x = parseFloat(elem.x) || 0;
        let y = parseFloat(elem.y) || 0;
        let w = parseFloat(elem.w) || 0;
        let h = parseFloat(elem.h) || 0;
        let elType = elem.type || "";
        let elId = elem.id || "";
        let content = elem.content || "";

        if (x < 0 || y < 0 || (x + w) > lw || (y + h) > lh) {
            diagnostics.push({
                element_id: elId,
                severity: "error",
                message: `Element ${elId || elType} exceeds printable area (${lw}x${lh}mm)`
            });
            return;
        }

        if (x < SAFE_MARGIN_MM || y < SAFE_MARGIN_MM || (x + w) > (lw - SAFE_MARGIN_MM) || (y + h) > (lh - SAFE_MARGIN_MM)) {
            if (elType === 'barcode' || elType === 'qrcode') {
                diagnostics.push({
                    element_id: elId,
                    severity: "error",
                    message: `${elType.toUpperCase()} ${elId} overlaps print-safe margin`
                });
            } else {
                diagnostics.push({
                    element_id: elId,
                    severity: "warning",
                    message: `Element ${elId || elType} overlaps print-safe margin`
                });
            }
        }

        if (elType === 'text') {
            let resolved = resolveTokens(content, item);
            let estW = estimateTextWidthMM(resolved, h);
            if (estW > w) {
                diagnostics.push({
                    element_id: elId,
                    severity: "warning",
                    message: `Text element ${elId} content may overflow designed width`
                });
            }
        }
    });

    let nonDecorative = elements.filter(e => e.type !== 'box' && e.type !== 'bar');
    for (let i = 0; i < nonDecorative.length; i++) {
        for (let j = i + 1; j < nonDecorative.length; j++) {
            let a = nonDecorative[i];
            let b = nonDecorative[j];
            if (checkElementCollision(a, b)) {
                diagnostics.push({
                    element_id: `${a.id}<->${b.id}`,
                    severity: "error",
                    message: `Collision detected between ${a.id || a.type} and ${b.id || b.type}`
                });
            }
        }
    }

    return diagnostics;
}

// ── SVG Preview generator ──
function renderSVGPreview(item, layoutJson, dpi, zoom, showMargins) {
    const elements = parseLayoutJson(layoutJson);
    let parts = (item.label_size || "50x25").split('x');
    let mmW = parseFloat(parts[0]) || 50;
    let mmH = parseFloat(parts[1]) || 25;
    
    const dotsW = Math.round(mmW * dpi / 25.4);
    const dotsH = Math.round(mmH * dpi / 25.4);
    const pxW = mmW * 8 * (zoom / 100);
    const pxH = mmH * 8 * (zoom / 100);
    
    let svg = `<svg viewBox="0 0 ${dotsW} ${dotsH}" width="${pxW}px" height="${pxH}px" style="background:var(--smriti-color-text-primary); border:1px solid #cbd5e1; border-radius:4px; overflow:hidden; display:block;" xmlns="http://www.w3.org/2000/svg">`;
    
    function toDots(mm) {
        return Math.round(mm * dpi / 25.4);
    }
    
    svg += `<g stroke="#f1f5f9" stroke-width="0.5">`;
    const step = toDots(2);
    for (let x = step; x < dotsW; x += step) {
        svg += `<line x1="${x}" y1="0" x2="${x}" y2="${dotsH}" />`;
    }
    for (let y = step; y < dotsH; y += step) {
        svg += `<line x1="0" y1="${y}" x2="${dotsW}" y2="${y}" />`;
    }
    svg += `</g>`;
    
    elements.forEach(elem => {
        const dx = toDots(elem.x);
        const dy = toDots(elem.y);
        const dw = toDots(elem.w);
        const dh = toDots(elem.h);
        const rot = elem.rotation || 0;
        
        if (elem.type === 'text') {
            const resolved = resolveTokens(elem.content, item);
            const fontSize = dh > 0 ? dh * 0.75 : 16;
            const yOffset = dy + (dh > 0 ? dh * 0.8 : 12);
            svg += `<text x="${dx}" y="${yOffset}" font-size="${fontSize}px" font-family="'Courier New', Courier, monospace" font-weight="bold" fill="#000000" transform="rotate(${rot}, ${dx}, ${dy})">${esc(resolved)}</text>`;
        } else if (elem.type === 'box') {
            svg += `<rect x="${dx}" y="${dy}" width="${dw}" height="${dh}" fill="none" stroke="#000000" stroke-width="2.5" transform="rotate(${rot}, ${dx + dw/2}, ${dy + dh/2})" />`;
        } else if (elem.type === 'bar') {
            svg += `<rect x="${dx}" y="${dy}" width="${dw}" height="${dh}" fill="#000000" transform="rotate(${rot}, ${dx + dw/2}, ${dy + dh/2})" />`;
        } else if (elem.type === 'barcode') {
            const resolvedBC = resolveTokens(elem.content, item);
            svg += `<g transform="rotate(${rot}, ${dx + dw/2}, ${dy + dh/2})">`;
            svg += generateBarcodeSVG(dx, dy, dw, dh, resolvedBC);
            svg += `</g>`;
        } else if (elem.type === 'qrcode') {
            const resolvedQR = resolveTokens(elem.content, item);
            svg += `<g transform="rotate(${rot}, ${dx + dw/2}, ${dy + dh/2})">`;
            svg += generateQRCodeSVG(dx, dy, dw, dh, resolvedQR);
            svg += `</g>`;
        } else if (elem.type === 'image') {
            svg += `<g transform="rotate(${rot}, ${dx + dw/2}, ${dy + dh/2})">`;
            if (elem.image_ref) {
                svg += `<image href="/files/${elem.image_ref}" x="${dx}" y="${dy}" width="${dw}" height="${dh}" preserveAspectRatio="none" />`;
            } else {
                svg += `<rect x="${dx}" y="${dy}" width="${dw}" height="${dh}" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1" />`;
                svg += `<text x="${dx + dw/2}" y="${dy + dh/2 + 3}" font-size="8px" text-anchor="middle" fill="#64748b" font-family="sans-serif">No Image</text>`;
            }
            svg += `</g>`;
        }
    });
    
    if (showMargins) {
        const marginDots = toDots(1.5);
        svg += `<rect x="${marginDots}" y="${marginDots}" width="${dotsW - marginDots * 2}" height="${dotsH - marginDots * 2}" fill="none" stroke="var(--barcode-danger-glow)" stroke-width="1" stroke-dasharray="3,3" pointer-events="none" />`;
    }
    
    svg += `</svg>`;
    return svg;
}

// ── Live Simulator Renderers ──
function drawLivePreview(item) {
    const boxContainer = document.getElementById('preview-box-container');
    if (!boxContainer) return;
    if (!item) {
        boxContainer.innerHTML = `
            <div class="sim-label sz-50x25" style="display:flex; align-items:center; justify-content:center; text-align:center; color:var(--text-sub);">
                <div style="font-size:10px;">Load and select an item to simulate visual output</div>
            </div>
        `;
        return;
    }

    const templateSelect = document.getElementById('cfg-template');
    const selectedTemplateVal = templateSelect ? templateSelect.value : "";
    
    let hasVisualLayout = false;
    let templateObj = null;
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    if (selectedTemplateVal) {
        templateObj = printTemplatesList.find(t => t.name === selectedTemplateVal);
        if (templateObj && templateObj.custom_visual_layout_json) {
            hasVisualLayout = true;
        }
    }

    if (hasVisualLayout) {
        const svgHTML = renderSVGPreview(item, templateObj.custom_visual_layout_json, window.BarcodeStudioState.activePreviewDPI, window.BarcodeStudioState.activeZoom, window.BarcodeStudioState.activeShowMargins);
        boxContainer.innerHTML = `<div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; overflow: auto; padding: 10px;">${svgHTML}</div>`;
    } else {
        let templateLanguage = window.BarcodeStudioState.activePrinterLanguage;
        let templateSize = item.label_size || "50x25";

        if (selectedTemplateVal) {
            const found = printTemplatesList.find(t => t.name === selectedTemplateVal);
            if (found) {
                templateLanguage = found.printer_language;
                templateSize = found.label_size;
            }
        }

        if (templateSize === "106x55") {
            boxContainer.innerHTML = `
                <div class="sim-label sz-106x55">
                    <div class="sim-sub-col sim-col1">
                        <div class="sim-brand" style="font-size:7px; margin-bottom:1px;">${(item.brand || 'SMRITI').toUpperCase()}</div>
                        <div class="sim-name" style="font-size:7px; margin-bottom:1px;">${item.item_name}</div>
                        <div class="sim-barcode-img narrow" style="height:16px;"></div>
                        <div class="sim-barcode-text" style="font-size:6px; margin-bottom:1px;" id="sim-barcode">${item.barcode}</div>
                        <div class="sim-mrp-price" style="font-size:7px; margin-top:2px;">Rs. ${parseInt(item.mrp)}/-</div>
                        <div class="sim-meta" style="font-size:6px; margin-top:1px;">
                            <span>Sz: ${item.size || 'L'}</span>
                            <span>Col: ${item.color || ''}</span>
                        </div>
                    </div>
                    <div class="sim-sub-col sim-col2">
                        <div class="sim-brand" style="font-size:6px; border:none; margin-bottom:0; text-align:left;">${(item.brand || 'S').toUpperCase()}</div>
                        <div class="sim-name" style="font-size:6px; margin-bottom:0;">${item.style}</div>
                        <div class="sim-barcode-img narrow" style="height:12px;"></div>
                        <div style="font-size:5px; text-align:center;">${item.barcode}</div>
                        <div style="font-size:7px; font-weight:800; margin-top:auto;">Rs. ${parseInt(item.mrp)}</div>
                        <div style="font-size:5px; color:#475569;">Size: ${item.size || 'L'}</div>
                    </div>
                    <div class="sim-sub-col sim-col3">
                        <div class="sim-brand" style="font-size:6px; border:none; margin-bottom:0; text-align:left;">${(item.brand || 'S').toUpperCase()}</div>
                        <div class="sim-name" style="font-size:6px; margin-bottom:0;">${item.style}</div>
                        <div class="sim-barcode-img narrow" style="height:12px;"></div>
                        <div style="font-size:5px; text-align:center;">${item.barcode}</div>
                        <div style="font-size:7px; font-weight:800; margin-top:auto;">Rs. ${parseInt(item.mrp)}</div>
                        <div style="font-size:5px; color:#475569;">Size: ${item.size || 'L'}</div>
                    </div>
                </div>
            `;
        } else {
            let barcodeImgClass = "sim-barcode-img";
            if (templateSize === "50x25" || templateSize === "50x30") {
                barcodeImgClass = "sim-barcode-img narrow";
            }
            
            boxContainer.innerHTML = `
                <div class="sim-label sz-${templateSize}" id="sim-label-box">
                    <div class="sim-brand" id="sim-brand">${(item.brand || 'SMRITI').toUpperCase()}</div>
                    <div class="sim-name" id="sim-name">${item.item_name}</div>
                    <div class="${barcodeImgClass}" id="sim-barcode-img"></div>
                    <div class="sim-barcode-text" id="sim-barcode">${item.barcode}</div>
                    <div class="sim-mrp-price" id="sim-mrp-row">
                        <span>Rs. ${parseInt(item.mrp)}.00</span>
                        <span style="font-size:7px; font-weight:normal;">(Incl of all Taxes)</span>
                    </div>
                    <div class="sim-meta" id="sim-meta-row">
                        <span>SIZE: ${item.size || 'N/A'}</span>
                        <span>ART: ${item.style}</span>
                    </div>
                </div>
            `;
        }
    }
}

function drawConfirmPreview(item) {
    const container = document.getElementById('confirm-preview-container');
    if (!container) return;

    const templateSelect = document.getElementById('cfg-template');
    const selectedTemplateVal = templateSelect ? templateSelect.value : "";
    let templateObj = null;
    let hasVisualLayout = false;
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    if (selectedTemplateVal) {
        templateObj = printTemplatesList.find(t => t.name === selectedTemplateVal);
        if (templateObj && templateObj.custom_visual_layout_json) {
            hasVisualLayout = true;
        }
    }

    if (hasVisualLayout) {
        const svgHTML = renderSVGPreview(item, templateObj.custom_visual_layout_json, window.BarcodeStudioState.activePreviewDPI, window.BarcodeStudioState.activeZoom, window.BarcodeStudioState.activeShowMargins);
        container.innerHTML = `<div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; overflow: auto; padding: 10px;">${svgHTML}</div>`;
        
        updateConfirmMetadata(templateObj);
        
        const elements = parseLayoutJson(templateObj.custom_visual_layout_json);
        const diagnostics = validateLayoutDiagnostics(item, elements, templateObj.label_size, window.BarcodeStudioState.activePreviewDPI);
        showConfirmDiagnostics(diagnostics);
    } else {
        const boxContainer = document.getElementById('preview-box-container');
        if (boxContainer) container.innerHTML = boxContainer.innerHTML;
        const metaPanel = document.getElementById('confirm-metadata-panel');
        if (metaPanel) metaPanel.style.display = 'none';
        const diagBox = document.getElementById('confirm-validation-box');
        if (diagBox) diagBox.style.display = 'none';
        
        const printBtn = document.getElementById('btn-confirm-print-action');
        if (printBtn) {
            printBtn.removeAttribute('disabled');
            printBtn.style.opacity = '1';
            printBtn.style.pointerEvents = 'auto';
        }
    }
}

function updateConfirmMetadata(templateObj) {
    const metaPanel = document.getElementById('confirm-metadata-panel');
    if (!metaPanel) return;
    metaPanel.style.display = 'grid';

    let layoutVer = 1;
    let compilerVer = 1;
    let elementsCount = 0;
    
    if (templateObj && templateObj.custom_visual_layout_json) {
        try {
            const parsed = JSON.parse(templateObj.custom_visual_layout_json);
            if (parsed.layout_version) layoutVer = parsed.layout_version;
            if (parsed.compiler_version) compilerVer = parsed.compiler_version;
            if (parsed.elements) elementsCount = parsed.elements.length;
            else if (Array.isArray(parsed)) elementsCount = parsed.length;
        } catch(e) {
            console.error(e);
        }
    }

    const lvEl = document.getElementById('meta-layout-version');
    const cvEl = document.getElementById('meta-compiler-version');
    const adEl = document.getElementById('meta-active-dpi');
    const ecEl = document.getElementById('meta-elements-count');
    
    if (lvEl) lvEl.textContent = layoutVer;
    if (cvEl) cvEl.textContent = compilerVer;
    if (adEl) adEl.textContent = window.BarcodeStudioState.activePreviewDPI + ' DPI';
    if (ecEl) ecEl.textContent = elementsCount;
}

function showConfirmDiagnostics(diagnostics) {
    const diagBox = document.getElementById('confirm-validation-box');
    const list = document.getElementById('validation-diagnostics-list');
    const printBtn = document.getElementById('btn-confirm-print-action');
    const diagCountEl = document.getElementById('meta-diagnostics-count');
    
    if (!diagBox || !list) return;
    
    let errorsCount = 0;
    let warningsCount = 0;
    
    list.innerHTML = '';
    
    if (diagnostics.length === 0) {
        diagBox.style.display = 'block';
        list.innerHTML = `
            <div style="color: var(--success); display: flex; align-items: center; gap: 6px; font-weight: 600; padding: 4px 0;">
                <span class="material-symbols-outlined" style="font-size: 16px;">check_circle</span>
                All pre-print validation checks passed. Label is print-safe.
            </div>
        `;
        if (diagCountEl) diagCountEl.innerHTML = '<span style="color: var(--success); font-weight: bold;">0 Errors / 0 Warnings</span>';
        
        if (printBtn) {
            printBtn.removeAttribute('disabled');
            printBtn.style.opacity = '1';
            printBtn.style.pointerEvents = 'auto';
        }
        return;
    }
    
    diagBox.style.display = 'block';
    
    diagnostics.forEach(diag => {
        let icon = 'warning';
        let color = 'var(--warning)';
        if (diag.severity === 'error') {
            errorsCount++;
            icon = 'cancel';
            color = 'var(--danger)';
        } else {
            warningsCount++;
        }
        
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.alignItems = 'flex-start';
        row.style.gap = '6px';
        row.style.padding = '4px 0';
        row.style.color = color;
        row.style.lineHeight = '1.3';
        row.innerHTML = `
            <span class="material-symbols-outlined" style="font-size: 16px; margin-top: 1px;">${icon}</span>
            <span><strong>[${diag.severity.toUpperCase()}]</strong> ${diag.message}</span>
        `;
        list.appendChild(row);
    });
    
    if (diagCountEl) {
        diagCountEl.innerHTML = `
            <span style="color: ${errorsCount > 0 ? 'var(--danger)' : 'var(--warning)'}; font-weight: bold;">
                ${errorsCount} Errors / ${warningsCount} Warnings
            </span>
        `;
    }
    
    if (printBtn) {
        if (errorsCount > 0) {
            printBtn.setAttribute('disabled', 'true');
            printBtn.style.opacity = '0.5';
            printBtn.style.pointerEvents = 'none';
        } else {
            printBtn.removeAttribute('disabled');
            printBtn.style.opacity = '1';
            printBtn.style.pointerEvents = 'auto';
        }
    }
}

function updateTokenMappingUI(item) {
    const container = document.getElementById('token-mapping-content');
    if (!container) return;
    if (!item) {
        container.innerHTML = `<div style="color: var(--text-muted); text-align: center;">Select an item in the worksheet to view token mapping</div>`;
        return;
    }
    
    const tokens = [
        { name: 'Barcode', val: item.barcode || 'N/A' },
        { name: 'MRP', val: item.mrp },
        { name: 'Color', val: item.color || 'N/A' },
        { name: 'Size', val: item.size || 'N/A' },
        { name: 'Style', val: item.style || 'N/A' },
        { name: 'Brand', val: item.brand || 'N/A' },
        { name: 'Item Code', val: item.item_code },
        { name: 'Item Name', val: item.item_name }
    ];
    
    container.innerHTML = tokens.map(t => 
        `<div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--barcode-overlay-md); padding-bottom: 4px;">
            <span style="color: var(--primary-lt); font-size: 11px;">{${t.name.toLowerCase().replace(' ', '_')}} &rarr;</span>
            <span style="color: var(--text); text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 160px; font-size: 11px;" title="${esc(t.val)}">${esc(t.val)}</span>
         </div>`
    ).join('');
}
