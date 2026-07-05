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
            window.SMRITI_NAV_DATA = navData;

            var activeRoute = window.location.pathname + window.location.hash;
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
            html.push('<div class="smriti-sidebar-content" role="tree">');

            // Pinned group (MyDesk)
            if (pinnedItems.length > 0) {
                var isMyDeskCollapsed = collapsedGroupIds.indexOf("mydesk") !== -1;
                html.push('<div class="smriti-sidebar-group' + (isMyDeskCollapsed ? ' collapsed' : '') + '" data-group-id="mydesk" role="none">');
                html.push('  <div class="smriti-sidebar-group-header" role="treeitem" aria-expanded="' + (isMyDeskCollapsed ? 'false' : 'true') + '" tabindex="0"><span>MyDesk</span>' + ICONS.chevron + '</div>');
                html.push('  <div class="smriti-sidebar-group-items" role="group"><div class="smriti-sidebar-group-items-inner">');
                pinnedItems.forEach(function(p) {
                    var item = p.item;
                    var isItemActive = (item.id === activePageId || item.route === activeRoute);
                    html.push('<a class="smriti-sidebar-item' + (isItemActive ? ' active' : '') + '" href="' + (item.route || "#") + '" role="treeitem" tabindex="0"' + (isItemActive ? ' aria-current="page"' : '') + '>');
                    html.push('  <div class="smriti-sidebar-item-icon">' + (ICONS[p.sec.id] || ICONS.default) + '</div>');
                    html.push('  <span class="smriti-sidebar-item-label">' + item.label + '</span>');
                    html.push('  <div class="smriti-sidebar-item-actions">');
                    html.push('    <button class="smriti-star-btn active" data-item-id="' + item.id + '" title="Unpin from MyDesk">⭐</button>');
                    html.push('  </div>');
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

                html.push('<div class="smriti-sidebar-group' + (isCollapsed ? ' collapsed' : '') + '" data-group-id="' + sec.id + '" role="none">');
                html.push('  <div class="smriti-sidebar-group-header" role="treeitem" aria-expanded="' + (isCollapsed ? 'false' : 'true') + '" tabindex="0">');
                html.push('    <span>' + sec.label + '</span>');
                html.push(ICONS.chevron);
                html.push('  </div>');
                html.push('  <div class="smriti-sidebar-group-items" role="group">');
                html.push('    <div class="smriti-sidebar-group-items-inner">');

                sec.items.forEach(function (item) {
                    if (item.status === "hidden") return;

                    if (item.type === "header") {
                        html.push('<div class="smriti-sidebar-item-header" role="presentation">' + item.label + '</div>');
                        return;
                    }

                    var isItemActive = (item.id === activePageId || item.route === activeRoute || item.standalone_route === activeRoute);
                    var iconHtml = ICONS[sec.id] || ICONS.default;
                    var itemRoute = item.route || "#";
                    var isFav = favorites.indexOf(item.id) !== -1;

                    html.push('<a class="smriti-sidebar-item' + (isItemActive ? ' active' : '') + '" href="' + itemRoute + '" role="treeitem" tabindex="0"' + (isItemActive ? ' aria-current="page"' : '') + '>');
                    html.push('  <div class="smriti-sidebar-item-icon">' + iconHtml + '</div>');
                    html.push('  <span class="smriti-sidebar-item-label">' + item.label + '</span>');
                    html.push('  <div class="smriti-sidebar-item-actions">');
                    html.push('    <button class="smriti-popout-icon-btn" onclick="SMRITI.triggerPopout(event, \'' + itemRoute + '\')" title="Open in Popout Window">📺</button>');
                    html.push('    <button class="smriti-star-btn' + (isFav ? ' active' : '') + '" data-item-id="' + item.id + '" title="' + (isFav ? 'Unpin' : 'Pin to Favorites') + '">' + (isFav ? '⭐' : '☆') + '</button>');
                    html.push('  </div>');
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

            // ── SIDEBAR POSITION PICKER ──
            var currentPos = localStorage.getItem("smriti-sidebar-position") || "left";
            var posOptions = [
                { key: "left",   icon: "◁", label: "Left"   },
                { key: "right",  icon: "▷", label: "Right"  },
                { key: "top",    icon: "△", label: "Top"    },
                { key: "bottom", icon: "▽", label: "Bottom" }
            ];
            html.push('<div class="smriti-pos-bar" title="Sidebar Position">');
            posOptions.forEach(function(p) {
                html.push('<button class="smriti-pos-btn' + (currentPos === p.key ? " active" : "") + '" data-pos="' + p.key + '" title="Sidebar: ' + p.label + '">' + p.icon + '<span class="pos-label">' + p.label + '</span></button>');
            });
            html.push('</div>');
            // ── FOOTER USER PROFILE + NOTIFICATION BELL ──
            var userFullName = (window.frappe && window.frappe.session && window.frappe.session.user_fullname) || user;
            var firstChar = userFullName.charAt(0).toUpperCase();
            var userRole = "Retail Operator";
            if (window.frappe && window.frappe.user_roles && window.frappe.user_roles.indexOf("Administrator") !== -1) {
                userRole = "Administrator";
            } else if (window.frappe && window.frappe.user_roles && window.frappe.user_roles.indexOf("SMRITI Cashier") !== -1) {
                userRole = "Cashier";
            } else if (window.frappe && window.frappe.user_roles && window.frappe.user_roles.indexOf("SMRITI Store Manager") !== -1) {
                userRole = "Store Manager";
            }

            html.push('<div class="smriti-sidebar-footer">');
            // Notification Bell
            html.push('  <a class="smriti-notif-bell" href="/smriti-notifications" id="smriti-notif-bell" title="Notification Center">');
            html.push('    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>');
            html.push('    <span class="smriti-notif-badge" id="smriti-notif-badge" style="display:none;">0</span>');
            html.push('  </a>');
            // User Avatar → Profile
            html.push('  <a class="smriti-sidebar-user" href="/smriti-profile" title="My Profile" style="text-decoration:none;cursor:pointer;">');
            html.push('    <div class="smriti-sidebar-user-avatar">' + firstChar + '</div>');
            html.push('    <div class="smriti-sidebar-user-info">');
            html.push('      <span class="smriti-sidebar-user-name">' + userFullName + '</span>');
            html.push('      <span class="smriti-sidebar-user-role">' + userRole + '</span>');
            html.push('    </div>');
            html.push('  </a>');
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

            // Global Keyboard Shortcut: Toggle Sidebar with Ctrl+B / Cmd+B
            function handleGlobalKeyDown(e) {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
                    var activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
                    if (activeTag === "input" || activeTag === "textarea") return;

                    e.preventDefault();
                    var btn = target.querySelector("#smriti-sidebar-toggle");
                    if (btn) btn.click();
                }
            }
            if (target._smritiSidebarShortcutHandler) {
                document.removeEventListener("keydown", target._smritiSidebarShortcutHandler);
            }
            target._smritiSidebarShortcutHandler = handleGlobalKeyDown;
            document.addEventListener("keydown", handleGlobalKeyDown);

            // 2. Expand/Collapse Section Groups
            var headers = target.querySelectorAll(".smriti-sidebar-group-header");
            headers.forEach(function (hdr) {
                hdr.addEventListener("click", function () {
                    if (target.classList.contains("collapsed")) return;

                    var groupEl = hdr.parentElement;
                    var groupId = groupEl.getAttribute("data-group-id");
                    var isCollapsedNow = groupEl.classList.toggle("collapsed");
                    hdr.setAttribute("aria-expanded", isCollapsedNow ? "false" : "true");

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

            // Keyboard Navigation (ArrowUp / ArrowDown)
            var contentContainer = target.querySelector(".smriti-sidebar-content");
            if (contentContainer) {
                contentContainer.addEventListener("keydown", function (e) {
                    if (e.key !== "ArrowDown" && e.key !== "ArrowUp" && e.key !== "Enter" && e.key !== " ") return;

                    var activeEl = document.activeElement;
                    if (!activeEl || !contentContainer.contains(activeEl)) return;

                    // Find all visible focusable treeitems
                    var items = Array.prototype.slice.call(contentContainer.querySelectorAll('[role="treeitem"]')).filter(function (el) {
                        var parentGroup = el.closest(".smriti-sidebar-group");
                        if (parentGroup && parentGroup.classList.contains("collapsed") && el.classList.contains("smriti-sidebar-item")) {
                            return false;
                        }
                        return el.offsetWidth > 0 || el.offsetHeight > 0;
                    });

                    var index = items.indexOf(activeEl);
                    if (index === -1) return;

                    if (e.key === "ArrowDown") {
                        e.preventDefault();
                        var nextIndex = (index + 1) % items.length;
                        items[nextIndex].focus();
                    } else if (e.key === "ArrowUp") {
                        e.preventDefault();
                        var prevIndex = (index - 1 + items.length) % items.length;
                        items[prevIndex].focus();
                    } else if (e.key === "Enter" || e.key === " ") {
                        if (activeEl.classList.contains("smriti-sidebar-group-header")) {
                            e.preventDefault();
                            activeEl.click();
                        }
                    }
                });
            }

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

            // 7. Notification Bell Badge — hydrate on render + real-time
            SMRITI._hydrateNotifBadge();

            // 8. Position Picker — click handlers
            target.querySelectorAll(".smriti-pos-btn").forEach(function(btn) {
                btn.addEventListener("click", function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    var pos = btn.getAttribute("data-pos");
                    if (pos) SMRITI.setSidebarPosition(pos);
                });
            });

            // 9. Restore saved position on every render
            SMRITI.setSidebarPosition(localStorage.getItem("smriti-sidebar-position") || "left");
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

    // ── Position toggle handler — supports left/right/top/bottom ──
    SMRITI.setSidebarPosition = function (pos) {
        // Apply to both #app and body — works on all SMRITI page types
        var targets = [
            document.getElementById("app"),
            document.getElementById("smriti-app"),
            document.body
        ].filter(Boolean);

        var allCls = ["sidebar-position-right", "sidebar-position-top", "sidebar-position-bottom"];

        targets.forEach(function(el) {
            allCls.forEach(function(cls) { el.classList.remove(cls); });
            if (pos === "right")  el.classList.add("sidebar-position-right");
            if (pos === "top")    el.classList.add("sidebar-position-top");
            if (pos === "bottom") el.classList.add("sidebar-position-bottom");
        });

        localStorage.setItem("smriti-sidebar-position", pos);

        // Update the active state on position buttons
        document.querySelectorAll(".smriti-pos-btn").forEach(function(btn) {
            btn.classList.toggle("active", btn.getAttribute("data-pos") === pos);
        });
    };

    // Backward compat — left/right binary toggle
    SMRITI.toggleSidebarPosition = function () {
        var cur = localStorage.getItem("smriti-sidebar-position") || "left";
        SMRITI.setSidebarPosition(cur === "left" ? "right" : "left");
    };

    SMRITI.toggleSidebarCollapse = function () {
        var toggleBtn = document.getElementById("smriti-sidebar-toggle");
        if (toggleBtn) toggleBtn.click();
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

    window.addEventListener('hashchange', function() {
        if (window.SMRITI_NAV_DATA) {
            buildTree(window.SMRITI_NAV_DATA);
        }
    });

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

    // ── Notification Bell Badge Hydration ──────────────────────────────────
    SMRITI._notifBadgeInterval = null;

    SMRITI._hydrateNotifBadge = function () {
        if (!window.frappe || !frappe.call) return;

        function updateBadge() {
            frappe.call({
                method: "smriti_retail_os.notification_studio.api.notifications.get_unread_badge",
                callback: function (r) {
                    if (!r || !r.message) return;
                    var cnt = r.message.count || 0;
                    var badge = document.getElementById("smriti-notif-badge");
                    if (badge) {
                        badge.textContent = cnt > 99 ? "99+" : cnt;
                        badge.style.display = cnt > 0 ? "inline-flex" : "none";
                    }
                }
            });
        }

        // Initial fetch
        updateBadge();

        // Real-time — update badge when a new notification arrives
        if (frappe.realtime) {
            frappe.realtime.on("smriti_notification", function () {
                updateBadge();
            });
        }

        // Polling fallback every 60s (in case realtime is not available)
        if (SMRITI._notifBadgeInterval) clearInterval(SMRITI._notifBadgeInterval);
        SMRITI._notifBadgeInterval = setInterval(updateBadge, 60000);
    };

    // ── Inject Bell + User Avatar CSS (once) ──────────────────────────────
    (function injectSidebarExtCSS() {
        if (document.getElementById("smriti-sidebar-ext-css")) return;
        var style = document.createElement("style");
        style.id = "smriti-sidebar-ext-css";
        style.textContent = [
            ".smriti-sidebar-footer { display:flex; align-items:center; gap:8px; padding:12px 14px; border-top:1px solid rgba(255,255,255,0.07); }",
            ".smriti-notif-bell { position:relative; display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:9px; color:rgba(148,163,184,0.8); transition:all 0.15s; text-decoration:none; flex-shrink:0; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.07); }",
            ".smriti-notif-bell:hover { background:rgba(37,99,235,0.12); color:#2563EB; border-color:rgba(37,99,235,0.3); }",
            ".smriti-notif-badge { position:absolute; top:-4px; right:-4px; min-width:16px; height:16px; background:#ef4444; color:#fff; border-radius:8px; font-size:9px; font-weight:700; padding:0 3px; display:inline-flex; align-items:center; justify-content:center; border:2px solid var(--sidebar-bg,#0f1729); animation:smriti-badge-pop 0.2s ease; }",
            "@keyframes smriti-badge-pop { from{transform:scale(0.5);opacity:0;} to{transform:scale(1);opacity:1;} }",
            ".smriti-sidebar-user { display:flex; align-items:center; gap:8px; flex:1; min-width:0; padding:6px 8px; border-radius:9px; transition:background 0.15s; text-decoration:none; color:inherit; }",
            ".smriti-sidebar-user:hover { background:rgba(37,99,235,0.08); }",
            ".smriti-sidebar-user-avatar { width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#2563EB,#7c3aed); display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; color:#fff; flex-shrink:0; }",
            ".smriti-sidebar-user-info { display:flex; flex-direction:column; overflow:hidden; }",
            ".smriti-sidebar-user-name { font-size:12px; font-weight:600; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }",
            ".smriti-sidebar-user-role { font-size:10px; color:#64748b; }",
            ".smriti-sidebar.collapsed .smriti-sidebar-user-info { display:none; }",
            ".smriti-sidebar.collapsed .smriti-notif-bell { width:32px; height:32px; }",
        ].join("\n");
        document.head.appendChild(style);
    })();

}(window.SMRITI));
