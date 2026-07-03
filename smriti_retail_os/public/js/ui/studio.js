/**
 * @file:    public/js/ui/studio.js
 * @desc:    SMRITI Studio Kernel - Runtime and SDK entrypoint.
 *           Coordinates lifecycles, routing, component registry, and event dispatching.
 * @version: 1.0.0
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

(function() {
    const registry = {};
    const eventHandlers = {};

    // 1. Studio Registry SDK
    SMRITI.registerStudio = function(config) {
        if (!config.id) {
            console.error("SMRITI SDK: Cannot register studio with missing ID.");
            return;
        }
        registry[config.id] = config;
        console.log(`SMRITI SDK: Registered Studio [${config.id}] - "${config.title}"`);
        
        // Trigger beforeLoad lifecycle hook
        if (config.lifecycle && typeof config.lifecycle.beforeLoad === "function") {
            config.lifecycle.beforeLoad(config);
        }

        // Auto initialize after rendering finishes
        $(document).ready(() => {
            if (config.lifecycle && typeof config.lifecycle.afterLoad === "function") {
                config.lifecycle.afterLoad(config);
            }
            SMRITI.trigger("studio:loaded", config);
        });
    };

    SMRITI.getStudio = function(id) {
        return registry[id];
    };

    // 2. Global Event Bus
    SMRITI.on = function(event, handler) {
        if (!eventHandlers[event]) {
            eventHandlers[event] = [];
        }
        eventHandlers[event].push(handler);
    };

    SMRITI.trigger = function(event, data) {
        if (eventHandlers[event]) {
            eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (e) {
                    console.error(`SMRITI SDK Error in event [${event}] handler:`, e);
                }
            });
        }
    };
})();
