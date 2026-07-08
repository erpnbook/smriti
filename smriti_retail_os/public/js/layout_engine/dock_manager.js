/**
 * @file:    public/js/layout_engine/dock_manager.js
 * @desc:    SMRITI Retail OS Layout Engine — Dock Manager.
 *           Applies dock-specific CSS classes, updates workspace offset
 *           CSS custom properties, and adjusts .srle-workspace margins
 *           so any page using the opt-in class gets correct layout automatically.
 * @version: 1.0.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function (global) {
    "use strict";

    var POSITION_CLASSES = [
        "sidebar-position-left",
        "sidebar-position-right",
        "sidebar-position-top",
        "sidebar-position-bottom"
    ];

    var COLLAPSED_CLASS  = "srle-sidebar-collapsed";
    var ACTIVE_CLASS     = "srle-active";

    /**
     * Returns the current sidebar width in pixels (reads CSS custom property).
     */
    function _sidebarWidth() {
        var raw = getComputedStyle(document.documentElement)
            .getPropertyValue("--srle-sidebar-width").trim();
        return parseInt(raw, 10) || 260;
    }

    function _collapsedWidth() {
        var raw = getComputedStyle(document.documentElement)
            .getPropertyValue("--srle-sidebar-collapsed-width").trim();
        return parseInt(raw, 10) || 68;
    }

    function _topHeight() {
        var raw = getComputedStyle(document.documentElement)
            .getPropertyValue("--srle-sidebar-top-height").trim();
        return parseInt(raw, 10) || 52;
    }

    function _bottomHeight() {
        var raw = getComputedStyle(document.documentElement)
            .getPropertyValue("--srle-sidebar-bottom-height").trim();
        return parseInt(raw, 10) || 60;
    }

    /**
     * Sets CSS custom properties on :root for workspace offsets.
     * These are consumed by layout.css .srle-workspace margin transitions.
     */
    function _applyOffsets(position, collapsed) {
        var root = document.documentElement;
        var sw = collapsed ? _collapsedWidth() : _sidebarWidth();
        var offsets = { left: "0px", top: "0px", right: "0px", bottom: "0px" };

        if (position === "left")   offsets.left   = sw + "px";
        if (position === "right")  offsets.right  = sw + "px";
        if (position === "top")    offsets.top    = _topHeight() + "px";
        if (position === "bottom") offsets.bottom = _bottomHeight() + "px";

        root.style.setProperty("--srle-workspace-offset-left",   offsets.left);
        root.style.setProperty("--srle-workspace-offset-top",    offsets.top);
        root.style.setProperty("--srle-workspace-offset-right",  offsets.right);
        root.style.setProperty("--srle-workspace-offset-bottom", offsets.bottom);
    }

    var DockManager = {
        /**
         * Applies the dock position to all relevant DOM targets.
         * @param {string}  position  — "left" | "right" | "top" | "bottom"
         * @param {boolean} collapsed — whether the sidebar is currently collapsed
         */
        applyDock: function (position, collapsed) {
            var targets = [
                document.getElementById("app"),
                document.getElementById("smriti-app"),
                document.body
            ].filter(Boolean);

            targets.forEach(function (el) {
                // Remove all dock classes
                POSITION_CLASSES.forEach(function (cls) { el.classList.remove(cls); });

                // Add active SRLE marker
                el.classList.add(ACTIVE_CLASS);

                // Apply new dock class (left is default — no extra class needed by sidebar CSS)
                if (position === "right")  el.classList.add("sidebar-position-right");
                if (position === "top")    el.classList.add("sidebar-position-top");
                if (position === "bottom") el.classList.add("sidebar-position-bottom");

                // Collapsed state marker
                if (collapsed) {
                    el.classList.add(COLLAPSED_CLASS);
                } else {
                    el.classList.remove(COLLAPSED_CLASS);
                }
            });

            _applyOffsets(position, collapsed);
        },

        /**
         * Updates just the collapsed state without changing dock position.
         * @param {boolean} collapsed
         */
        setCollapsed: function (collapsed) {
            var position = global.SRLE_Store
                ? global.SRLE_Store.get("position", "left")
                : "left";

            var targets = [
                document.getElementById("app"),
                document.getElementById("smriti-app"),
                document.body
            ].filter(Boolean);

            targets.forEach(function (el) {
                if (collapsed) {
                    el.classList.add(COLLAPSED_CLASS);
                } else {
                    el.classList.remove(COLLAPSED_CLASS);
                }
            });

            _applyOffsets(position, collapsed);
        },

        /**
         * Returns the current computed workspace offsets as a plain object.
         * @returns {{ left: string, top: string, right: string, bottom: string }}
         */
        getWorkspaceOffset: function () {
            var style = getComputedStyle(document.documentElement);
            return {
                left:   style.getPropertyValue("--srle-workspace-offset-left").trim()   || "0px",
                top:    style.getPropertyValue("--srle-workspace-offset-top").trim()    || "0px",
                right:  style.getPropertyValue("--srle-workspace-offset-right").trim()  || "0px",
                bottom: style.getPropertyValue("--srle-workspace-offset-bottom").trim() || "0px"
            };
        },

        /**
         * Re-applies offsets from current stored state.
         * Safe to call after window resize.
         */
        refresh: function () {
            var store = global.SRLE_Store;
            if (!store) return;
            this.applyDock(
                store.get("position", "left"),
                store.get("collapsed", false)
            );
        }
    };

    global.SRLE_DockManager = DockManager;

}(window));
