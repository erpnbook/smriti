/**
 * @file:    public/js/layout_engine/navigation_renderer.js
 * @desc:    SMRITI Retail OS Layout Engine — Top Dock Navigation Renderer.
 *           When the sidebar is in top-dock mode, horizontal nav items that
 *           overflow the available width are collected into a "More ▾" dropdown.
 *           Uses ResizeObserver for live reflow on window resize.
 *
 *           Only activates when body/app has class sidebar-position-top.
 *           In left/right/bottom dock modes this module is a no-op.
 *
 * @version: 1.0.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function (global) {
    "use strict";

    var MORE_ID     = "srle-nav-more-btn";
    var DROPDOWN_ID = "srle-nav-more-dropdown";
    var _observer   = null;
    var _active     = false;

    /* ── Helpers ────────────────────────────────────────────────────────── */

    function _isTopDock() {
        return document.body.classList.contains("sidebar-position-top") ||
               (document.getElementById("app") &&
                document.getElementById("app").classList.contains("sidebar-position-top"));
    }

    function _getSidebarContent() {
        return document.querySelector(".smriti-sidebar-content");
    }

    function _getNavItems() {
        var content = _getSidebarContent();
        if (!content) return [];
        return Array.prototype.slice.call(
            content.querySelectorAll(".smriti-sidebar-item:not(.srle-more-hidden)")
        );
    }

    function _removeMoreButton() {
        var btn  = document.getElementById(MORE_ID);
        var drop = document.getElementById(DROPDOWN_ID);
        if (btn)  btn.parentNode && btn.parentNode.removeChild(btn);
        if (drop) drop.parentNode && drop.parentNode.removeChild(drop);

        // Restore all hidden items
        var hidden = document.querySelectorAll(".smriti-sidebar-item.srle-overflow-hidden");
        Array.prototype.forEach.call(hidden, function (el) {
            el.classList.remove("srle-overflow-hidden");
            el.style.display = "";
        });
    }

    function _buildMoreButton(overflowItems) {
        // Remove stale button
        _removeMoreButton();

        var content = _getSidebarContent();
        if (!content || overflowItems.length === 0) return;

        // "More ▾" button
        var btn = document.createElement("button");
        btn.id = MORE_ID;
        btn.className = "smriti-sidebar-item srle-more-btn";
        btn.setAttribute("aria-haspopup", "true");
        btn.setAttribute("aria-expanded", "false");
        btn.setAttribute("aria-controls", DROPDOWN_ID);
        btn.innerHTML =
            '<span class="smriti-sidebar-item-label">More</span>' +
            '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';

        // Dropdown panel
        var dropdown = document.createElement("div");
        dropdown.id = DROPDOWN_ID;
        dropdown.className = "srle-more-dropdown";
        dropdown.setAttribute("role", "menu");
        dropdown.hidden = true;

        overflowItems.forEach(function (item) {
            var clone = item.cloneNode(true);
            clone.setAttribute("role", "menuitem");
            clone.classList.remove("srle-overflow-hidden");
            dropdown.appendChild(clone);

            // Hide original
            item.classList.add("srle-overflow-hidden");
            item.style.display = "none";
        });

        // Toggle dropdown on button click
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            var open = !dropdown.hidden;
            dropdown.hidden = open;
            btn.setAttribute("aria-expanded", String(!open));
        });

        // Close on outside click
        document.addEventListener("click", function closeOnOutside(e) {
            if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.hidden = true;
                btn.setAttribute("aria-expanded", "false");
            }
        });

        // Keyboard: Escape closes
        dropdown.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                dropdown.hidden = true;
                btn.setAttribute("aria-expanded", "false");
                btn.focus();
            }
        });

        content.appendChild(btn);
        document.body.appendChild(dropdown);   // appended to body so it clears sidebar overflow:hidden

        // Position dropdown below the "More" button
        btn.addEventListener("click", function () {
            if (!dropdown.hidden) {
                var rect = btn.getBoundingClientRect();
                dropdown.style.top  = rect.bottom + "px";
                dropdown.style.left = rect.left + "px";
            }
        });
    }

    /* ── Core reflow logic ───────────────────────────────────────────────── */

    function _reflow() {
        if (!_isTopDock()) {
            _removeMoreButton();
            return;
        }

        var content = _getSidebarContent();
        if (!content) return;

        // First: restore all hidden items so we can re-measure
        _removeMoreButton();

        var items = _getNavItems();
        if (items.length === 0) return;

        var containerW  = content.clientWidth;
        var MORE_BTN_W  = 72;   // approximate px width of "More" button
        var usedW       = 0;
        var overflowItems = [];

        items.forEach(function (item) {
            var itemW = item.getBoundingClientRect().width || item.offsetWidth || 90;
            usedW += itemW;
            if (usedW > containerW - MORE_BTN_W) {
                overflowItems.push(item);
            }
        });

        if (overflowItems.length > 0) {
            _buildMoreButton(overflowItems);
        }
    }

    /* ── Public API ──────────────────────────────────────────────────────── */

    var NavRenderer = {
        /**
         * Initialises the overflow manager.
         * Watches dock position changes and window resizes.
         */
        init: function () {
            if (_active) return;
            _active = true;

            // Run immediately
            _reflow();

            // Observe sidebar content container resize
            if (global.ResizeObserver) {
                _observer = new global.ResizeObserver(function () { _reflow(); });
                var content = _getSidebarContent();
                if (content) _observer.observe(content);
            }

            // Re-run when dock position changes (class mutation on body/app)
            if (global.MutationObserver) {
                var targets = [document.body, document.getElementById("app")].filter(Boolean);
                var mutObs = new global.MutationObserver(function () { _reflow(); });
                targets.forEach(function (el) {
                    mutObs.observe(el, { attributes: true, attributeFilter: ["class"] });
                });
            }
        },

        /**
         * Forces an immediate reflow. Call after sidebar re-renders.
         */
        reflow: function () { _reflow(); },

        /**
         * Tears down all observers. Used in tests.
         */
        destroy: function () {
            if (_observer) { _observer.disconnect(); _observer = null; }
            _removeMoreButton();
            _active = false;
        }
    };

    global.SRLE_NavRenderer = NavRenderer;

}(window));
