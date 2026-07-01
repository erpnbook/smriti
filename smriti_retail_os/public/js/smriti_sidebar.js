/**
 * @file: smriti_retail_os/public/js/smriti_sidebar.js
 * @description: SMRITI Retail OS — Unified Sidebar Controller (shadcn/ui-style)
 * @author: Jawahar R Mallah
 * @version: 2.0.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

window.SMRITI = window.SMRITI || {};

(function (SMRITI) {
    "use strict";

    // ── SVG Icon Registry (Self-contained, no external deps) ──
    var ICONS = {
        chevron: '<svg class="smriti-sidebar-group-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>',
        collapse: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>',
        expand: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line><path d="M14 9l3 3-3 3"></path></svg>',
        default: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle></svg>',
        
        masters: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>',
        cge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 6l-9.5 9.5-5-5L1 18"></path><polyline points="17 6 23 6 23 12"></polyline></svg>',
        psv: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        sales: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>',
        purchase: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>',
        inventory: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>',
        barcode_studio: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5v14M6 5v14M10 5v14M14 5v14M17 5v14M21 5v14"></path></svg>',
        finance: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect><line x1="12" y1="4" x2="12" y2="20"></line></svg>',
        reports: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
        administration: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
        help_desk: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        ai_hub: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="M12 6v12M6 12h12"></path></svg>',
        commercial: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>'
    };

    /**
     * Renders the unified dynamic sidebar into the page target element.
     * Maps both standalone activePageId AND current pathname routes.
     */
    SMRITI.renderFlexibleSidebar = function (activePageId) {
        var target = document.getElementById("smriti-sidebar-target") || document.getElementById("smriti-sidebar");
        if (!target) {
            target = document.createElement("div");
            target.id = "smriti-sidebar";
            document.body.appendChild(target);
        }

        // Apply sidebar class to container
        target.classList.add("smriti-sidebar");

        var user = (window.frappe && window.frappe.session && window.frappe.session.user) || "Administrator";
        var bootNav = window.frappe && window.frappe.boot && window.frappe.boot.smriti_navigation;

        if (bootNav) {
            buildTree(bootNav);
        } else {
            window.frappe.call({
                method: "smriti_retail_os.navigation.navigation_service.get_user_navigation",
                args: { user: user },
                callback: function (r) {
                    if (r && r.message) {
                        buildTree(r.message);
                    }
                }
            });
        }

        function buildTree(navData) {
            if (!navData || !navData.sections) return;

            var activeRoute = window.location.pathname;
            var collapsedGroupIds = JSON.parse(localStorage.getItem("smriti-sidebar-collapsed-groups") || "[]");
            var isSidebarCollapsed = localStorage.getItem("smriti-sidebar-collapsed") === "true";

            // Apply sidebar layout controls from localStorage
            var currentPosition = localStorage.getItem("smriti-sidebar-position") || "left";
            var appNode = document.getElementById("app") || document.body;
            if (currentPosition === "right") {
                appNode.classList.add("sidebar-position-right");
            } else {
                appNode.classList.remove("sidebar-position-right");
            }

            if (isSidebarCollapsed) {
                target.classList.add("collapsed");
                var mainEl = document.querySelector(".smriti-main") || document.querySelector(".main-wrapper");
                if (mainEl) mainEl.classList.add("sidebar-collapsed");
                appNode.classList.add("sidebar-collapsed");
            }

            var html = [];

            // ── HEADER BRAND ──
            html.push('<div class="smriti-sidebar-header">');
            html.push('  <div class="smriti-sidebar-brand">');
            html.push('    <div class="smriti-sidebar-brand-logo"></div>');
            html.push('    <span>SMRITI Retail OS</span>');
            html.push('  </div>');
            html.push('  <button class="smriti-sidebar-toggle-btn" id="smriti-sidebar-toggle">');
            html.push(isSidebarCollapsed ? ICONS.expand : ICONS.collapse);
            html.push('  </button>');
            html.push('</div>');

            // ── FAVORITES / PINNED ──
            var favorites = JSON.parse(localStorage.getItem("smriti-sidebar-favorites") || "[]");
            var pinnedItems = [];
            if (favorites.length > 0) {
                navData.sections.forEach(function(sec) {
                    (sec.items || []).forEach(function(item) {
                        if (favorites.indexOf(item.id) !== -1) {
                            pinnedItems.push({ item: item, sec: sec });
                        }
                    });
                });
            }

            // ── SEARCH BUTTON ──
            html.push('<button class="smriti-cmd-search-btn" id="smriti-cmd-trigger" title="Search (Ctrl+K)">');
            html.push('  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>');
            html.push('  <span>Search</span>');
            html.push('  <kbd>⌘K</kbd>');
            html.push('</button>');

            // ── CONTENT GROUPS ──
            html.push('<div class="smriti-sidebar-content">');

            // Pinned group
            if (pinnedItems.length > 0) {
                html.push('<div class="smriti-sidebar-group" data-group-id="__pinned__">');
                html.push('  <div class="smriti-sidebar-group-header"><span>⭐ Pinned</span>' + ICONS.chevron + '</div>');
                html.push('  <div class="smriti-sidebar-group-items"><div class="smriti-sidebar-group-items-inner">');
                pinnedItems.forEach(function(p) {
                    var item = p.item;
                    var isItemActive = (item.id === activePageId || item.route === activeRoute);
                    html.push('<a class="smriti-sidebar-item' + (isItemActive ? ' active' : '') + '" href="' + (item.route || "#") + '">');
                    html.push('  <div class="smriti-sidebar-item-icon">' + (ICONS[p.sec.id] || ICONS.default) + '</div>');
                    html.push('  <span class="smriti-sidebar-item-label">' + item.label + '</span>');
                    html.push('  <button class="smriti-star-btn active" data-item-id="' + item.id + '" title="Unpin">⭐</button>');
                    html.push('</a>');
                });
                html.push('  </div></div></div>');
            }

            
            navData.sections.forEach(function (sec) {
                if (sec.status === "hidden" || !sec.items || sec.items.length === 0) return;

                // Check if activePageId matches this section's item IDs, or if pathname matches
                var hasActiveChild = sec.items.some(function (item) {
                    return item.id === activePageId || item.route === activeRoute || item.standalone_route === activeRoute;
                });

                var isCollapsed = collapsedGroupIds.indexOf(sec.id) !== -1;
                if (hasActiveChild) {
                    isCollapsed = false;
                    var idx = collapsedGroupIds.indexOf(sec.id);
                    if (idx !== -1) collapsedGroupIds.splice(idx, 1);
                }

                html.push('<div class="smriti-sidebar-group' + (isCollapsed ? ' collapsed' : '') + '" data-group-id="' + sec.id + '">');
                html.push('  <div class="smriti-sidebar-group-header">');
                html.push('    <span>' + sec.label + '</span>');
                html.push(ICONS.chevron);
                html.push('  </div>');
                html.push('  <div class="smriti-sidebar-group-items">');
                html.push('    <div class="smriti-sidebar-group-items-inner">');

                sec.items.forEach(function (item) {
                    if (item.status === "hidden") return;

                    if (item.type === "header") {
                        html.push('<div class="smriti-sidebar-item-header">' + item.label + '</div>');
                        return;
                    }

                    var isItemActive = (item.id === activePageId || item.route === activeRoute || item.standalone_route === activeRoute);
                    var iconHtml = ICONS[sec.id] || ICONS.default;
                    var itemRoute = item.route || "#";
                    var isFav = favorites.indexOf(item.id) !== -1;

                    html.push('<a class="smriti-sidebar-item' + (isItemActive ? ' active' : '') + '" href="' + itemRoute + '">');
                    html.push('  <div class="smriti-sidebar-item-icon">' + iconHtml + '</div>');
                    html.push('  <span class="smriti-sidebar-item-label">' + item.label + '</span>');
                    html.push('  <button class="smriti-star-btn' + (isFav ? ' active' : '') + '" data-item-id="' + item.id + '" title="' + (isFav ? 'Unpin' : 'Pin to Favorites') + '">' + (isFav ? '⭐' : '☆') + '</button>');
                    html.push('</a>');

                });

                html.push('    </div>');
                html.push('  </div>');
                html.push('</div>');
            });

            html.push('</div>');

            // ── THEME MANAGER PILL BAR ──
            var currentTheme = localStorage.getItem("smriti-theme-style") || "sleek-compact";
            html.push('<div class="smriti-standalone-theme-bar">');
            html.push('  <div class="smriti-standalone-theme-pill' + (currentTheme === "sleek-compact" ? " active" : "") + '" data-theme="sleek-compact" title="Sleek Compact Flat">');
            html.push('    <span>⚡</span><span class="theme-label">Sleek</span>');
            html.push('  </div>');
            html.push('  <div class="smriti-standalone-theme-pill' + (currentTheme === "hybrid-light" ? " active" : "") + '" data-theme="hybrid-light" title="Hybrid Light Mode">');
            html.push('    <span>🎨</span><span class="theme-label">Hybrid L</span>');
            html.push('  </div>');
            html.push('  <div class="smriti-standalone-theme-pill' + (currentTheme === "hybrid-dark" ? " active" : "") + '" data-theme="hybrid-dark" title="Hybrid Dark Mode">');
            html.push('    <span>🌙</span><span class="theme-label">Hybrid D</span>');
            html.push('  </div>');
            html.push('  <div class="smriti-standalone-theme-pill' + (currentTheme === "minimalist" ? " active" : "") + '" data-theme="minimalist" title="Minimalist Flat">');
            html.push('    <span>🏢</span><span class="theme-label">Minimal</span>');
            html.push('  </div>');
            html.push('</div>');

            // ── FOOTER USER PROFILE ──
            var userFullName = (window.frappe && window.frappe.session && window.frappe.session.user_fullname) || user;
            var firstChar = userFullName.charAt(0).toUpperCase();
            var userRole = "Retail Operator";
            if (window.frappe && window.frappe.user_roles && window.frappe.user_roles.indexOf("Administrator") !== -1) {
                userRole = "Administrator";
            } else if (window.frappe && window.frappe.user_roles && window.frappe.user_roles.indexOf("SMRITI Cashier") !== -1) {
                userRole = "Cashier";
            }

            html.push('<div class="smriti-sidebar-footer">');
            html.push('  <div class="smriti-sidebar-user">');
            html.push('    <div class="smriti-sidebar-user-avatar">' + firstChar + '</div>');
            html.push('    <div class="smriti-sidebar-user-info">');
            html.push('      <span class="smriti-sidebar-user-name">' + userFullName + '</span>');
            html.push('      <span class="smriti-sidebar-user-role">' + userRole + '</span>');
            html.push('    </div>');
            html.push('  </div>');
            html.push('</div>');

            target.innerHTML = html.join("\n");

            // ── CLICK HANDLERS ──

            // 1. Sidebar Toggle Button
            var toggleBtn = target.querySelector("#smriti-sidebar-toggle");
            if (toggleBtn) {
                toggleBtn.addEventListener("click", function () {
                    var collapsed = target.classList.toggle("collapsed");
                    localStorage.setItem("smriti-sidebar-collapsed", collapsed);
                    
                    var mainEl = document.querySelector(".smriti-main") || document.querySelector(".main-wrapper");
                    if (mainEl) mainEl.classList.toggle("sidebar-collapsed", collapsed);
                    appNode.classList.toggle("sidebar-collapsed", collapsed);
                    
                    toggleBtn.innerHTML = collapsed ? ICONS.expand : ICONS.collapse;
                });
            }

            // 2. Expand/Collapse Section Groups
            var headers = target.querySelectorAll(".smriti-sidebar-group-header");
            headers.forEach(function (hdr) {
                hdr.addEventListener("click", function () {
                    if (target.classList.contains("collapsed")) return;

                    var groupEl = hdr.parentElement;
                    var groupId = groupEl.getAttribute("data-group-id");
                    var isCollapsedNow = groupEl.classList.toggle("collapsed");

                    var collapsedGroups = JSON.parse(localStorage.getItem("smriti-sidebar-collapsed-groups") || "[]");
                    if (isCollapsedNow) {
                        if (collapsedGroups.indexOf(groupId) === -1) {
                            collapsedGroups.push(groupId);
                        }
                    } else {
                        var idx = collapsedGroups.indexOf(groupId);
                        if (idx !== -1) collapsedGroups.splice(idx, 1);
                    }
                    localStorage.setItem("smriti-sidebar-collapsed-groups", JSON.stringify(collapsedGroups));
                });
            });

            // 3. Theme switching pills click
            var themePills = target.querySelectorAll(".smriti-standalone-theme-pill");
            themePills.forEach(function (pill) {
                pill.addEventListener("click", function () {
                    var themeKey = pill.getAttribute("data-theme");
                    if (window.SMRITI.switchTheme) {
                        window.SMRITI.switchTheme(themeKey);
                    }
                });
            });

            // 4. Favorites — Star button handler
            var starBtns = target.querySelectorAll(".smriti-star-btn");
            starBtns.forEach(function(btn) {
                btn.addEventListener("click", function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    var itemId = btn.getAttribute("data-item-id");
                    if (!itemId) return;
                    var favs = JSON.parse(localStorage.getItem("smriti-sidebar-favorites") || "[]");
                    var idx = favs.indexOf(itemId);
                    if (idx === -1) {
                        favs.push(itemId);
                    } else {
                        favs.splice(idx, 1);
                    }
                    localStorage.setItem("smriti-sidebar-favorites", JSON.stringify(favs));
                    // Rebuild sidebar to reflect change
                    buildTree(navData);
                });
            });

            // 5. Command Palette (Ctrl+K) trigger button
            var cmdBtn = target.querySelector("#smriti-cmd-trigger");
            if (cmdBtn) {
                cmdBtn.addEventListener("click", function() {
                    SMRITI.openCommandPalette(navData);
                });
            }

            // 6. Handle explain button injection if relevant
            if (window.SMRITI.injectExplainScreenButton) {
                window.SMRITI.injectExplainScreenButton(activePageId);
            }
        }
    };


    // Alias renderSidebar for backward compatibility and global inclusion
    SMRITI.renderSidebar = function (activePageId) {
        return SMRITI.renderFlexibleSidebar(activePageId);
    };

    // ── Command Palette (Ctrl+K) ──
    SMRITI.openCommandPalette = function(navData) {
        // Remove existing if open
        var existing = document.getElementById("smriti-cmd-overlay");
        if (existing) { existing.remove(); return; }

        // Flatten all nav items into a searchable list
        var allItems = [];
        if (navData && navData.sections) {
            navData.sections.forEach(function(sec) {
                (sec.items || []).forEach(function(item) {
                    if (item.type === "header" || item.status === "hidden") return;
                    allItems.push({
                        id: item.id,
                        label: item.label,
                        section: sec.label,
                        route: item.route || "#"
                    });
                });
            });
        }

        // Overlay DOM
        var overlay = document.createElement("div");
        overlay.id = "smriti-cmd-overlay";
        overlay.setAttribute("role", "dialog");
        overlay.setAttribute("aria-modal", "true");
        overlay.setAttribute("aria-label", "Command Palette");
        overlay.innerHTML = [
            '<div class="smriti-cmd-backdrop"></div>',
            '<div class="smriti-cmd-panel">',
            '  <div class="smriti-cmd-input-row">',
            '    <svg class="smriti-cmd-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
            '    <input type="text" id="smriti-cmd-input" class="smriti-cmd-input" placeholder="Search menus, pages, reports…" autocomplete="off" autofocus />',
            '    <kbd class="smriti-cmd-esc-hint">ESC</kbd>',
            '  </div>',
            '  <div class="smriti-cmd-results" id="smriti-cmd-results" role="listbox" aria-label="Search results"></div>',
            '</div>'
        ].join("");
        document.body.appendChild(overlay);

        var input = overlay.querySelector("#smriti-cmd-input");
        var results = overlay.querySelector("#smriti-cmd-results");
        var activeIdx = -1;

        function renderResults(query) {
            var q = (query || "").trim().toLowerCase();
            var filtered = q ? allItems.filter(function(it) {
                return it.label.toLowerCase().indexOf(q) !== -1 ||
                    it.section.toLowerCase().indexOf(q) !== -1;
            }) : allItems.slice(0, 12);

            activeIdx = -1;
            if (!filtered.length) {
                results.innerHTML = '<div class="smriti-cmd-empty">No results for "' + _escHtml(query) + '"</div>';
                return;
            }

            results.innerHTML = filtered.map(function(it, i) {
                return '<a class="smriti-cmd-result-item" href="' + _escHtml(it.route) + '" role="option" data-idx="' + i + '">' +
                    '<span class="smriti-cmd-result-label">' + _escHtml(it.label) + '</span>' +
                    '<span class="smriti-cmd-result-section">' + _escHtml(it.section) + '</span>' +
                    '</a>';
            }).join("");

            // Click handlers
            results.querySelectorAll(".smriti-cmd-result-item").forEach(function(el) {
                el.addEventListener("click", function() { overlay.remove(); });
            });
        }

        function setActive(idx) {
            var items = results.querySelectorAll(".smriti-cmd-result-item");
            items.forEach(function(el, i) {
                el.classList.toggle("active", i === idx);
            });
            if (items[idx]) {
                items[idx].scrollIntoView({ block: "nearest" });
            }
        }

        input.addEventListener("input", function() { renderResults(input.value); });

        input.addEventListener("keydown", function(e) {
            var items = results.querySelectorAll(".smriti-cmd-result-item");
            if (e.key === "ArrowDown") {
                e.preventDefault();
                activeIdx = Math.min(activeIdx + 1, items.length - 1);
                setActive(activeIdx);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                activeIdx = Math.max(activeIdx - 1, 0);
                setActive(activeIdx);
            } else if (e.key === "Enter") {
                if (activeIdx >= 0 && items[activeIdx]) {
                    window.location.href = items[activeIdx].getAttribute("href");
                    overlay.remove();
                }
            } else if (e.key === "Escape") {
                overlay.remove();
            }
        });

        overlay.querySelector(".smriti-cmd-backdrop").addEventListener("click", function() { overlay.remove(); });

        renderResults("");
        setTimeout(function() { if (input) input.focus(); }, 50);
    };

    function _escHtml(str) {
        return String(str || "")
            .replace(/&/g, "&amp;").replace(/</g, "&lt;")
            .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // ── Global Ctrl+K keyboard listener ──
    document.addEventListener("keydown", function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            var navData = window.frappe && window.frappe.boot && window.frappe.boot.smriti_navigation;
            SMRITI.openCommandPalette(navData || { sections: [] });
        }
    });



    // ── Listen to theme changes globally to highlight correct sidebar theme pill ──
    document.addEventListener("smriti-theme-changed", function (e) {
        var activeTheme = e.detail.theme;
        var pills = document.querySelectorAll(".smriti-standalone-theme-pill");
        pills.forEach(function (pill) {
            if (pill.getAttribute("data-theme") === activeTheme) {
                pill.classList.add("active");
            } else {
                pill.classList.remove("active");
            }
        });
    });

    // ── Swapping & Toggling settings (backward compatibility API) ──
    SMRITI.toggleSidebarPosition = function () {
        var app = document.getElementById("app") || document.body;
        var isRight = app.classList.toggle("sidebar-position-right");
        localStorage.setItem("smriti-sidebar-position", isRight ? "right" : "left");
    };

    SMRITI.toggleSidebarCollapse = function () {
        var toggleBtn = document.getElementById("smriti-sidebar-toggle");
        if (toggleBtn) {
            toggleBtn.click();
        }
    };

    // ── Popout Window Logic ──
    SMRITI.triggerPopout = function (e, url) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        var w = 1400, h = 900;
        var left = Math.round((screen.width - w) / 2);
        var top  = Math.round((screen.height - h) / 2);
        window.open(
            url + (url.includes('?') ? '&' : '?') + 'popout=true',
            '_blank',
            `width=${w},height=${h},left=${left},top=${top},toolbar=no,menubar=no,location=no,status=no,scrollbars=yes,resizable=yes`
        );
    };

    function _initPopoutMode() {
        if (!new URLSearchParams(window.location.search).get('popout')) return;
        document.body.classList.add('popout-mode');
    }
    
    document.addEventListener('DOMContentLoaded', _initPopoutMode);

    // ── Topbar Shortcuts & Explanations ──
    SMRITI.injectLabelStudioShortcut = function () {
        var topbarRight = document.querySelector(".topbar-right");
        if (!topbarRight) return;
        if (document.getElementById("label-studio-shortcut")) return;

        var btn = document.createElement("button");
        btn.id = "label-studio-shortcut";
        btn.className = "topbtn";
        btn.title = "Label Studio";
        btn.innerHTML = `<span class="material-symbols-outlined">qr_code_scanner</span><span>Label Studio</span>`;
        btn.addEventListener("click", function () {
            window.location.href = "/barcode";
        });
        topbarRight.insertBefore(btn, topbarRight.firstChild);
    };

    SMRITI.injectExplainScreenButton = function (activePageId) {
        var topbarRight = document.querySelector(".topbar-right");
        if (!topbarRight) return;
        if (document.getElementById("smriti-explain-button")) return;

        var activeScreens = ["item_master", "billing", "purchase", "inventory"];
        if (activeScreens.indexOf(activePageId) === -1) return;

        var btn = document.createElement("button");
        btn.id = "smriti-explain-button";
        btn.className = "topbtn smriti-explain-button";
        btn.title = "Explain this Screen";
        btn.innerHTML = `<span class="material-symbols-outlined" style="color:var(--primary)">help</span><span>Explain Screen</span>`;
        
        btn.addEventListener("click", function () {
            if (typeof window.smritiExplainCurrent === 'undefined') {
                var script = document.createElement('script');
                script.src = '/assets/smriti_retail_os/js/smriti_explain.js';
                script.onload = function () {
                    if (window.smritiExplainCurrent) window.smritiExplainCurrent();
                };
                document.head.appendChild(script);
            } else {
                window.smritiExplainCurrent();
            }
        });
        topbarRight.appendChild(btn);
    };

}(window.SMRITI));
