/**
 * @file: smriti_retail_os/public/js/smriti_breadcrumbs.js
 * @description: SMRITI Retail OS — Recursive Automatic Breadcrumb Engine
 * @author: Jawahar R. Mallah
 * @version: 1.0.0
 */

window.SMRITI = window.SMRITI || {};

(function(SMRITI) {
    "use strict";

    /**
     * Recursively traverse the navigation tree to build a breadcrumb trail
     * for the given pathname, supporting unlimited nesting depth.
     *
     * Returns an array of {label, route} objects from root to active item,
     * or an empty array if no match is found.
     */
    SMRITI.buildBreadcrumbTrail = function(navData, pathname) {
        if (!navData || !navData.sections) return [];

        var cleanPath = pathname.split("?")[0].rstrip ? pathname.split("?")[0] : pathname.split("?")[0];
        cleanPath = cleanPath.replace(/\/$/, "") || "/";

        for (var si = 0; si < navData.sections.length; si++) {
            var sec = navData.sections[si];
            if (sec.status === "hidden") continue;

            var items = sec.items || [];
            for (var ii = 0; ii < items.length; ii++) {
                var item = items[ii];
                if (item.type === "header") continue;

                var itemRoute = (item.route || "").split("?")[0].replace(/\/$/, "");
                var itemStandalone = (item.standalone_route || "").split("?")[0].replace(/\/$/, "");

                if (itemRoute === cleanPath || itemStandalone === cleanPath) {
                    // Found — build trail: [Home, Section, Item]
                    var trail = [
                        { label: "Home", route: "/smriti" },
                        { label: sec.label, route: sec.route || null },
                        { label: item.label, route: itemRoute || null }
                    ];
                    // If the item has nested children (future), recurse here
                    if (item.children && item.children.length) {
                        var childTrail = _findInChildren(item.children, cleanPath);
                        if (childTrail.length) {
                            trail = trail.concat(childTrail);
                        }
                    }
                    return trail;
                }
            }
        }
        return [];
    };

    function _findInChildren(children, cleanPath) {
        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            var childRoute = (child.route || "").split("?")[0].replace(/\/$/, "");
            if (childRoute === cleanPath) {
                return [{ label: child.label, route: childRoute }];
            }
            if (child.children && child.children.length) {
                var deeper = _findInChildren(child.children, cleanPath);
                if (deeper.length) {
                    return [{ label: child.label, route: childRoute }].concat(deeper);
                }
            }
        }
        return [];
    }

    /**
     * Renders a breadcrumb bar into the given container element.
     * Creates a styled <nav> with aria-label="Breadcrumb".
     */
    SMRITI.renderBreadcrumbs = function(containerId, navData, pathname) {
        var container = document.getElementById(containerId) || document.querySelector(".smriti-breadcrumbs");
        if (!container) {
            container = document.createElement("nav");
            container.id = "smriti-breadcrumbs";
            container.setAttribute("aria-label", "Breadcrumb");
            container.className = "smriti-breadcrumbs";
            var firstSection = document.querySelector(".smriti-main, .main-content, main");
            if (firstSection) firstSection.insertBefore(container, firstSection.firstChild);
        }

        var trail = SMRITI.buildBreadcrumbTrail(navData, pathname || window.location.pathname);
        if (!trail || trail.length === 0) {
            container.style.display = "none";
            return;
        }

        container.style.display = "";

        var html = '<ol class="smriti-breadcrumb-list" aria-label="breadcrumb">';
        trail.forEach(function(crumb, idx) {
            var isLast = idx === trail.length - 1;
            if (isLast || !crumb.route) {
                html += '<li class="smriti-breadcrumb-item active" aria-current="page">' +
                    _escHtml(crumb.label) + '</li>';
            } else {
                html += '<li class="smriti-breadcrumb-item">' +
                    '<a href="' + _escHtml(crumb.route) + '">' + _escHtml(crumb.label) + '</a>' +
                    '<span class="smriti-breadcrumb-sep" aria-hidden="true"> › </span>' +
                    '</li>';
            }
        });
        html += '</ol>';
        container.innerHTML = html;
    };

    /**
     * Auto-mount: if navigation is available in frappe.boot, render breadcrumbs immediately.
     */
    SMRITI.mountBreadcrumbs = function(activeContainerId) {
        var navData = window.frappe && window.frappe.boot && window.frappe.boot.smriti_navigation;
        if (navData) {
            SMRITI.renderBreadcrumbs(activeContainerId, navData, window.location.pathname);
        } else if (window.frappe && window.frappe.call) {
            window.frappe.call({
                method: "smriti_retail_os.navigation.navigation_service.get_user_navigation",
                callback: function(r) {
                    if (r && r.message) {
                        SMRITI.renderBreadcrumbs(activeContainerId, r.message, window.location.pathname);
                    }
                }
            });
        }
    };

    function _escHtml(str) {
        return String(str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

}(window.SMRITI));
