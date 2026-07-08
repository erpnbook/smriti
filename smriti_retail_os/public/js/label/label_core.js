/**
 * @file:    smriti_retail_os/public/js/label/label_core.js
 * @desc:    Unified state and event bus orchestrator for SMRITI Label Studio.
 * @author:  Jawahar R. Mallah
 */

(function() {
    'use strict';

    // ── State Namespace ──────────────────────────────────────────────────────
    window.LabelStudioState = {
        activeTemplate: null,
        activePrinter:  null,
        templatesList:  [],
        printersList:   [],
        nextId: 1,                  // Auto-increment for unique element IDs
        labelDimensions: {
            width_mm:  100,
            height_mm:  50
        },
        elements: []               // Starts EMPTY — user adds elements via toolbar
    };

    // ── Event Bus ────────────────────────────────────────────────────────────
    window.LabelEvents = {
        listeners: {},

        on(event, callback) {
            if (!this.listeners[event]) this.listeners[event] = [];
            this.listeners[event].push(callback);
        },

        off(event, callback) {
            if (!this.listeners[event]) return;
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        },

        emit(event, data) {
            (this.listeners[event] || []).forEach(cb => {
                try { cb(data); } catch(e) { console.error('[LabelEvents]', event, e); }
            });
        }
    };

    // ── Element Factory ──────────────────────────────────────────────────────
    window.LabelElementFactory = {
        /** Creates a new element object with sensible retail defaults */
        create(type, overrides = {}) {
            const state = window.LabelStudioState;
            const id    = `${type.toLowerCase()}_${state.nextId++}`;
            const defaults = {
                Text:    { width: 60, height: 8,  content: 'Product Name' },
                Barcode: { width: 80, height: 18, content: '000000000000' },
                QRCode:  { width: 20, height: 20, content: 'https://smriti.app' },
                Line:    { width: 90, height: 1,  content: '' }
            };
            const typeDefaults = defaults[type] || defaults.Text;
            return Object.assign({
                id,
                type,
                x:        5,
                y:        5,
                rotation: 0,
                locked:   false,
                visible:  true,
                zIndex:   state.nextId,
                font_size: 8,
                ...typeDefaults
            }, overrides);
        }
    };

    // ── Init ─────────────────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        window.LabelEvents.emit('studio:ready');
    });

})();
