/**
 * @file:    public/js/layout_engine/responsive_manager.js
 * @desc:    SMRITI Retail OS Layout Engine — Responsive Breakpoint Manager.
 *           Observes viewport width and auto-switches dock on mobile/tablet.
 *           On desktop, user's saved preference is always respected.
 * @version: 1.0.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function (global) {
    "use strict";

    var BP_DESKTOP = 1280;   // >= 1280px: user preference
    var BP_TABLET  = 768;    // 768–1279px: left or bottom only
    // < 768px: bottom dock + hamburger drawer

    var _callbacks   = [];
    var _current     = null;
    var _observer    = null;
    var _mql_tablet  = null;
    var _mql_desktop = null;

    function _detect() {
        var w = window.innerWidth;
        if (w >= BP_DESKTOP) return "desktop";
        if (w >= BP_TABLET)  return "tablet";
        return "mobile";
    }

    function _applyBreakpoint(bp) {
        if (bp === _current) return;
        _current = bp;

        var store   = global.SRLE_Store;
        var dock    = global.SRLE_DockManager;
        var smriti  = global.SMRITI;

        if (!store || !dock) return;

        var savedPos = store.get("position", "left");

        var targetPos;
        if (bp === "desktop") {
            targetPos = savedPos;                        // user's choice
        } else if (bp === "tablet") {
            // Tablet: allow left; collapse top/right/bottom to left
            targetPos = (savedPos === "left" || savedPos === "bottom") ? savedPos : "left";
        } else {
            targetPos = "bottom";                        // mobile always bottom
        }

        dock.applyDock(targetPos, store.get("collapsed", false));

        // Keep existing SMRITI sidebar in sync
        if (smriti && smriti.setSidebarPosition) {
            smriti.setSidebarPosition(targetPos);
        }

        // Fire registered callbacks
        _callbacks.forEach(function (fn) {
            try { fn({ breakpoint: bp, position: targetPos }); } catch (e) {}
        });
    }

    var Responsive = {
        /**
         * Initialises the responsive manager.
         * Call once after SRLE_Store and SRLE_DockManager are ready.
         */
        init: function () {
            if (_observer) return;   // already initialised

            _current = _detect();

            if (global.ResizeObserver) {
                _observer = new global.ResizeObserver(function () {
                    _applyBreakpoint(_detect());
                });
                _observer.observe(document.documentElement);
            } else {
                // Fallback: matchMedia listeners
                _mql_desktop = window.matchMedia("(min-width: " + BP_DESKTOP + "px)");
                _mql_tablet  = window.matchMedia("(min-width: " + BP_TABLET  + "px)");
                var handler = function () { _applyBreakpoint(_detect()); };
                if (_mql_desktop.addEventListener) {
                    _mql_desktop.addEventListener("change", handler);
                    _mql_tablet.addEventListener("change", handler);
                } else {
                    // Legacy (Safari 13)
                    _mql_desktop.addListener(handler);
                    _mql_tablet.addListener(handler);
                }
            }

            // Apply immediately
            _applyBreakpoint(_current);
        },

        /**
         * Returns the current breakpoint string.
         * @returns {"desktop"|"tablet"|"mobile"}
         */
        getCurrentBreakpoint: function () {
            return _current || _detect();
        },

        /**
         * Registers a callback for breakpoint changes.
         * @param {function} fn — called with { breakpoint, position }
         */
        onBreakpointChange: function (fn) {
            if (typeof fn === "function") _callbacks.push(fn);
        },

        /**
         * Tears down all observers. Used in tests.
         */
        destroy: function () {
            if (_observer) { _observer.disconnect(); _observer = null; }
            _callbacks = [];
            _current   = null;
        }
    };

    global.SRLE_Responsive = Responsive;

}(window));
