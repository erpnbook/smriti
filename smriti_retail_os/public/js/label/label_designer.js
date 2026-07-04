/**
 * @file:    smriti_retail_os/public/js/label/label_designer.js
 * @desc:    Interactive HTML5 Canvas Designer for SMRITI layouts.
 * @author:  Jawahar R. Mallah
 */

(function() {
    'use strict';

    // 1. Initial State Alignment
    window.LabelStudioState = {
        document: {
            elements: [
                { id: "txt_1", type: "Text", x: 10, y: 10, width: 60, height: 10, rotation: 0, locked: false, visible: true, zIndex: 1, content: "SMRITI OS" },
                { id: "bc_1", type: "Barcode", x: 10, y: 25, width: 80, height: 18, rotation: 0, locked: false, visible: true, zIndex: 2, content: "12345678" }
            ]
        },
        canvas: {
            width: 100, // mm
            height: 50, // mm
            unit: "mm"
        },
        viewport: {
            zoom: 1.0, // scale factor
            panX: 0,
            panY: 0
        },
        selection: {
            activeElementId: null,
            dragMode: null, // "move" or "resize"
            resizeHandle: null,
            dragStartX: 0,
            dragStartY: 0,
            elemStartX: 0,
            elemStartY: 0,
            elemStartWidth: 0,
            elemStartHeight: 0
        },
        history: {
            undo: [],
            redo: []
        },
        preferences: {
            snap: true,
            grid: true,
            gridSize: 5 // mm
        },
        ui: {
            inspectorOpen: true
        }
    };

    const MM_TO_PX = 3.78; // 96 DPI approximation (3.779527559 px per mm)

    class LabelDesigner {
        constructor(canvasId) {
            this.canvas = document.getElementById(canvasId);
            if (!this.canvas) return;
            this.ctx = this.canvas.getContext("2d");
            this.initEvents();
            this.redraw();
        }

        initEvents() {
            this.canvas.addEventListener("mousedown", this.onMouseDown.bind(this));
            this.canvas.addEventListener("mousemove", this.onMouseMove.bind(this));
            document.addEventListener("mouseup", this.onMouseUp.bind(this));

            window.LabelEvents.on("studio:ready", () => this.redraw());
            window.LabelEvents.on("grid:toggle", (val) => {
                window.LabelStudioState.preferences.grid = val;
                this.redraw();
            });
            window.LabelEvents.on("grid:size", (val) => {
                window.LabelStudioState.preferences.gridSize = parseInt(val) || 5;
                this.redraw();
            });
            window.LabelEvents.on("zoom:change", (val) => {
                if (val === "fit") {
                    window.LabelStudioState.viewport.zoom = 1.0;
                } else {
                    window.LabelStudioState.viewport.zoom = parseFloat(val) || 1.0;
                }
                this.redraw();
            });
            window.LabelEvents.on("history:undo", () => this.undo());
            window.LabelEvents.on("history:redo", () => this.redo());
        }

        redraw() {
            const state = window.LabelStudioState;
            const zoom = state.viewport.zoom;

            // Resize canvas resolution according to dimensions and zoom scale
            const w_px = state.canvas.width * MM_TO_PX * zoom;
            const h_px = state.canvas.height * MM_TO_PX * zoom;
            this.canvas.width = w_px;
            this.canvas.height = h_px;

            this.ctx.clearRect(0, 0, w_px, h_px);
            this.ctx.fillStyle = "#ffffff";
            this.ctx.fillRect(0, 0, w_px, h_px);

            if (state.preferences.grid) {
                this.drawGrid(w_px, h_px, zoom);
            }

            // Draw elements ordered by zIndex
            const sorted = [...state.document.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
            sorted.forEach(el => {
                if (el.visible) {
                    this.drawElement(el, zoom);
                }
            });

            // Draw Selection Highlight
            if (state.selection.activeElementId) {
                const active = state.document.elements.find(el => el.id === state.selection.activeElementId);
                if (active && active.visible) {
                    this.drawSelectionOutline(active, zoom);
                }
            }
        }

        drawGrid(w_px, h_px, zoom) {
            const state = window.LabelStudioState;
            const step_px = state.preferences.gridSize * MM_TO_PX * zoom;
            this.ctx.strokeStyle = "#e2e8f0";
            this.ctx.lineWidth = 0.5;

            // Columns
            for (let x = 0; x < w_px; x += step_px) {
                this.ctx.beginPath();
                this.ctx.moveTo(x, 0);
                this.ctx.lineTo(x, h_px);
                this.ctx.stroke();
            }
            // Rows
            for (let y = 0; y < h_px; y += step_px) {
                this.ctx.beginPath();
                this.ctx.moveTo(0, y);
                this.ctx.lineTo(w_px, y);
                this.ctx.stroke();
            }
        }

        drawElement(el, zoom) {
            const x = el.x * MM_TO_PX * zoom;
            const y = el.y * MM_TO_PX * zoom;
            const w = el.width * MM_TO_PX * zoom;
            const h = el.height * MM_TO_PX * zoom;

            this.ctx.save();
            this.ctx.translate(x + w / 2, y + h / 2);
            this.ctx.rotate((el.rotation * Math.PI) / 180);
            this.ctx.translate(-(x + w / 2), -(y + h / 2));

            if (el.type === "Barcode") {
                this.ctx.fillStyle = "#000000";
                this.ctx.fillRect(x, y, w, h - 4);
                this.ctx.fillStyle = "#ffffff";
                // Simple barcode pattern lines simulation
                for (let i = 4; i < w - 4; i += 6) {
                    this.ctx.fillRect(x + i, y, 2, h - 4);
                }
            } else {
                this.ctx.fillStyle = "#1e293b";
                this.ctx.font = `${Math.max(8, 12 * zoom)}px Arial`;
                this.ctx.textBaseline = "top";
                this.ctx.fillText(el.content || "", x + 4, y + 2);
            }
            this.ctx.restore();
        }

        drawSelectionOutline(el, zoom) {
            const x = el.x * MM_TO_PX * zoom;
            const y = el.y * MM_TO_PX * zoom;
            const w = el.width * MM_TO_PX * zoom;
            const h = el.height * MM_TO_PX * zoom;

            this.ctx.strokeStyle = "#2563eb";
            this.ctx.lineWidth = 1.5;
            this.ctx.strokeRect(x, y, w, h);

            // Draw Resize Handles (Bottom Right corner resize handle)
            this.ctx.fillStyle = "#2563eb";
            this.ctx.fillRect(x + w - 6, y + h - 6, 8, 8);
        }

        onMouseDown(e) {
            const state = window.LabelStudioState;
            const zoom = state.viewport.zoom;
            const rect = this.canvas.getBoundingClientRect();
            const mX = (e.clientX - rect.left) / (MM_TO_PX * zoom);
            const mY = (e.clientY - rect.top) / (MM_TO_PX * zoom);

            // 1. Check if resizing handle clicked
            if (state.selection.activeElementId) {
                const el = state.document.elements.find(item => item.id === state.selection.activeElementId);
                if (el && !el.locked) {
                    const rX = el.x + el.width;
                    const rY = el.y + el.height;
                    const tolerance = 6 / (MM_TO_PX * zoom);
                    if (Math.abs(mX - rX) <= tolerance && Math.abs(mY - rY) <= tolerance) {
                        this.pushHistoryState();
                        state.selection.dragMode = "resize";
                        state.selection.dragStartX = e.clientX;
                        state.selection.dragStartY = e.clientY;
                        state.selection.elemStartWidth = el.width;
                        state.selection.elemStartHeight = el.height;
                        return;
                    }
                }
            }

            // 2. Select element (Top-down order)
            const sorted = [...state.document.elements].sort((a, b) => (b.zIndex || 0) - (a.zIndex || 0));
            const selected = sorted.find(el => {
                return (
                    el.visible &&
                    mX >= el.x &&
                    mX <= el.x + el.width &&
                    mY >= el.y &&
                    mY <= el.y + el.height
                );
            });

            if (selected) {
                state.selection.activeElementId = selected.id;
                window.LabelEvents.emit("element:selected", selected);

                if (!selected.locked) {
                    this.pushHistoryState();
                    state.selection.dragMode = "move";
                    state.selection.dragStartX = e.clientX;
                    state.selection.dragStartY = e.clientY;
                    state.selection.elemStartX = selected.x;
                    state.selection.elemStartY = selected.y;
                }
            } else {
                state.selection.activeElementId = null;
                window.LabelEvents.emit("element:unselected");
            }
            this.redraw();
        }

        onMouseMove(e) {
            const state = window.LabelStudioState;
            const mode = state.selection.dragMode;
            if (!mode || !state.selection.activeElementId) return;

            const el = state.document.elements.find(item => item.id === state.selection.activeElementId);
            if (!el || el.locked) return;

            const zoom = state.viewport.zoom;
            const dX = (e.clientX - state.selection.dragStartX) / (MM_TO_PX * zoom);
            const dY = (e.clientY - state.selection.dragStartY) / (MM_TO_PX * zoom);

            if (mode === "move") {
                let newX = state.selection.elemStartX + dX;
                let newY = state.selection.elemStartY + dY;

                if (state.preferences.snap) {
                    newX = Math.round(newX / state.preferences.gridSize) * state.preferences.gridSize;
                    newY = Math.round(newY / state.preferences.gridSize) * state.preferences.gridSize;
                }
                el.x = Math.max(0, Math.min(state.canvas.width - el.width, newX));
                el.y = Math.max(0, Math.min(state.canvas.height - el.height, newY));
                window.LabelEvents.emit("element:changed", el);
            } else if (mode === "resize") {
                let newW = state.selection.elemStartWidth + dX;
                let newH = state.selection.elemStartHeight + dY;

                if (state.preferences.snap) {
                    newW = Math.round(newW / state.preferences.gridSize) * state.preferences.gridSize;
                    newH = Math.round(newH / state.preferences.gridSize) * state.preferences.gridSize;
                }
                el.width = Math.max(5, Math.min(state.canvas.width - el.x, newW));
                el.height = Math.max(5, Math.min(state.canvas.height - el.y, newH));
                window.LabelEvents.emit("element:changed", el);
            }
            this.redraw();
        }

        onMouseUp() {
            const state = window.LabelStudioState;
            state.selection.dragMode = null;
        }

        pushHistoryState() {
            const state = window.LabelStudioState;
            // Clone document elements state (Command history transaction)
            const snapshot = JSON.stringify(state.document.elements);
            state.history.undo.push(snapshot);
            state.history.redo = []; // clear redo buffer
        }

        undo() {
            const state = window.LabelStudioState;
            if (state.history.undo.length === 0) return;
            const current = JSON.stringify(state.document.elements);
            state.history.redo.push(current);

            const previous = state.history.undo.pop();
            state.document.elements = JSON.parse(previous);
            this.redraw();
            if (state.selection.activeElementId) {
                const el = state.document.elements.find(item => item.id === state.selection.activeElementId);
                if (el) window.LabelEvents.emit("element:selected", el);
            }
        }

        redo() {
            const state = window.LabelStudioState;
            if (state.history.redo.length === 0) return;
            const current = JSON.stringify(state.document.elements);
            state.history.undo.push(current);

            const next = state.history.redo.pop();
            state.document.elements = JSON.parse(next);
            this.redraw();
            if (state.selection.activeElementId) {
                const el = state.document.elements.find(item => item.id === state.selection.activeElementId);
                if (el) window.LabelEvents.emit("element:selected", el);
            }
        }
    }

    window.LabelDesigner = LabelDesigner;

    document.addEventListener("DOMContentLoaded", () => {
        const designer = new LabelDesigner("labelCanvas");
        window.LabelEvents.emit("designer:ready", designer);
    });

})();
