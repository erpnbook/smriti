/**
 * @file:    smriti_retail_os/public/js/label/label_designer.js
 * @desc:    Interactive HTML5 Canvas Designer for SMRITI Label Studio.
 *           Handles element add/delete, QR/Barcode/Line/Text rendering,
 *           canvas resize, drag-move, drag-resize, undo/redo.
 * @author:  Jawahar R. Mallah
 */

(function() {
    'use strict';

    const MM_TO_PX = 3.78; // 96 DPI approximation

    // ── Shared document state used by designer ───────────────────────────────
    window.LabelStudioState = Object.assign(window.LabelStudioState || {}, {
        document: {
            elements: []   // shared with label_core.js; starts empty
        },
        canvas: {
            width:  100,   // mm
            height:  50,   // mm
            unit:   'mm'
        },
        viewport: {
            zoom:  1.0,
            panX:  0,
            panY:  0
        },
        selection: {
            activeElementId: null,
            dragMode:        null,   // 'move' | 'resize'
            resizeHandle:    null,
            dragStartX:      0,
            dragStartY:      0,
            elemStartX:      0,
            elemStartY:      0,
            elemStartWidth:  0,
            elemStartHeight: 0
        },
        history: {
            undo: [],
            redo: []
        },
        preferences: {
            snap:     true,
            grid:     true,
            gridSize: 5     // mm
        },
        ui: {
            inspectorOpen: true
        }
    });

    // ── Designer Class ───────────────────────────────────────────────────────
    class LabelDesigner {
        constructor(canvasId) {
            this.canvas = document.getElementById(canvasId);
            if (!this.canvas) return;
            this.ctx = this.canvas.getContext('2d');
            this._initEvents();
            this.redraw();
        }

        // ── Event wiring ─────────────────────────────────────────────────────
        _initEvents() {
            this.canvas.addEventListener('mousedown', this._onMouseDown.bind(this));
            this.canvas.addEventListener('mousemove', this._onMouseMove.bind(this));
            document.addEventListener('mouseup',     this._onMouseUp.bind(this));

            // Keep legacy event name working
            window.LabelEvents.on('studio:ready',   () => this.redraw());

            window.LabelEvents.on('grid:toggle', val => {
                window.LabelStudioState.preferences.grid = val;
                this.redraw();
            });
            window.LabelEvents.on('grid:size', val => {
                window.LabelStudioState.preferences.gridSize = parseInt(val) || 5;
                this.redraw();
            });
            window.LabelEvents.on('zoom:change', val => {
                window.LabelStudioState.viewport.zoom = (val === 'fit') ? 1.0 : (parseFloat(val) || 1.0);
                this.redraw();
            });
            window.LabelEvents.on('history:undo', () => this._undo());
            window.LabelEvents.on('history:redo', () => this._redo());

            // ── Element lifecycle events ──────────────────────────────────────
            window.LabelEvents.on('element:add', ({ type, overrides = {} } = {}) => {
                const el = window.LabelElementFactory.create(type, overrides);
                this._pushHistory();
                window.LabelStudioState.document.elements.push(el);
                window.LabelStudioState.selection.activeElementId = el.id;
                window.LabelEvents.emit('element:selected', el);
                this.redraw();
            });

            window.LabelEvents.on('element:delete', () => {
                const state = window.LabelStudioState;
                if (!state.selection.activeElementId) return;
                this._pushHistory();
                state.document.elements = state.document.elements.filter(
                    el => el.id !== state.selection.activeElementId
                );
                state.selection.activeElementId = null;
                window.LabelEvents.emit('element:unselected');
                this.redraw();
            });

            // canvas:resize — from label size preset selector
            window.LabelEvents.on('canvas:resize', ({ width_mm, height_mm }) => {
                const state = window.LabelStudioState;
                state.canvas.width  = parseFloat(width_mm)  || state.canvas.width;
                state.canvas.height = parseFloat(height_mm) || state.canvas.height;
                this.redraw();
            });

            // element:load_item — from "Load from SKU" panel
            window.LabelEvents.on('element:load_item', item => {
                const state = window.LabelStudioState;
                this._pushHistory();

                // Update existing elements whose source matches known item fields
                state.document.elements.forEach(el => {
                    if (el.source === 'item_name')  el.content = item.item_name || el.content;
                    if (el.source === 'barcode')    el.content = item.barcode   || el.content;
                    if (el.source === 'mrp')        el.content = `MRP: ₹${item.mrp}` || el.content;
                    if (el.source === 'item_code')  el.content = item.item_code  || el.content;
                    if (el.source === 'hsn_code')   el.content = `HSN: ${item.hsn_code}` || el.content;
                    if (el.source === 'brand')      el.content = item.brand      || el.content;
                });

                // If canvas is empty, scaffold a standard retail label layout
                if (state.document.elements.length === 0) {
                    const elements = [
                        window.LabelElementFactory.create('Text',    { x: 5, y: 4,  width: 90, height: 8,  content: item.item_name || 'Product Name', source: 'item_name', font_size: 9 }),
                        window.LabelElementFactory.create('Text',    { x: 5, y: 14, width: 50, height: 6,  content: item.brand || '', source: 'brand', font_size: 7 }),
                        window.LabelElementFactory.create('Text',    { x: 5, y: 21, width: 40, height: 7,  content: `MRP: ₹${item.mrp}`, source: 'mrp', font_size: 8 }),
                        window.LabelElementFactory.create('Barcode', { x: 5, y: 30, width: 80, height: 16, content: item.barcode || item.item_code, source: 'barcode' }),
                    ];
                    elements.forEach(el => state.document.elements.push(el));
                }

                this.redraw();
                window.LabelEvents.emit('item:loaded', item);
            });
        }

        // ── Render ───────────────────────────────────────────────────────────
        redraw() {
            const state = window.LabelStudioState;
            const zoom  = state.viewport.zoom;
            const w_px  = state.canvas.width  * MM_TO_PX * zoom;
            const h_px  = state.canvas.height * MM_TO_PX * zoom;

            this.canvas.width  = w_px;
            this.canvas.height = h_px;
            this.ctx.clearRect(0, 0, w_px, h_px);

            // Label background
            this.ctx.fillStyle = '#ffffff';
            this.ctx.fillRect(0, 0, w_px, h_px);

            // Label border
            this.ctx.strokeStyle = '#cbd5e1';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(0, 0, w_px, h_px);

            if (state.preferences.grid) this._drawGrid(w_px, h_px, zoom);

            // Draw elements sorted by zIndex
            [...state.document.elements]
                .sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
                .forEach(el => { if (el.visible) this._drawElement(el, zoom); });

            // Selection outline
            if (state.selection.activeElementId) {
                const active = state.document.elements.find(el => el.id === state.selection.activeElementId);
                if (active && active.visible) this._drawSelectionOutline(active, zoom);
            }
        }

        _drawGrid(w_px, h_px, zoom) {
            const step_px = window.LabelStudioState.preferences.gridSize * MM_TO_PX * zoom;
            this.ctx.strokeStyle = '#e2e8f0';
            this.ctx.lineWidth = 0.5;
            for (let x = 0; x < w_px; x += step_px) {
                this.ctx.beginPath(); this.ctx.moveTo(x, 0); this.ctx.lineTo(x, h_px); this.ctx.stroke();
            }
            for (let y = 0; y < h_px; y += step_px) {
                this.ctx.beginPath(); this.ctx.moveTo(0, y); this.ctx.lineTo(w_px, y); this.ctx.stroke();
            }
        }

        _drawElement(el, zoom) {
            const x = el.x * MM_TO_PX * zoom;
            const y = el.y * MM_TO_PX * zoom;
            const w = el.width  * MM_TO_PX * zoom;
            const h = el.height * MM_TO_PX * zoom;
            const ctx = this.ctx;

            ctx.save();
            ctx.translate(x + w / 2, y + h / 2);
            ctx.rotate((el.rotation * Math.PI) / 180);
            ctx.translate(-(x + w / 2), -(y + h / 2));

            if (el.type === 'Barcode') {
                // Barcode simulation — black bars pattern
                ctx.fillStyle = '#000000';
                ctx.fillRect(x, y, w, h - 6);
                ctx.fillStyle = '#ffffff';
                for (let i = 4; i < w - 4; i += 6) ctx.fillRect(x + i, y, 2, h - 6);
                // Human-readable text below barcode
                ctx.fillStyle = '#000000';
                ctx.font = `${Math.max(7, 8 * zoom)}px monospace`;
                ctx.textAlign = 'center';
                ctx.fillText(el.content || '', x + w / 2, y + h - 1);
                ctx.textAlign = 'left';

            } else if (el.type === 'QRCode') {
                // QR Code placeholder grid
                const cell = Math.max(2, Math.floor(w / 10));
                ctx.fillStyle = '#000000';
                ctx.fillRect(x, y, w, h);
                ctx.fillStyle = '#ffffff';
                // Simulate QR pattern with a simple grid
                for (let r = 1; r < 9; r++) {
                    for (let c = 1; c < 9; c++) {
                        if ((r + c) % 2 === 0) {
                            ctx.fillRect(x + c * cell, y + r * cell, cell - 1, cell - 1);
                        }
                    }
                }
                // QR finder squares
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2;
                ctx.strokeRect(x + 2, y + 2, cell * 3, cell * 3);
                // Label below
                ctx.fillStyle = '#000000';
                ctx.font = `${Math.max(6, 7 * zoom)}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.fillText('QR', x + w / 2, y + h + 8);
                ctx.textAlign = 'left';

            } else if (el.type === 'Line') {
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = Math.max(1, h);
                ctx.beginPath();
                ctx.moveTo(x, y + h / 2);
                ctx.lineTo(x + w, y + h / 2);
                ctx.stroke();

            } else {
                // Text
                const fs = Math.max(7, (el.font_size || 8) * MM_TO_PX * zoom * 0.55);
                ctx.fillStyle = '#000000';
                ctx.font = `${fs}px Arial, sans-serif`;
                ctx.textBaseline = 'top';
                ctx.fillText(el.content || '', x + 2, y + 2);
            }
            ctx.restore();
        }

        _drawSelectionOutline(el, zoom) {
            const x = el.x * MM_TO_PX * zoom;
            const y = el.y * MM_TO_PX * zoom;
            const w = el.width  * MM_TO_PX * zoom;
            const h = el.height * MM_TO_PX * zoom;
            this.ctx.strokeStyle = '#7c3aed';
            this.ctx.lineWidth = 1.5;
            this.ctx.setLineDash([4, 2]);
            this.ctx.strokeRect(x, y, w, h);
            this.ctx.setLineDash([]);
            // Resize handle (bottom-right)
            this.ctx.fillStyle = '#7c3aed';
            this.ctx.fillRect(x + w - 5, y + h - 5, 8, 8);
        }

        // ── Mouse interactions ────────────────────────────────────────────────
        _onMouseDown(e) {
            const state = window.LabelStudioState;
            const zoom  = state.viewport.zoom;
            const rect  = this.canvas.getBoundingClientRect();
            const mX    = (e.clientX - rect.left)  / (MM_TO_PX * zoom);
            const mY    = (e.clientY - rect.top)   / (MM_TO_PX * zoom);

            // Check resize handle first
            if (state.selection.activeElementId) {
                const el = state.document.elements.find(item => item.id === state.selection.activeElementId);
                if (el && !el.locked) {
                    const rX = el.x + el.width;
                    const rY = el.y + el.height;
                    const tol = 6 / (MM_TO_PX * zoom);
                    if (Math.abs(mX - rX) <= tol && Math.abs(mY - rY) <= tol) {
                        this._pushHistory();
                        state.selection.dragMode        = 'resize';
                        state.selection.dragStartX      = e.clientX;
                        state.selection.dragStartY      = e.clientY;
                        state.selection.elemStartWidth  = el.width;
                        state.selection.elemStartHeight = el.height;
                        return;
                    }
                }
            }

            // Hit-test elements (highest zIndex first)
            const sorted   = [...state.document.elements].sort((a, b) => (b.zIndex || 0) - (a.zIndex || 0));
            const selected = sorted.find(el =>
                el.visible && mX >= el.x && mX <= el.x + el.width && mY >= el.y && mY <= el.y + el.height
            );

            if (selected) {
                state.selection.activeElementId = selected.id;
                window.LabelEvents.emit('element:selected', selected);
                if (!selected.locked) {
                    this._pushHistory();
                    state.selection.dragMode   = 'move';
                    state.selection.dragStartX = e.clientX;
                    state.selection.dragStartY = e.clientY;
                    state.selection.elemStartX = selected.x;
                    state.selection.elemStartY = selected.y;
                }
            } else {
                state.selection.activeElementId = null;
                window.LabelEvents.emit('element:unselected');
            }
            this.redraw();
        }

        _onMouseMove(e) {
            const state = window.LabelStudioState;
            const mode  = state.selection.dragMode;
            if (!mode || !state.selection.activeElementId) return;
            const el = state.document.elements.find(item => item.id === state.selection.activeElementId);
            if (!el || el.locked) return;

            const zoom = state.viewport.zoom;
            const dX   = (e.clientX - state.selection.dragStartX) / (MM_TO_PX * zoom);
            const dY   = (e.clientY - state.selection.dragStartY) / (MM_TO_PX * zoom);
            const snap = state.preferences.snap;
            const gs   = state.preferences.gridSize;

            if (mode === 'move') {
                let nX = state.selection.elemStartX + dX;
                let nY = state.selection.elemStartY + dY;
                if (snap) { nX = Math.round(nX / gs) * gs; nY = Math.round(nY / gs) * gs; }
                el.x = Math.max(0, Math.min(state.canvas.width  - el.width,  nX));
                el.y = Math.max(0, Math.min(state.canvas.height - el.height, nY));
            } else if (mode === 'resize') {
                let nW = state.selection.elemStartWidth  + dX;
                let nH = state.selection.elemStartHeight + dY;
                if (snap) { nW = Math.round(nW / gs) * gs; nH = Math.round(nH / gs) * gs; }
                el.width  = Math.max(5, Math.min(state.canvas.width  - el.x, nW));
                el.height = Math.max(1, Math.min(state.canvas.height - el.y, nH));
            }
            window.LabelEvents.emit('element:changed', el);
            this.redraw();
        }

        _onMouseUp() {
            window.LabelStudioState.selection.dragMode = null;
        }

        // ── History ───────────────────────────────────────────────────────────
        _pushHistory() {
            const state    = window.LabelStudioState;
            const snapshot = JSON.stringify(state.document.elements);
            state.history.undo.push(snapshot);
            state.history.redo = [];
        }

        _undo() {
            const state = window.LabelStudioState;
            if (!state.history.undo.length) return;
            state.history.redo.push(JSON.stringify(state.document.elements));
            state.document.elements = JSON.parse(state.history.undo.pop());
            if (state.selection.activeElementId) {
                const el = state.document.elements.find(item => item.id === state.selection.activeElementId);
                if (el) window.LabelEvents.emit('element:selected', el);
                else { state.selection.activeElementId = null; window.LabelEvents.emit('element:unselected'); }
            }
            this.redraw();
        }

        _redo() {
            const state = window.LabelStudioState;
            if (!state.history.redo.length) return;
            state.history.undo.push(JSON.stringify(state.document.elements));
            state.document.elements = JSON.parse(state.history.redo.pop());
            this.redraw();
        }
    }

    window.LabelDesigner = LabelDesigner;

    document.addEventListener('DOMContentLoaded', () => {
        const designer = new LabelDesigner('labelCanvas');
        window.LabelEvents.emit('designer:ready', designer);
    });

})();
