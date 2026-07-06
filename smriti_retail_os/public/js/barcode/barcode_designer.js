/**
 * @file: smriti_retail_os/public/js/barcode/barcode_designer.js
 * @description: Visual template visual editor, canvas mappings, and raw PRN parser.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

// ── Tab Switching ──
function switchDesignerTab(tab) {
    const activeTemplateName = window.BarcodeStudioState.activeTemplateName;
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    const canvasElements = window.BarcodeStudioState.canvasElements;
    
    if (tab === 'visual') {
        const template = activeTemplateName ? printTemplatesList.find(t => t.name === activeTemplateName) : null;
        if (activeTemplateName && (!template || !template.custom_visual_layout_json) && canvasElements.length === 0) {
            toast('Legacy template lacks visual layout JSON. Open in Raw mode only.', 'error');
            switchDesignerTab('raw');
            return;
        }
    }
    
    window.BarcodeStudioState.activeTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    const visualContent = document.getElementById('designer-visual-tab-content');
    const rawContent = document.getElementById('designer-raw-tab-content');
    const visualTabBtn = document.getElementById('btn-tab-visual');
    const rawTabBtn = document.getElementById('btn-tab-raw');
    
    if (tab === 'visual') {
        if (visualTabBtn) visualTabBtn.classList.add('active');
        if (visualContent) visualContent.style.display = 'flex';
        if (rawContent) rawContent.style.display = 'none';
        renderCanvas();
    } else {
        if (rawTabBtn) rawTabBtn.classList.add('active');
        if (visualContent) visualContent.style.display = 'none';
        if (rawContent) rawContent.style.display = 'flex';
        
        if (canvasElements.length > 0) {
            document.getElementById('design-raw').value = compileVisualToPRN();
            validateSandbox(document.getElementById('design-raw').value);
        }
    }
}

// ── Bounding Canvas Dimensions ──
function updateCanvasDimensions() {
    const sizeVal = document.getElementById('design-size').value;
    const parts = sizeVal.split('x');
    if (parts.length === 2) {
        const mmW = parseFloat(parts[0]);
        const mmH = parseFloat(parts[1]);
        const canvas = document.getElementById('visual-canvas');
        if (canvas) {
            canvas.style.width = (mmW * 8) + 'px';
            canvas.style.height = (mmH * 8) + 'px';
        }
    }
}

function parseLayoutJson(jsonStr) {
    if (!jsonStr) return [];
    try {
        const parsed = JSON.parse(jsonStr);
        if (Array.isArray(parsed)) {
            return parsed;
        } else if (parsed && parsed.elements) {
            return parsed.elements;
        }
    } catch(e) {
        console.error("Error parsing layout JSON:", e);
    }
    return [];
}

function getLayoutJsonString() {
    const canvasElements = window.BarcodeStudioState.canvasElements;
    if (canvasElements.length === 0) return null;
    return JSON.stringify({
        layout_version: 1,
        compiler_version: 1,
        elements: canvasElements
    });
}

function openTemplateDesigner() {
    const template = document.getElementById('cfg-template').value;
    const printTemplatesList = window.BarcodeStudioState.printTemplatesList;
    
    const chips = [
        "barcode", "item_code", "item_name", "brand", "mrp", "size", "color", "style", "pkd_date",
        "gender", "heel_type", "outsole", "upper_material", "merchandise_category", "sub_category", "purchase_class"
    ];
    const chipsDiv = document.getElementById('token-chip-list');
    if (chipsDiv) {
        chipsDiv.innerHTML = chips.map(c => `
            <span class="token-chip" onclick="insertTokenAtCursor('{${c}}')">{${c}}</span>
        `).join('');
    }

    window.BarcodeStudioState.undoStack = [];
    window.BarcodeStudioState.redoStack = [];
    updateUndoRedoButtons();
    window.BarcodeStudioState.selectedElementId = null;

    if (template) {
        const found = printTemplatesList.find(t => t.name === template);
        if (found) {
            window.BarcodeStudioState.activeTemplateName = found.name;
            window.BarcodeStudioState.activeTemplateChecksum = found.template_checksum;
            
            document.getElementById('design-name').value = found.template_name;
            document.getElementById('design-lang').value = found.printer_language;
            document.getElementById('design-size').value = found.label_size;
            document.getElementById('design-raw').value = found.raw_template || '';
            
            try {
                window.BarcodeStudioState.designerMappings = found.custom_field_mappings_json ? JSON.parse(found.custom_field_mappings_json) : [];
            } catch(e) {
                window.BarcodeStudioState.designerMappings = [];
            }
            
            window.BarcodeStudioState.canvasElements = parseLayoutJson(found.custom_visual_layout_json);
            
            renderMappingTable();
            validateSandbox(found.raw_template || '');
            loadVersionHistory(found.name);
            openModal('designer-modal');
            
            if (found.custom_visual_layout_json) {
                switchDesignerTab('visual');
            } else {
                switchDesignerTab('raw');
            }
            return;
        }
    }

    window.BarcodeStudioState.activeTemplateName = null;
    window.BarcodeStudioState.activeTemplateChecksum = null;
    document.getElementById('design-name').value = '';
    document.getElementById('design-lang').value = 'ZPL';
    document.getElementById('design-size').value = '50x25';
    document.getElementById('design-raw').value = '^XA\n^FO20,10^BCN,60,Y,N,N^FD{barcode}^FS\n^FO20,80^ADN,18,10^FD{item_name}^FS\n^FO20,100^ADN,18,10^FDMRP: Rs.{mrp}^FS\n^FO20,120^ADN,14,8^FD{brand} | Size: {size}^FS\n^XZ';
    window.BarcodeStudioState.designerMappings = [];
    window.BarcodeStudioState.canvasElements = [];
    renderMappingTable();
    validateSandbox(document.getElementById('design-raw').value);
    
    const dropdown = document.getElementById('design-version-history');
    if (dropdown) dropdown.innerHTML = '<option value="">-- Active (Latest) --</option>';
    
    openModal('designer-modal');
    switchDesignerTab('visual');
}

function insertTokenAtCursor(text) {
    const textel = document.getElementById('design-raw');
    const scrollPos = textel.scrollTop;
    let strPos = 0;
    const br = ((textel.selectionStart || textel.selectionStart === '0') ? "ff" : (document.selection ? "ie" : false));
    if (br === "ff") {
        strPos = textel.selectionStart;
    } else if (br === "ie") {
        textel.focus();
        const range = document.selection.createRange();
        range.moveStart('character', -textel.value.length);
        strPos = range.text.length;
    }

    const front = (textel.value).substring(0, strPos);
    const back = (textel.value).substring(strPos, textel.value.length);
    textel.value = front + text + back;
    strPos = strPos + text.length;
    if (br === "ff") {
        textel.selectionStart = strPos;
        textel.selectionEnd = strPos;
    } else if (br === "ie") {
        textel.focus();
        const ieRange = document.selection.createRange();
        ieRange.moveStart('character', -textel.value.length);
        ieRange.moveStart('character', strPos);
        ieRange.moveEnd('character', 0);
        ieRange.select();
    }
    textel.scrollTop = scrollPos;
    validateSandbox(textel.value);
}

function triggerFileImport(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const content = e.target.result;
            if (file.name.endsWith('.json')) {
                try {
                    const parsed = JSON.parse(content);
                    
                    if (parsed.smriti_version !== "2.1" || parsed.template_version !== "1.0.0") {
                        alert("Template cannot be imported.\nInvalid or unsupported SMRITI template signature version.");
                        input.value = '';
                        return;
                    }
                    
                    const supported = ["ZPL", "TSPL", "EPL", "CPCL"];
                    const lang = (parsed.printer_language || "").toUpperCase();
                    if (!supported.includes(lang)) {
                        alert("Template cannot be imported.\nUnsupported printer language.");
                        input.value = '';
                        return;
                    }
                    
                    document.getElementById('design-name').value = parsed.template_name || '';
                    document.getElementById('design-size').value = parsed.label_size || '50x25';
                    document.getElementById('design-lang').value = lang;
                    document.getElementById('design-raw').value = parsed.raw_template || '';
                    
                    try {
                        window.BarcodeStudioState.designerMappings = parsed.custom_field_mappings_json ? JSON.parse(parsed.custom_field_mappings_json) : [];
                    } catch(e) {
                        window.BarcodeStudioState.designerMappings = [];
                    }
                    
                    window.BarcodeStudioState.canvasElements = parseLayoutJson(parsed.custom_visual_layout_json);
                    
                    renderMappingTable();
                    renderCanvas();
                    updatePropertiesInspector();
                    toast(`Template JSON imported successfully!`, 'success');
                    validateSandbox(parsed.raw_template || '');
                } catch(err) {
                    alert("Failed to parse template JSON: " + err.message);
                }
            } else {
                let lang = "ZPL";
                if (content.includes("SIZE ") || content.includes("GAP ") || content.includes("PRINT ")) {
                    lang = "TSPL";
                }
                
                const supported = ["ZPL", "TSPL", "EPL", "CPCL"];
                if (!supported.includes(lang)) {
                    alert("Template cannot be imported.\nUnsupported printer language.");
                    input.value = '';
                    return;
                }
                
                document.getElementById('design-raw').value = content;
                document.getElementById('design-lang').value = lang;
                window.BarcodeStudioState.canvasElements = [];
                renderCanvas();
                updatePropertiesInspector();
                toast(`PRN Template imported! Detected Language: ${lang}`, 'success');
                validateSandbox(content);
            }
            input.value = '';
        };
        reader.readAsText(file);
    }
}

function exportDesignerTemplate() {
    const name = document.getElementById('design-name').value.trim() || 'export';
    const raw = document.getElementById('design-raw').value;
    const size = document.getElementById('design-size').value;
    const lang = document.getElementById('design-lang').value;
    const mappings = getDesignerMappings();

    const data = {
        smriti_version: "2.1",
        template_version: "1.0.0",
        template_name: name,
        label_size: size,
        printer_language: lang,
        raw_template: raw,
        custom_field_mappings_json: mappings.length ? JSON.stringify(mappings) : null,
        custom_visual_layout_json: getLayoutJsonString()
    };

    const blob = new Blob([JSON.stringify(data, null, 4)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name.replace(/\s+/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast('Template configurations exported as JSON.', 'success');
}

function renderMappingTable() {
    const tbody = document.getElementById('designer-mapping-tbody');
    if (!tbody) return;
    
    const designerMappings = window.BarcodeStudioState.designerMappings;
    if (designerMappings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:var(--text-sub);">No variables mapped yet.</td></tr>';
        return;
    }

    tbody.innerHTML = designerMappings.map((m, idx) => `
        <tr>
            <td><input type="text" class="tbl-input" style="width:100%; font-family:monospace; font-size:11px;" value="${m.label_field}" onchange="updateMappingRow(${idx}, 'label_field', this.value)" placeholder="e.g. {token_name}"></td>
            <td><input type="text" class="tbl-input" style="width:100%; font-family:monospace; font-size:11px;" value="${m.erp_field}" onchange="updateMappingRow(${idx}, 'erp_field', this.value)" placeholder="e.g. custom_mrp"></td>
            <td style="text-align:right;"><button class="btn-del-row" onclick="removeMappingRow(${idx})" style="padding:4px;"><span class="material-symbols-outlined" style="font-size:14px;">close</span></button></td>
        </tr>
    `).join('');
}

function addNewMappingRow() {
    window.BarcodeStudioState.designerMappings.push({ label_field: '', erp_field: '' });
    renderMappingTable();
}

function updateMappingRow(idx, key, val) {
    window.BarcodeStudioState.designerMappings[idx][key] = val.trim();
    validateSandbox(document.getElementById('design-raw').value);
}

function removeMappingRow(idx) {
    window.BarcodeStudioState.designerMappings.splice(idx, 1);
    renderMappingTable();
    validateSandbox(document.getElementById('design-raw').value);
}

function getDesignerMappings() {
    return window.BarcodeStudioState.designerMappings.filter(m => m.label_field && m.erp_field);
}

// ── Visual Canvas Operations ──
function addVisualElement(type) {
    pushState();
    const id = type + '_' + Date.now();
    let newElem = {
        id: id,
        type: type,
        x: 10,
        y: 10,
        rotation: 0
    };
    
    if (type === 'text') {
        newElem.w = 30;
        newElem.h = 5;
        newElem.content = 'Text Element';
    } else if (type === 'barcode') {
        newElem.w = 40;
        newElem.h = 10;
        newElem.content = '{barcode}';
    } else if (type === 'qrcode') {
        newElem.w = 15;
        newElem.h = 15;
        newElem.content = '{barcode}';
    } else if (type === 'box') {
        newElem.w = 20;
        newElem.h = 10;
    } else if (type === 'bar') {
        newElem.w = 30;
        newElem.h = 1;
    } else if (type === 'image') {
        newElem.w = 15;
        newElem.h = 15;
        newElem.image_ref = '';
    }
    
    window.BarcodeStudioState.canvasElements.push(newElem);
    window.BarcodeStudioState.selectedElementId = id;
    renderCanvas();
    updatePropertiesInspector();
}

function deleteSelectedElement() {
    const selectedElementId = window.BarcodeStudioState.selectedElementId;
    if (selectedElementId) {
        pushState();
        window.BarcodeStudioState.canvasElements = window.BarcodeStudioState.canvasElements.filter(e => e.id !== selectedElementId);
        window.BarcodeStudioState.selectedElementId = null;
        renderCanvas();
        updatePropertiesInspector();
    }
}

function updateSelectedElementProperty(prop, value) {
    const selectedElementId = window.BarcodeStudioState.selectedElementId;
    const elem = window.BarcodeStudioState.canvasElements.find(e => e.id === selectedElementId);
    if (elem) {
        elem[prop] = value;
        const elDiv = document.getElementById(selectedElementId);
        if (elDiv) {
            if (prop === 'x') elDiv.style.left = (value * 8) + 'px';
            if (prop === 'y') elDiv.style.top = (value * 8) + 'px';
            if (prop === 'w') elDiv.style.width = (value * 8) + 'px';
            if (prop === 'h') elDiv.style.height = (value * 8) + 'px';
            if (prop === 'rotation') elDiv.style.transform = `rotate(${value}deg)`;
            
            if (prop === 'content') {
                const textSpan = elDiv.querySelector('.visual-elem-text');
                if (textSpan) textSpan.textContent = value;
            }
            if (prop === 'image_ref') {
                const imgSpan = elDiv.querySelector('.visual-elem-image');
                if (imgSpan) imgSpan.textContent = `IMG: ${value}`;
            }
        }
    }
}

function renderCanvas() {
    const canvas = document.getElementById('visual-canvas');
    if (!canvas) return;
    canvas.innerHTML = '';
    updateCanvasDimensions();
    
    const canvasElements = window.BarcodeStudioState.canvasElements;
    canvasElements.forEach(elem => {
        const div = document.createElement('div');
        div.id = elem.id;
        div.className = 'visual-elem' + (elem.id === window.BarcodeStudioState.selectedElementId ? ' selected' : '');
        div.style.left = (elem.x * 8) + 'px';
        div.style.top = (elem.y * 8) + 'px';
        div.style.width = (elem.w * 8) + 'px';
        div.style.height = (elem.h * 8) + 'px';
        div.style.transform = `rotate(${elem.rotation || 0}deg)`;
        
        if (elem.type === 'text') {
            div.innerHTML = `<span class="visual-elem-text">${esc(elem.content)}</span>`;
        } else if (elem.type === 'barcode') {
            div.innerHTML = `<div class="visual-elem-barcode"></div>`;
        } else if (elem.type === 'qrcode') {
            div.innerHTML = `<div class="visual-elem-qrcode"></div>`;
        } else if (elem.type === 'box') {
            div.innerHTML = `<div class="visual-elem-box"></div>`;
        } else if (elem.type === 'bar') {
            div.innerHTML = `<div class="visual-elem-bar"></div>`;
        } else if (elem.type === 'image') {
            div.innerHTML = `<div class="visual-elem-image" style="font-size: 8px; font-weight: bold;">IMG: ${esc(elem.image_ref || 'None')}</div>`;
        }
        
        div.addEventListener('mousedown', function(e) {
            e.stopPropagation();
            window.BarcodeStudioState.selectedElementId = elem.id;
            document.querySelectorAll('.visual-elem').forEach(el => el.classList.remove('selected'));
            div.classList.add('selected');
            updatePropertiesInspector();
            
            const startX = e.clientX;
            const startY = e.clientY;
            const elemStartX = elem.x;
            const elemStartY = elem.y;
            
            pushState();
            
            function onMouseMove(moveEvent) {
                const dx = moveEvent.clientX - startX;
                const dy = moveEvent.clientY - startY;
                elem.x = Math.max(0, parseFloat((elemStartX + dx / 8).toFixed(1)));
                elem.y = Math.max(0, parseFloat((elemStartY + dy / 8).toFixed(1)));
                
                div.style.left = (elem.x * 8) + 'px';
                div.style.top = (elem.y * 8) + 'px';
                
                const pxInput = document.getElementById('prop-x');
                const pyInput = document.getElementById('prop-y');
                if (pxInput) pxInput.value = elem.x;
                if (pyInput) pyInput.value = elem.y;
            }
            
            function onMouseUp() {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            }
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
        
        canvas.appendChild(div);
    });
}

function updatePropertiesInspector() {
    const form = document.getElementById('prop-editor-form');
    const noSel = document.getElementById('prop-no-selection');
    if (!form || !noSel) return;
    
    const selectedElementId = window.BarcodeStudioState.selectedElementId;
    if (!selectedElementId) {
        form.style.display = 'none';
        noSel.style.display = 'block';
        return;
    }
    
    const elem = window.BarcodeStudioState.canvasElements.find(e => e.id === selectedElementId);
    if (!elem) return;
    
    noSel.style.display = 'none';
    form.style.display = 'flex';
    
    document.getElementById('prop-elem-id').value = elem.id;
    document.getElementById('prop-elem-type').value = elem.type.toUpperCase();
    document.getElementById('prop-x').value = elem.x;
    document.getElementById('prop-y').value = elem.y;
    
    const wGroup = document.getElementById('prop-w-group');
    const hGroup = document.getElementById('prop-h-group');
    const contentGroup = document.getElementById('prop-content-group');
    const imageGroup = document.getElementById('prop-image-group');
    const rotationGroup = document.getElementById('prop-rotation-group');
    
    if (wGroup) wGroup.style.display = (elem.type === 'bar' && elem.h === 1) ? 'block' : (elem.type === 'bar' ? 'none' : 'block');
    if (hGroup) hGroup.style.display = elem.type === 'bar' ? 'none' : 'block';
    if (elem.w !== undefined) document.getElementById('prop-w').value = elem.w;
    if (elem.h !== undefined) document.getElementById('prop-h').value = elem.h;
    
    if (contentGroup) contentGroup.style.display = ['text', 'barcode', 'qrcode'].includes(elem.type) ? 'flex' : 'none';
    if (elem.content !== undefined) document.getElementById('prop-content').value = elem.content;
    
    if (imageGroup) imageGroup.style.display = elem.type === 'image' ? 'block' : 'none';
    if (elem.image_ref !== undefined) document.getElementById('prop-image-ref').value = elem.image_ref;
    
    document.getElementById('prop-rotation').value = elem.rotation || 0;
    
    const tokenChips = document.getElementById('prop-token-chips');
    if (tokenChips) {
        const chips = ["barcode", "item_code", "item_name", "brand", "mrp", "size", "color", "style", "pkd_date"];
        tokenChips.innerHTML = chips.map(c => `
            <span class="token-chip" onclick="insertTokenInContent('{${c}}')">{${c}}</span>
        `).join('');
    }
}

function insertTokenInContent(token) {
    const textel = document.getElementById('prop-content');
    if (textel) {
        const start = textel.selectionStart;
        const end = textel.selectionEnd;
        const val = textel.value;
        textel.value = val.substring(0, start) + token + val.substring(end);
        textel.selectionStart = textel.selectionEnd = start + token.length;
        textel.focus();
        updateSelectedElementProperty('content', textel.value);
    }
}

function openImageAssetSelector() {
    openModal('image-asset-modal');
    const listContainer = document.getElementById('image-asset-list');
    if (listContainer) {
        listContainer.innerHTML = '<div style="color:var(--text-sub); text-align:center; padding: 10px;">Loading assets...</div>';
        
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "File",
                filters: {"is_folder": 0, "is_image": 1},
                fields: ["name", "file_name", "file_url"],
                limit: 30
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    listContainer.innerHTML = '<div class="asset-grid">' + r.message.map(f => `
                        <div class="asset-item" onclick="selectImageAsset('${esc(f.name)}')">
                            <img src="${f.file_url}" alt="${esc(f.file_name)}">
                            <div class="asset-name">${esc(f.file_name)}</div>
                        </div>
                    `).join('') + '</div>';
                } else {
                    listContainer.innerHTML = '<div style="color:var(--text-sub); text-align:center; padding: 10px;">No images found in File Manager</div>';
                }
            }
        });
    }
}

function selectImageAsset(fileId) {
    const refInput = document.getElementById('prop-image-ref');
    if (refInput) {
        refInput.value = fileId;
        updateSelectedElementProperty('image_ref', fileId);
    }
    closeModal('image-asset-modal');
}

function compileVisualToPRN() {
    const lang = document.getElementById('design-lang').value;
    const dpi = window.BarcodeStudioState.activeDPI || 203;
    const canvasElements = window.BarcodeStudioState.canvasElements;
    
    function toDots(mm) {
        return Math.round(mm * dpi / 25.4);
    }
    
    let prn = '';
    
    if (lang === 'ZPL') {
        prn += '^XA\n';
        canvasElements.forEach(elem => {
            const dx = toDots(elem.x);
            const dy = toDots(elem.y);
            const dw = toDots(elem.w);
            const dh = toDots(elem.h);
            const rotZPL = elem.rotation === 90 ? 'R' : (elem.rotation === 180 ? 'I' : (elem.rotation === 270 ? 'B' : 'N'));
            
            if (elem.type === 'text') {
                prn += `^FO${dx},${dy}^A${rotZPL},24,14^FD${elem.content}^FS\n`;
            } else if (elem.type === 'barcode') {
                prn += `^FO${dx},${dy}^BC${rotZPL},${dh},Y,N,N^FD${elem.content}^FS\n`;
            } else if (elem.type === 'qrcode') {
                prn += `^FO${dx},${dy}^BQN,2,${Math.round(dw / 8 || 4)}^FDQA,${elem.content}^FS\n`;
            } else if (elem.type === 'box') {
                prn += `^FO${dx},${dy}^GB${dw},${dh},2^FS\n`;
            } else if (elem.type === 'bar') {
                prn += `^FO${dx},${dy}^GB${dw},${dh},${dh}^FS\n`;
            } else if (elem.type === 'image') {
                prn += `^FO${dx},${dy}^XG${elem.image_ref},1,1^FS\n`;
            }
        });
        prn += '^XZ';
    } else { // TSPL
        const sizeVal = document.getElementById('design-size').value;
        const parts = sizeVal.split('x');
        const mmW = parts[0] || '50';
        const mmH = parts[1] || '25';
        
        prn += `SIZE ${mmW} mm, ${mmH} mm\nGAP 3 mm, 0 mm\nDIRECTION 1\nCLS\n`;
        
        canvasElements.forEach(elem => {
            const dx = toDots(elem.x);
            const dy = toDots(elem.y);
            const dw = toDots(elem.w);
            const dh = toDots(elem.h);
            const rotTSPL = elem.rotation || 0;
            
            if (elem.type === 'text') {
                prn += `TEXT ${dx},${dy},"3",${rotTSPL},1,1,"${elem.content}"\n`;
            } else if (elem.type === 'barcode') {
                prn += `BARCODE ${dx},${dy},"128",${dh},1,${rotTSPL},2,4,"${elem.content}"\n`;
            } else if (elem.type === 'qrcode') {
                prn += `QRCODE ${dx},${dy},H,4,A,${rotTSPL},"${elem.content}"\n`;
            } else if (elem.type === 'box') {
                prn += `BOX ${dx},${dy},${dx + dw},${dy + dh},2\n`;
            } else if (elem.type === 'bar') {
                prn += `BAR ${dx},${dy},${dw},${dh}\n`;
            } else if (elem.type === 'image') {
                prn += `PUTBMP ${dx},${dy},"${elem.image_ref}"\n`;
            }
        });
        prn += 'PRINT 1,1';
    }
    return prn;
}

// ── Undo / Redo operations ──
function pushState() {
    const canvasElements = window.BarcodeStudioState.canvasElements;
    const undoStack = window.BarcodeStudioState.undoStack;
    if (undoStack.length >= 20) {
        undoStack.shift();
    }
    undoStack.push(JSON.stringify(canvasElements));
    window.BarcodeStudioState.redoStack = [];
    updateUndoRedoButtons();
}

function undoVisual() {
    const undoStack = window.BarcodeStudioState.undoStack;
    if (undoStack.length > 0) {
        const currentState = JSON.stringify(window.BarcodeStudioState.canvasElements);
        window.BarcodeStudioState.redoStack.push(currentState);
        const prevState = undoStack.pop();
        window.BarcodeStudioState.canvasElements = JSON.parse(prevState);
        window.BarcodeStudioState.selectedElementId = null;
        renderCanvas();
        updatePropertiesInspector();
        updateUndoRedoButtons();
    }
}

function redoVisual() {
    const redoStack = window.BarcodeStudioState.redoStack;
    if (redoStack.length > 0) {
        const nextState = redoStack.pop();
        window.BarcodeStudioState.undoStack.push(JSON.stringify(window.BarcodeStudioState.canvasElements));
        window.BarcodeStudioState.canvasElements = JSON.parse(nextState);
        window.BarcodeStudioState.selectedElementId = null;
        renderCanvas();
        updatePropertiesInspector();
        updateUndoRedoButtons();
    }
}

function updateUndoRedoButtons() {
    const undoBtn = document.getElementById('btn-undo');
    const redoBtn = document.getElementById('btn-redo');
    if (undoBtn) undoBtn.style.opacity = window.BarcodeStudioState.undoStack.length > 0 ? '1' : '0.4';
    if (redoBtn) redoBtn.style.opacity = window.BarcodeStudioState.redoStack.length > 0 ? '1' : '0.4';
}
