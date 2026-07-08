/**
 * @file:    public/js/layout_engine/layout_manager.js
 * @desc:    SMRITI Retail OS Layout Engine — Primary Public API (window.SRLE).
 *           This is the single entry-point all modules and pages should call.
 *           It wraps SMRITI.* sidebar functions — it does NOT replace them.
 *           All 171 existing pages calling SMRITI.renderFlexibleSidebar()
 *           continue to work without any change.
 *
 *           Load order:
 *             layout_tokens.css → layout.css
 *             layout_store.js → dock_manager.js → responsive_manager.js
 *             → layout_manager.js   (this file)
 *
 * @version: 1.0.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function (global) {
    "use strict";

    var VERSION = "1.0.0";

    /* ── Workspace Registry ─────────────────────────────────────────────── */
    var _registry = {};    // id → config
    var _activeId = null;

    /* ── Internal helpers ───────────────────────────────────────────────── */
    function _store()     { return global.SRLE_Store; }
    function _dock()      { return global.SRLE_DockManager; }
    function _resp()      { return global.SRLE_Responsive; }
    function _smriti()    { return global.SMRITI; }

    function _warn(msg) {
        if (global.console && global.console.warn) console.warn("[SRLE] " + msg);
    }

    function _applyAll(position, collapsed) {
        var d = _dock();
        if (d) d.applyDock(position, collapsed);

        // Keep legacy SMRITI sidebar in sync
        var s = _smriti();
        if (s && s.setSidebarPosition) s.setSidebarPosition(position);
        if (s && s.toggleSidebarCollapse && collapsed !== undefined) {
            // Only call if the state actually changed
            var sidebar = document.querySelector(".smriti-sidebar");
            if (sidebar) {
                var isCollapsed = sidebar.classList.contains("collapsed");
                if (collapsed !== isCollapsed) {
                    s.toggleSidebarCollapse();
                }
            }
        }
    }

    /* ── Public API — window.SRLE ───────────────────────────────────────── */
    var SRLE = {

        /**
         * Returns the SRLE version string.
         * @returns {string}
         */
        getVersion: function () { return VERSION; },

        /**
         * Switches the dock position at runtime without a page reload.
         * Persists to SRLE_Store (localStorage + legacy keys).
         *
         * @param {"left"|"right"|"top"|"bottom"} position
         */
        setLayout: function (position) {
            var valid = { left: 1, right: 1, top: 1, bottom: 1 };
            if (!valid[position]) {
                _warn("setLayout: invalid position '" + position + "'. Use left|right|top|bottom.");
                return;
            }
            var s = _store();
            if (s) s.set("position", position);

            var collapsed = s ? s.get("collapsed", false) : false;
            _applyAll(position, collapsed);
        },

        /**
         * Returns the currently active dock position from the store.
         * @returns {"left"|"right"|"top"|"bottom"}
         */
        getLayout: function () {
            var s = _store();
            return s ? s.get("position", "left") : "left";
        },

        /**
         * Toggles the sidebar open/collapsed without changing dock position.
         */
        toggleSidebar: function () {
            var s = _store();
            var current = s ? s.get("collapsed", false) : false;
            this.setCollapsed(!current);
        },

        /**
         * Sets the sidebar collapsed state.
         * @param {boolean} state — true = collapsed, false = expanded
         */
        setCollapsed: function (state) {
            var s = _store();
            if (s) s.set("collapsed", !!state);

            var d = _dock();
            if (d) d.setCollapsed(!!state);

            // Sync to legacy sidebar toggle
            var sidebar = document.querySelector(".smriti-sidebar");
            if (sidebar) {
                var isCollapsed = sidebar.classList.contains("collapsed");
                if (!!state !== isCollapsed) {
                    var sm = _smriti();
                    if (sm && sm.toggleSidebarCollapse) sm.toggleSidebarCollapse();
                }
            }
        },

        /**
         * Saves all current preferences to localStorage and the server.
         */
        savePreferences: function () {
            var s = _store();
            if (s) s.syncToServer();
        },

        /**
         * Restores preferences from the server and re-applies layout.
         * @param {function} [callback] — called after preferences are applied
         */
        restorePreferences: function (callback) {
            var self = this;
            var s = _store();
            if (!s) {
                if (callback) callback();
                return;
            }
            s.restoreFromServer(function (prefs) {
                _applyAll(prefs.position || "left", !!prefs.collapsed);
                if (callback) callback(prefs);
            });
        },

        /**
         * Registers a workspace in the SRLE workspace registry.
         * Pages call this on load to declare themselves.
         *
         * @param {{ id: string, label: string, url: string, icon?: string, module?: string }} config
         */
        registerWorkspace: function (config) {
            if (!config || !config.id) {
                _warn("registerWorkspace: config.id is required.");
                return;
            }
            _registry[config.id] = {
                id:     config.id,
                label:  config.label   || config.id,
                url:    config.url     || window.location.pathname,
                icon:   config.icon    || null,
                module: config.module  || null
            };
            // Store last workspace
            var s = _store();
            if (s) s.set("last_workspace", config.id);
            _activeId = config.id;
        },

        /**
         * Returns all registered workspaces.
         * @returns {Object}
         */
        getWorkspaces: function () {
            return Object.assign({}, _registry);
        },

        /**
         * Returns the active workspace id.
         * @returns {string|null}
         */
        getActiveWorkspace: function () {
            return _activeId;
        },

        /**
         * Re-applies the current layout state to the DOM.
         * Safe to call after a dynamic DOM change or page transition.
         */
        refreshLayout: function () {
            var s = _store();
            var position  = s ? s.get("position",  "left")  : "left";
            var collapsed = s ? s.get("collapsed", false) : false;
            _applyAll(position, collapsed);
        },

        /**
         * Initialises the entire SRLE stack.
         * Call once after DOM is ready, before rendering the sidebar.
         * Optionally pass a workspace config to register the current page.
         *
         * @param {{ workspace?: Object, restoreFromServer?: boolean }} [options]
         */
        init: function (options) {
            options = options || {};

            // Apply saved layout immediately (before sidebar renders)
            this.refreshLayout();

            // Boot responsive manager
            var r = _resp();
            if (r) r.init();

            // Register current workspace if provided
            if (options.workspace) {
                this.registerWorkspace(options.workspace);
            }

            // Optionally restore from server (cross-device sync)
            if (options.restoreFromServer) {
                this.restorePreferences();
            }
        }
    };

    global.SRLE = SRLE;

    // Auto-init after DOM ready if not already done by the page
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            if (!global._srle_init_done) SRLE.init();
        });
    } else {
        if (!global._srle_init_done) {
            setTimeout(function () { SRLE.init(); }, 0);
        }
    }

}(window));
