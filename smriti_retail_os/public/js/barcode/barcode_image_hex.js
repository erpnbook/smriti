/**
 * @file: smriti_retail_os/public/js/barcode/barcode_image_hex.js
 * @description: SMRITI Label Studio — Image to PRN / ZPL / TSPL Hex Code Generator
 * Converts PNG, JPG, SVG, WebP images to ZPL ^GF / ~DG, TSPL BITMAP, and Raw Hex code
 * for thermal barcode printers.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 2.2.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

window.SMRITI = window.SMRITI || {};
window.SMRITI.ImageHexConverter = (function () {
    "use strict";

    let currentImageData = null;
    let originalImageObj = null;

    /**
     * Converts a Canvas 2D Context image buffer into monochrome binary bytes and ZPL/TSPL Hex strings.
     * @param {HTMLCanvasElement} canvas
     * @param {number} threshold (0-255)
     * @param {boolean} invert
     * @param {string} mode - 'zpl_gf' | 'zpl_dg' | 'tspl_bitmap' | 'raw_hex'
     * @param {number} xPos
     * @param {number} yPos
     * @returns {object} { hexString, bytesPerRow, totalBytes, width, height, prnCommand }
     */
    function convertCanvasToHex(canvas, threshold = 128, invert = false, mode = 'zpl_gf', xPos = 20, yPos = 20) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const imageData = ctx.getImageData(0, 0, width, height);
        const data = imageData.data;

        const bytesPerRow = Math.ceil(width / 8);
        const totalBytes = bytesPerRow * height;

        let hexLines = [];
        let rawBytes = [];

        for (let y = 0; y < height; y++) {
            let rowHex = '';
            for (let byteIdx = 0; byteIdx < bytesPerRow; byteIdx++) {
                let byteVal = 0;
                for (let bitIdx = 0; bitIdx < 8; bitIdx++) {
                    const x = byteIdx * 8 + bitIdx;
                    if (x < width) {
                        const pixelIdx = (y * width + x) * 4;
                        const r = data[pixelIdx];
                        const g = data[pixelIdx + 1];
                        const b = data[pixelIdx + 2];
                        const a = data[pixelIdx + 3];

                        // Luminance algorithm
                        const luminance = (0.299 * r + 0.587 * g + 0.114 * b);
                        let isBlack = luminance < threshold && a > 30;
                        if (invert) isBlack = !isBlack;

                        if (isBlack) {
                            byteVal |= (1 << (7 - bitIdx));
                        }
                    }
                }
                const hexByte = byteVal.toString(16).padStart(2, '0').toUpperCase();
                rowHex += hexByte;
                rawBytes.push(hexByte);
            }
            hexLines.push(rowHex);
        }

        const fullHex = hexLines.join('');
        let prnCommand = '';

        if (mode === 'zpl_gf') {
            prnCommand = `^FO${xPos},${yPos}^GFA,${totalBytes},${totalBytes},${bytesPerRow},${fullHex}^FS`;
        } else if (mode === 'zpl_dg') {
            prnCommand = `~DGIMAGE.GRF,${totalBytes},${bytesPerRow},${fullHex}\n^FO${xPos},${yPos}^XGIMAGE.GRF,1,1^FS`;
        } else if (mode === 'tspl_bitmap') {
            prnCommand = `BITMAP ${xPos},${yPos},${bytesPerRow},${height},0,${fullHex}`;
        } else {
            // Raw hex format with spaces
            prnCommand = rawBytes.join(' ');
        }

        return {
            hexString: fullHex,
            bytesPerRow: bytesPerRow,
            totalBytes: totalBytes,
            width: width,
            height: height,
            prnCommand: prnCommand
        };
    }

    /**
     * Renders monochrome print preview canvas
     */
    function renderMonochromePreview(img, targetWidth, threshold, invert, previewCanvas) {
        if (!img) return null;
        const aspectRatio = img.height / img.width;
        const targetHeight = Math.round(targetWidth * aspectRatio);

        previewCanvas.width = targetWidth;
        previewCanvas.height = targetHeight;

        const ctx = previewCanvas.getContext('2d');
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, targetWidth, targetHeight);
        ctx.drawImage(img, 0, 0, targetWidth, targetHeight);

        const imgData = ctx.getImageData(0, 0, targetWidth, targetHeight);
        const d = imgData.data;

        for (let i = 0; i < d.length; i += 4) {
            const lum = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
            const alpha = d[i + 3];
            let isBlack = lum < threshold && alpha > 30;
            if (invert) isBlack = !isBlack;

            const val = isBlack ? 0 : 255;
            d[i] = val;
            d[i + 1] = val;
            d[i + 2] = val;
            d[i + 3] = 255;
        }

        ctx.putImageData(imgData, 0, 0);
        return previewCanvas;
    }

    /**
     * Opens Image-to-Hex Converter Modal
     */
    function openModal() {
        let modal = document.getElementById('image-hex-modal');
        if (!modal) {
            injectModalHTML();
            modal = document.getElementById('image-hex-modal');
        }
        modal.style.display = 'flex';
    }

    /**
     * Closes Image-to-Hex Converter Modal
     */
    function closeModal() {
        const modal = document.getElementById('image-hex-modal');
        if (modal) modal.style.display = 'none';
    }

    /**
     * Injects converter modal HTML into document body
     */
    function injectModalHTML() {
        const html = `
<div class="modal-backdrop" id="image-hex-modal" style="display:none;" onclick="if(event.target===this) window.SMRITI.ImageHexConverter.closeModal()">
    <div class="modal" onclick="event.stopPropagation()" style="max-width: 820px; width: 95%;">
        <div class="modal-header" style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); padding-bottom:12px;">
            <div class="modal-title" style="font-family:'Outfit',sans-serif; font-weight:700; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
                <span class="material-symbols-outlined" style="color:var(--primary-lt);">image</span> Image to PRN / Barcode Hex Code Generator
            </div>
            <button class="modal-close" onclick="window.SMRITI.ImageHexConverter.closeModal()" style="background:none; border:none; color:var(--text); font-size:24px; cursor:pointer;">&times;</button>
        </div>
        
        <div class="modal-body" style="padding:16px 0; display:flex; flex-direction:column; gap:16px;">
            <!-- Drag & Drop Upload Box -->
            <div id="hex-drop-zone" style="border:2px dashed var(--border2); border-radius:8px; padding:24px; text-align:center; background:rgba(0,0,0,0.02); cursor:pointer; transition:all 0.2s;"
                 onclick="document.getElementById('hex-file-input').click()">
                <span class="material-symbols-outlined" style="font-size:42px; color:var(--primary-lt);">cloud_upload</span>
                <div style="font-weight:600; margin-top:6px; color:var(--text);">Click or Drag & Drop Image Here</div>
                <div style="font-size:0.78rem; color:var(--text-muted); margin-top:4px;">Supports PNG, JPG, JPEG, SVG, WebP, GIF, BMP</div>
                <input type="file" id="hex-file-input" accept="image/*" style="display:none;" onchange="window.SMRITI.ImageHexConverter.handleFileSelect(event)">
            </div>

            <!-- Controls Grid -->
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; background:var(--bg2); padding:14px; border-radius:8px; border:1px solid var(--border);">
                <div class="form-group">
                    <label class="form-label" style="font-size:0.75rem; font-weight:600; margin-bottom:4px; display:block;">Protocol / Format</label>
                    <select id="hex-format-select" class="form-input" style="width:100%; padding:6px 10px; font-size:0.85rem;" onchange="window.SMRITI.ImageHexConverter.updateConversion()">
                        <option value="zpl_gf" selected>ZPL ^GF (Graphic Field)</option>
                        <option value="zpl_dg">ZPL ~DG (Download Graphic)</option>
                        <option value="tspl_bitmap">TSPL BITMAP Command</option>
                        <option value="raw_hex">Raw Hex String</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label" style="font-size:0.75rem; font-weight:600; margin-bottom:4px; display:block;">Image Width (px)</label>
                    <input type="number" id="hex-width-input" class="form-input" value="160" min="16" max="1000" step="8" style="width:100%; padding:6px 10px; font-size:0.85rem;" onchange="window.SMRITI.ImageHexConverter.updateConversion()">
                </div>

                <div class="form-group">
                    <label class="form-label" style="font-size:0.75rem; font-weight:600; margin-bottom:4px; display:block;">Threshold (0-255): <span id="threshold-val">128</span></label>
                    <input type="range" id="hex-threshold-input" min="10" max="245" value="128" style="width:100%; margin-top:6px;" oninput="document.getElementById('threshold-val').textContent=this.value; window.SMRITI.ImageHexConverter.updateConversion()">
                </div>

                <div class="form-group" style="display:flex; flex-direction:column; justify-content:center;">
                    <label style="font-size:0.8rem; font-weight:600; display:flex; align-items:center; gap:6px; cursor:pointer; margin-top:16px;">
                        <input type="checkbox" id="hex-invert-chk" onchange="window.SMRITI.ImageHexConverter.updateConversion()"> Invert Monochrome
                    </label>
                </div>
            </div>

            <!-- Preview & Hex Output Side-by-Side -->
            <div style="display:grid; grid-template-columns: 220px 1fr; gap:16px;">
                <!-- Preview Canvas Box -->
                <div style="border:1px solid var(--border); border-radius:8px; padding:12px; text-align:center; background:var(--card); display:flex; flex-direction:column; align-items:center; justify-content:center;">
                    <div style="font-size:0.75rem; font-weight:700; color:var(--text-muted); margin-bottom:8px;">THERMAL PRINT PREVIEW</div>
                    <canvas id="hex-preview-canvas" style="max-width:100%; max-height:160px; border:1px solid var(--border2); background:#fff; object-fit:contain;"></canvas>
                    <div id="hex-meta-info" style="font-size:0.72rem; color:var(--text-sub); margin-top:8px;">Upload an image</div>
                </div>

                <!-- Output Code Textarea -->
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.78rem; font-weight:700; color:var(--text-muted);">GENERATED PRN / BARCODE HEX CODE</span>
                        <button class="topbtn" onclick="window.SMRITI.ImageHexConverter.copyToClipboard()" style="padding:3px 10px; font-size:0.78rem;">
                            <span class="material-symbols-outlined" style="font-size:14px;">content_copy</span> Copy Code
                        </button>
                    </div>
                    <textarea id="hex-output-text" readonly style="width:100%; height:160px; font-family:'JetBrains Mono', monospace; font-size:0.75rem; padding:10px; background:var(--bg2); border:1px solid var(--border); border-radius:6px; color:var(--primary-lt); resize:none; white-space:pre-wrap; word-break:break-all;"></textarea>
                </div>
            </div>
        </div>

        <div class="modal-footer" style="display:flex; justify-content:flex-end; gap:8px; border-top:1px solid var(--border); padding-top:12px;">
            <button class="topbtn" onclick="window.SMRITI.ImageHexConverter.closeModal()">Close</button>
            <button class="btn-search" style="padding:6px 16px;" onclick="window.SMRITI.ImageHexConverter.insertIntoPRNEditor()">
                <span class="material-symbols-outlined" style="font-size:16px;">add_code</span> Insert into PRN Template
            </button>
        </div>
    </div>
</div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);

        // Setup Drag & Drop handlers
        const dropZone = document.getElementById('hex-drop-zone');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = 'var(--primary)';
                dropZone.style.background = 'rgba(37,99,235,0.06)';
            });
            dropZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = 'var(--border2)';
                dropZone.style.background = 'rgba(0,0,0,0.02)';
            });
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = 'var(--border2)';
                dropZone.style.background = 'rgba(0,0,0,0.02)';
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    processFile(e.dataTransfer.files[0]);
                }
            });
        }
    }

    function handleFileSelect(evt) {
        if (evt.target.files && evt.target.files[0]) {
            processFile(evt.target.files[0]);
        }
    }

    function processFile(file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = new Image();
            img.onload = function () {
                originalImageObj = img;
                updateConversion();
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    function updateConversion() {
        if (!originalImageObj) return;

        const targetWidth = parseInt(document.getElementById('hex-width-input').value, 10) || 160;
        const threshold = parseInt(document.getElementById('hex-threshold-input').value, 10) || 128;
        const invert = document.getElementById('hex-invert-chk').checked;
        const format = document.getElementById('hex-format-select').value;
        const previewCanvas = document.getElementById('hex-preview-canvas');

        renderMonochromePreview(originalImageObj, targetWidth, threshold, invert, previewCanvas);

        const converted = convertCanvasToHex(previewCanvas, threshold, invert, format, 20, 20);

        document.getElementById('hex-output-text').value = converted.prnCommand;
        document.getElementById('hex-meta-info').textContent = `${converted.width} × ${converted.height} px | ${converted.bytesPerRow} bytes/row | Total: ${converted.totalBytes} bytes`;
        currentImageData = converted;
    }

    function openModal() {
        let modal = document.getElementById('image-hex-modal');
        if (!modal) {
            injectModalHTML();
            modal = document.getElementById('image-hex-modal');
        }
        if (modal) {
            modal.classList.add('open');
            modal.style.display = 'flex';
        }
    }

    function closeModal() {
        const modal = document.getElementById('image-hex-modal');
        if (modal) {
            modal.classList.remove('open');
            modal.style.display = 'none';
        }
    }

    function copyToClipboard() {
        const text = document.getElementById('hex-output-text').value;
        if (!text) return;
        navigator.clipboard.writeText(text).then(() => {
            if (window.toast) {
                window.toast('PRN Hex Code copied to clipboard!', 'success');
            } else {
                alert('Hex Code copied!');
            }
        });
    }

    function insertIntoPRNEditor() {
        const prnCmd = document.getElementById('hex-output-text').value;
        if (!prnCmd) return;

        let applied = false;
        // Check if raw PRN text editor is active
        const prnEditor = document.getElementById('prn-raw-editor') || document.getElementById('design-raw-prn');
        if (prnEditor) {
            prnEditor.value += '\n' + prnCmd;
            applied = true;
            if (window.toast) window.toast('Inserted Hex code into PRN Editor!', 'success');
        }

        // Check if a canvas element is selected in Visual Designer
        if (window.BarcodeStudioState && window.BarcodeStudioState.selectedElement) {
            const selected = window.BarcodeStudioState.selectedElement;
            if (selected.type === 'image' && currentImageData) {
                selected.image_hex = currentImageData.hexString;
                selected.image_bytes = currentImageData.totalBytes;
                selected.image_row_bytes = currentImageData.bytesPerRow;
                if (window.updateSelectedElementProperty) {
                    window.updateSelectedElementProperty('image_hex', currentImageData.hexString);
                }
                if (window.renderVisualCanvas) {
                    window.renderVisualCanvas();
                }
                applied = true;
                if (window.toast) window.toast('Applied Hex Code to selected image element!', 'success');
            }
        }

        if (!applied) {
            copyToClipboard();
        }
        closeModal();
    }

    const API = {
        openModal: openModal,
        closeModal: closeModal,
        handleFileSelect: handleFileSelect,
        updateConversion: updateConversion,
        copyToClipboard: copyToClipboard,
        insertIntoPRNEditor: insertIntoPRNEditor
    };

    window.openImageHexConverterModal = openModal;
    return API;
})();
