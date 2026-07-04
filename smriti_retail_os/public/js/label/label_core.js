/**
 * @file:    smriti_retail_os/public/js/label/label_core.js
 * @desc:    Unified state and event bus orchestrator for SMRITI Label Studio.
 * @author:  Jawahar R. Mallah
 */

(function() {
    'use strict';

    // State Namespace
    window.LabelStudioState = {
        activeTemplate: null,
        activePrinter: null,
        templatesList: [],
        printersList: [],
        labelDimensions: {
            width_mm: 100,
            height_mm: 50
        },
        elements: []
    };

    // Event Bus Namespace
    window.LabelEvents = {
        listeners: {},
        on(event, callback) {
            if (!this.listeners[event]) {
                this.listeners[event] = [];
            }
            this.listeners[event].push(callback);
        },
        emit(event, data) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(cb => {
                    try { cb(data); } catch(e) { console.error(e); }
                });
            }
        }
    };

    // Initializer Orchestration
    document.addEventListener("DOMContentLoaded", () => {
        // Mock init hooks
        window.LabelEvents.emit("studio:ready");
    });

})();
