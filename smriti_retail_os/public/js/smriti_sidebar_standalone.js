/**
 * @file: smriti_retail_os/public/js/smriti_sidebar_standalone.js
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
        if (!target) return;

        // Apply sidebar class to container
        target.classList.add("smriti-sidebar");

        var user = (window.frappe && window.frappe.session && window.frappe.session.user) || "Administrator";
        var bootNav = window.frappe && window.frappe.boot && window.frappe.boot.smriti_navigation;

        if (bootNav) {
            buildTree(bootNav);
        } else if (window.SMRITI_NAV_DATA) {
            buildTree(window.SMRITI_NAV_DATA);
        } else {
            // Use fetch() — works on both standalone www pages and Frappe Desk.
            // frappe.call requires a full Frappe boot; www pages only have a partial
            // frappe object with no boot, causing silent empty sidebars.
            var user = (window.frappe && window.frappe.session && window.frappe.session.user) || "Administrator";
            var csrfToken = (window.frappe && window.frappe.csrf_token) || getCsrfFromCookie();
            fetch("/api/method/smriti_retail_os.navigation.navigation_service.get_user_navigation"
                + "?user=" + encodeURIComponent(user), {
                method: "GET",
                headers: {
                    "X-Frappe-CSRF-Token": csrfToken || "fetch",
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            })
            .then(function(resp) {
                if (!resp.ok) throw new Error("Navigation API " + resp.status);
                return resp.json();
            })
            .then(function(data) {
                if (data && data.message) {
                    buildTree(data.message);
                }
            })
            .catch(function(err) {
                console.error("[SMRITI Sidebar] Failed to load navigation:", err);
            });
        }

        function getCsrfFromCookie() {
            var match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/);
            return match ? decodeURIComponent(match[1]) : null;
        }

        function buildTree(navData) {
            if (!navData || !navData.sections) return;
            window.SMRITI_NAV_DATA = navData;

            var activeRoute = window.location.pathname + window.location.hash;
            var collapsedGroupIds = JSON.parse(localStorage.getItem("smriti-sidebar-collapsed-groups") || "[]");
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
                    var isItemActive = (item.id === activePageId || item.route === activeRoute || item.standalone_route === activeRoute);
                    var itemRoute = item.route || "#";
                    html.push('<a class="smriti-sidebar-item' + (isItemActive ? ' active' : '') + '" href="' + itemRoute + '" role="treeitem" tabindex="0"' + (isItemActive ? ' aria-current="page"' : '') + '>');
                    html.push('  <div class="smriti-sidebar-item-icon">' + (ICONS[p.sec.id] || ICONS.default) + '</div>');
                    html.push('  <span class="smriti-sidebar-item-label">' + item.label + '</span>');
                    if (item.badge) {
                        html.push('  <span class="smriti-nav-badge">' + item.badge + '</span>');
                    }
                    html.push('  <div class="smriti-sidebar-item-actions">');
                    html.push('    <button class="smriti-popout-icon-btn" onclick="SMRITI.triggerPopout(event, \'' + itemRoute + '\')" title="Open in Popout Window">📺</button>');
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

                    var isComingSoon = (item.status === "coming_soon");
                    var isItemActive = !isComingSoon && (item.id === activePageId || item.route === activeRoute || item.standalone_route === activeRoute);
                    var iconHtml = ICONS[sec.id] || ICONS.default;
                    var itemRoute = isComingSoon ? "/smriti-coming-soon" : (item.route || "#");
                    var itemClasses = "smriti-sidebar-item" + (isItemActive ? " active" : "") + (isComingSoon ? " coming-soon" : "");
                    var titleAttr = isComingSoon ? (item.eta ? " title=\"Coming " + item.eta + "\"" : " title=\"Coming Soon\"") : "";

                    html.push('<a class="' + itemClasses + '" href="' + itemRoute + '" role="treeitem" tabindex="' + (isComingSoon ? '-1' : '0') + '"' + (isItemActive ? ' aria-current="page"' : '') + titleAttr + '>');
                    html.push('  <div class="smriti-sidebar-item-icon">' + iconHtml + '</div>');
                    html.push('  <span class="smriti-sidebar-item-label">' + item.label + '</span>');
                    if (item.badge) {
                        var badgeClass = isComingSoon ? 'smriti-nav-badge smriti-nav-badge--soon' : 'smriti-nav-badge';
                        html.push('  <span class="' + badgeClass + '">' + item.badge + '</span>');
                    }
                    if (!isComingSoon) {
                        var isFav = favorites.indexOf(item.id) !== -1;
                        html.push('  <div class="smriti-sidebar-item-actions">');
                        html.push('    <button class="smriti-popout-icon-btn" onclick="SMRITI.triggerPopout(event, \'' + itemRoute + '\')" title="Open in Popout Window">📺</button>');
                        html.push('    <button class="smriti-star-btn' + (isFav ? ' active' : '') + '" data-item-id="' + item.id + '" title="' + (isFav ? 'Unpin' : 'Pin to Favorites') + '">' + (isFav ? '⭐' : '☆') + '</button>');
                        html.push('  </div>');
                    }
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
            }

            html.push('<div class="smriti-sidebar-footer">');
            html.push('  <a href="/smriti-profile" class="smriti-sidebar-user" title="My Profile" style="text-decoration:none;cursor:pointer;">');
            html.push('    <div class="smriti-sidebar-user-avatar" id="smriti-user-avatar">' + firstChar + '</div>');
            html.push('    <div class="smriti-sidebar-user-info">');
            html.push('      <span class="smriti-sidebar-user-name">' + userFullName + '</span>');
            html.push('      <span class="smriti-sidebar-user-role">' + userRole + '</span>');
            html.push('    </div>');
            html.push('  </a>');
            html.push('  <div class="smriti-sidebar-footer-actions">');
            html.push('    <a href="/smriti-notifications" id="smriti-notif-bell" class="smriti-footer-icon-btn" title="Notifications" style="position:relative;text-decoration:none;">');
            html.push('      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>');
            html.push('      <span id="smriti-notif-badge" class="smriti-notif-badge" style="display:none;"></span>');
            html.push('    </a>');
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

            // 3. Theme switching pills click & active state sync
            var updateActiveThemePills = function(currentTheme) {
                var themeKey = currentTheme || (window.SMRITI && window.SMRITI.getCurrentTheme ? window.SMRITI.getCurrentTheme() : "sleek-compact");
                var pills = target.querySelectorAll(".smriti-standalone-theme-pill");
                pills.forEach(function (p) {
                    if (p.getAttribute("data-theme") === themeKey) {
                        p.classList.add("active");
                    } else {
                        p.classList.remove("active");
                    }
                });
            };

            var themePills = target.querySelectorAll(".smriti-standalone-theme-pill");
            themePills.forEach(function (pill) {
                pill.addEventListener("click", function () {
                    var themeKey = pill.getAttribute("data-theme");
                    if (window.SMRITI && window.SMRITI.switchTheme) {
                        window.SMRITI.switchTheme(themeKey);
                        updateActiveThemePills(themeKey);
                    }
                });
            });

            updateActiveThemePills();
            document.addEventListener("smriti-theme-changed", function(e) {
                if (e.detail && e.detail.theme) updateActiveThemePills(e.detail.theme);
            });

            // 4. Handle explain button injection if relevant
            if (window.SMRITI.injectExplainScreenButton) {
                window.SMRITI.injectExplainScreenButton(activePageId);
            }

            // Favorites — Star button handler
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
                    buildTree(navData);
                });
            });

            // 5. Position Picker — click handlers
            target.querySelectorAll(".smriti-pos-btn").forEach(function(btn) {
                btn.addEventListener("click", function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    var pos = btn.getAttribute("data-pos");
                    if (pos && window.SMRITI.setSidebarPosition) {
                        SMRITI.setSidebarPosition(pos);
                    }
                });
            });

            // 6. Restore saved position on every render
            if (window.SMRITI.setSidebarPosition) {
                SMRITI.setSidebarPosition(localStorage.getItem("smriti-sidebar-position") || "left");
            }

            // 7. Notification Badge — hydrate
            (function() {
                var badge = document.getElementById("smriti-notif-badge");
                if (!badge) return;
                try {
                    frappe.call({
                        method: "smriti_retail_os.notification_studio.api.notifications.get_unread_count",
                        callback: function(r) {
                            if (r && r.message && r.message.count > 0) {
                                badge.textContent = r.message.count > 9 ? "9+" : r.message.count;
                                badge.style.display = "flex";
                            } else {
                                badge.style.display = "none";
                            }
                        },
                        error: function() {
                            if (badge) badge.style.display = "none";
                        }
                    });
                } catch(e) {}
            })();
        }
    };

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

    // ── Position toggle — supports left/right/top/bottom ──
    SMRITI.setSidebarPosition = SMRITI.setSidebarPosition || function (pos) {
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
        document.querySelectorAll(".smriti-pos-btn").forEach(function(btn) {
            btn.classList.toggle("active", btn.getAttribute("data-pos") === pos);
        });
    };

    // Backward compat — left/right only
    SMRITI.toggleSidebarPosition = function () {
        var cur = localStorage.getItem("smriti-sidebar-position") || "left";
        SMRITI.setSidebarPosition(cur === "left" ? "right" : "left");
    };

    SMRITI.toggleSidebarCollapse = function () {
        var toggleBtn = document.getElementById("smriti-sidebar-toggle");
        if (toggleBtn) toggleBtn.click();
    };

    // ── Popout Window Logic ──
    // @deprecated 2026-07-01 — zero call sites found anywhere in repo.
    // triggerPopout is fully implemented but unreachable: no button, link, or
    // menu item invokes it. Do NOT remove — keep for future UX wiring.
    // To enable: add a button with onclick="SMRITI.triggerPopout(event, '/target-page')"
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
            SMRITI.renderFlexibleSidebar();
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

    // ── Keyboard Shortcuts (Ctrl+H to toggle collapse, Ctrl+Arrow to change position) ──
    document.addEventListener("keydown", function (e) {
        var activeEl = document.activeElement;
        if (activeEl && (
            activeEl.tagName === "INPUT" || 
            activeEl.tagName === "TEXTAREA" || 
            activeEl.contentEditable === "true" ||
            activeEl.tagName === "SELECT"
        )) {
            return;
        }

        var isCtrl = e.ctrlKey || e.metaKey;
        if (!isCtrl) return;

        var key = e.key.toLowerCase();

        if (key === "h") {
            e.preventDefault();
            SMRITI.toggleSidebarCollapse();
            return;
        }

        if (e.key === "ArrowLeft") {
            e.preventDefault();
            if (SMRITI.setSidebarPosition) SMRITI.setSidebarPosition("left");
            return;
        }
        if (e.key === "ArrowRight") {
            e.preventDefault();
            if (SMRITI.setSidebarPosition) SMRITI.setSidebarPosition("right");
            return;
        }
        if (e.key === "ArrowUp") {
            e.preventDefault();
            if (SMRITI.setSidebarPosition) SMRITI.setSidebarPosition("top");
            return;
        }
        if (e.key === "ArrowDown") {
            e.preventDefault();
            if (SMRITI.setSidebarPosition) SMRITI.setSidebarPosition("bottom");
            return;
        }
    });

    // ── Voucher Sharing Observer & Actions ──
    function hijackDetailLoaders() {
        const loaders = {
            loadInvoiceDetails: "activeInvoiceName",
            loadPaymentDetails: "activePaymentName",
            loadChallanDetails: "activeChallanName",
            loadSODetails: "activeSOName",
            loadQuotationDetails: "activeQuotationName",
            loadReturnDetails: "activeReturnName"
        };
        for (const [funcName, winKey] of Object.entries(loaders)) {
            if (typeof window[funcName] === "function" && !window[funcName].hijacked) {
                const original = window[funcName];
                window[funcName] = function(id) {
                    window[winKey] = id;
                    return original.apply(this, arguments);
                };
                window[funcName].hijacked = true;
            }
        }
    }
    hijackDetailLoaders();
    document.addEventListener("DOMContentLoaded", hijackDetailLoaders);

    function getActiveDocInfo() {
        const path = window.location.pathname;
        if (path.includes("/sales_invoices")) {
            return { doctype: "Sales Invoice", name: window.activeInvoiceName || (window.activeInvoiceDoc ? window.activeInvoiceDoc.name : null) };
        } else if (path.includes("/purchase_invoice")) {
            return { doctype: "Purchase Invoice", name: window.activeInvoiceName || (window.activeInvoiceDoc ? window.activeInvoiceDoc.name : null) };
        } else if (path.includes("/payments")) {
            return { doctype: "Payment Entry", name: window.activePaymentName || (window.activePaymentDoc ? window.activePaymentDoc.name : null) };
        } else if (path.includes("/sales_orders")) {
            return { doctype: "Sales Order", name: window.activeSOName || (window.S && window.S.activeSO ? window.S.activeSO.name : null) };
        } else if (path.includes("/sales_return")) {
            return { doctype: "Sales Invoice", name: window.activeReturnName || (window.activeReturnDoc ? window.activeReturnDoc.name : null) };
        } else if (path.includes("/supplier_returns")) {
            return { doctype: "Purchase Receipt", name: window.activeReturnName || (window.activeReturnDoc ? window.activeReturnDoc.name : null) };
        } else if (path.includes("/delivery_challan")) {
            return { doctype: "Delivery Note", name: window.activeChallanName || (window.activeChallanDoc ? window.activeChallanDoc.name : null) };
        } else if (path.includes("/eway_bill")) {
            return { doctype: "Sales Invoice", name: window.activeInvoiceName || (window.activeInvoiceDoc ? window.activeInvoiceDoc.name : null) };
        } else if (path.includes("/smriti-quotation")) {
            return { doctype: "Quotation", name: window.activeQuotationName || (window.S && window.S.activeQ ? window.S.activeQ.name : null) };
        }
        return null;
    }

    // ── Print Guard Helpers ──

    /** Show a branded SMRITI modal instead of alert/confirm */
    function _showPrintGuardModal({ heading, reason, detail, doctype, docname, onSave, onClose }) {
        const existing = document.getElementById("smriti-print-guard-modal");
        if (existing) existing.remove();

        const overlay = document.createElement("div");
        overlay.id = "smriti-print-guard-modal";
        overlay.style.cssText = [
            "position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;",
            "background:rgba(10,15,30,0.85);backdrop-filter:blur(8px);",
            "animation:smriti-fadein 0.2s ease;"
        ].join("");

        overlay.innerHTML = `
            <style>
                @keyframes smriti-fadein{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
                #smriti-print-guard-modal .spg-card{
                    background:linear-gradient(135deg,#111827,#0f172a);
                    border:1px solid rgba(239,68,68,0.25);
                    border-radius:16px;padding:40px 36px;max-width:480px;width:90%;
                    box-shadow:0 24px 64px rgba(0,0,0,0.6),0 0 80px rgba(239,68,68,0.06);
                    font-family:'Inter',sans-serif;color:#e2e8f0;
                }
                #smriti-print-guard-modal .spg-icon{width:64px;height:64px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);margin:0 auto 20px;}
                #smriti-print-guard-modal .spg-icon .material-symbols-outlined{font-size:32px;color:#ef4444;}
                #smriti-print-guard-modal .spg-title{font-size:20px;font-weight:700;color:#f1f5f9;text-align:center;margin-bottom:6px;}
                #smriti-print-guard-modal .spg-reason{font-size:13px;color:#ef4444;font-weight:600;text-align:center;margin-bottom:16px;}
                #smriti-print-guard-modal .spg-divider{height:1px;background:rgba(255,255,255,0.07);margin:12px 0;}
                #smriti-print-guard-modal .spg-detail{font-size:13px;color:#94a3b8;line-height:1.6;text-align:center;margin-bottom:24px;}
                #smriti-print-guard-modal .spg-actions{display:flex;gap:10px;}
                #smriti-print-guard-modal .spg-btn{flex:1;display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:10px 16px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none;font-family:inherit;transition:all .15s;}
                #smriti-print-guard-modal .spg-btn-primary{background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#fff;box-shadow:0 4px 12px rgba(37,99,235,.3);}
                #smriti-print-guard-modal .spg-btn-primary:hover{background:linear-gradient(135deg,#1d4ed8,#1e40af);transform:translateY(-1px);}
                #smriti-print-guard-modal .spg-btn-ghost{background:rgba(255,255,255,.07);color:#94a3b8;border:1px solid rgba(255,255,255,.1);}
                #smriti-print-guard-modal .spg-btn-ghost:hover{background:rgba(255,255,255,.12);color:#e2e8f0;}
                #smriti-print-guard-modal .spg-offline{display:none;background:rgba(234,179,8,.1);border:1px solid rgba(234,179,8,.3);border-radius:8px;padding:12px;font-size:12px;color:#fbbf24;text-align:center;margin-bottom:16px;}
                #smriti-print-guard-modal .spg-offline.show{display:block;}
                #smriti-print-guard-modal .spg-log-tag{text-align:center;margin-top:20px;font-size:11px;color:#475569;}
            </style>
            <div class="spg-card">
                <div class="spg-icon"><span class="material-symbols-outlined">print_disabled</span></div>
                <div class="spg-title">${heading || 'Unable to print'}</div>
                <div class="spg-reason">${reason || ''}</div>
                <div class="spg-divider"></div>
                <div class="spg-offline ${!navigator.onLine ? 'show' : ''}" id="spg-offline-note">
                    ⚠️ You appear to be <strong>offline</strong>. The voucher may exist locally but cannot be verified or printed right now.
                </div>
                <div class="spg-detail">${detail || ''}</div>
                <div class="spg-actions">
                    <button class="spg-btn spg-btn-primary" id="spg-btn-save">
                        <span class="material-symbols-outlined" style="font-size:15px">save</span> Save Voucher
                    </button>
                    <button class="spg-btn spg-btn-ghost" id="spg-btn-close">
                        <span class="material-symbols-outlined" style="font-size:15px">close</span> Close
                    </button>
                </div>
                <div class="spg-log-tag">🔒 This attempt has been logged for diagnostics</div>
            </div>`;

        document.body.appendChild(overlay);

        overlay.querySelector("#spg-btn-save").addEventListener("click", () => {
            overlay.remove();
            if (typeof onSave === "function") onSave();
        });
        overlay.querySelector("#spg-btn-close").addEventListener("click", () => {
            overlay.remove();
            if (typeof onClose === "function") onClose();
        });
        overlay.addEventListener("click", (e) => { if (e.target === overlay) overlay.remove(); });

        window.addEventListener("offline", () => {
            const note = overlay.querySelector("#spg-offline-note");
            if (note) note.classList.add("show");
        });
    }

    /** Async: verify doc exists via API, log the attempt, then open /printview */
    async function handleSharePrint(doctype, name) {
        if (!doctype || !name) return;

        // Guard: offline detection
        if (!navigator.onLine) {
            _showPrintGuardModal({
                heading: "Print Preview Unavailable",
                reason: "You are currently offline.",
                detail: "Please reconnect to the network and try again, or sync the voucher first.",
                doctype, docname: name
            });
            return;
        }

        try {
            const check = await smriti.api.call(
                "smriti_retail_os.print_framework.api.print_api.check_doc_exists",
                { doctype, docname: name }
            );

            if (!check || !check.exists) {
                // Log the failed attempt
                smriti.api.call(
                    "smriti_retail_os.print_framework.api.print_api.log_print_attempt",
                    { doctype, docname: name, exists: 0, action: "PRINT" }
                ).catch(() => {});

                _showPrintGuardModal({
                    heading: "Unable to open document",
                    reason: "The requested voucher could not be found.",
                    detail: "This usually happens when the voucher has not yet been saved to the database. Please save the voucher and try again.",
                    doctype, docname: name
                });
                return;
            }

            // Log successful attempt
            smriti.api.call(
                "smriti_retail_os.print_framework.api.print_api.log_print_attempt",
                { doctype, docname: name, exists: 1, action: "PRINT" }
            ).catch(() => {});

            const url = `/printview?doctype=${encodeURIComponent(doctype)}&name=${encodeURIComponent(name)}`;
            window.open(url, "_blank");

        } catch (err) {
            console.warn("[SMRITI Print Guard] check_doc_exists failed:", err);
            // Fallback: open anyway (don't block if API itself is unavailable)
            const url = `/printview?doctype=${encodeURIComponent(doctype)}&name=${encodeURIComponent(name)}`;
            window.open(url, "_blank");
        }
    }

    async function handleShareWhatsApp(doctype, name) {
        if (!doctype || !name) return;

        // Guard: offline
        if (!navigator.onLine) {
            _showPrintGuardModal({
                heading: "WhatsApp Share Unavailable",
                reason: "You are currently offline.",
                detail: "WhatsApp sharing requires an active internet connection. Please reconnect and try again.",
                doctype, docname: name
            });
            return;
        }

        // Guard: document must exist
        try {
            const check = await smriti.api.call(
                "smriti_retail_os.print_framework.api.print_api.check_doc_exists",
                { doctype, docname: name }
            );
            if (!check || !check.exists) {
                smriti.api.call("smriti_retail_os.print_framework.api.print_api.log_print_attempt",
                    { doctype, docname: name, exists: 0, action: "WHATSAPP" }).catch(() => {});
                _showPrintGuardModal({
                    heading: "Unable to share via WhatsApp",
                    reason: "The requested voucher could not be found.",
                    detail: "Please save the voucher first, then try sharing again.",
                    doctype, docname: name
                });
                return;
            }
        } catch (e) { /* proceed if API unavailable */ }

        const phone = prompt("Enter recipient WhatsApp number (with country code, e.g. 919876543210):");
        if (!phone) return;

        try {
            const res = await smriti.api.call("smriti_retail_os.print_framework.api.print_api.share_via_whatsapp", {
                doctype: doctype,
                docname: name,
                phone: phone
            });
            smriti.api.call("smriti_retail_os.print_framework.api.print_api.log_print_attempt",
                { doctype, docname: name, exists: 1, action: "WHATSAPP" }).catch(() => {});
            if (res && res.file_url) {
                const message = encodeURIComponent(`Please find your ${doctype} (${name}) here: ${res.file_url}`);
                const waUrl = `https://api.whatsapp.com/send?phone=${phone}&text=${message}`;
                window.open(waUrl, "_blank");
            } else {
                alert("Failed to generate share link.");
            }
        } catch (err) {
            console.error(err);
            alert("Error sharing: " + err.message);
        }
    }

    async function handleShareEmail(doctype, name) {
        if (!doctype || !name) return;

        // Guard: offline
        if (!navigator.onLine) {
            _showPrintGuardModal({
                heading: "Email Share Unavailable",
                reason: "You are currently offline.",
                detail: "Sending email requires an active internet connection. Please reconnect and try again.",
                doctype, docname: name
            });
            return;
        }

        // Guard: document must exist
        try {
            const check = await smriti.api.call(
                "smriti_retail_os.print_framework.api.print_api.check_doc_exists",
                { doctype, docname: name }
            );
            if (!check || !check.exists) {
                smriti.api.call("smriti_retail_os.print_framework.api.print_api.log_print_attempt",
                    { doctype, docname: name, exists: 0, action: "EMAIL" }).catch(() => {});
                _showPrintGuardModal({
                    heading: "Unable to send Email",
                    reason: "The requested voucher could not be found.",
                    detail: "Please save the voucher first, then try emailing again.",
                    doctype, docname: name
                });
                return;
            }
        } catch (e) { /* proceed if API unavailable */ }

        const email = prompt("Enter recipient email address:");
        if (!email) return;

        try {
            const res = await smriti.api.call("smriti_retail_os.print_framework.api.print_api.share_via_email", {
                doctype: doctype,
                docname: name,
                email: email
            });
            smriti.api.call("smriti_retail_os.print_framework.api.print_api.log_print_attempt",
                { doctype, docname: name, exists: 1, action: "EMAIL" }).catch(() => {});
            if (res && res.success) {
                alert("Email sent successfully.");
            } else {
                alert("Failed to send email.");
            }
        } catch (err) {
            console.error(err);
            alert("Error sending email: " + err.message);
        }
    }

    /**
     * Show a "Save Required" toast in the sharing button instead of
     * navigating when the document is client-side only.
     */
    function _markSharingButtonSaveRequired(btn, originalHTML) {
        btn.disabled = true;
        btn.title = "Save the voucher first";
        btn.style.opacity = "0.55";
        btn.style.cursor = "not-allowed";
        btn.innerHTML = '<span class="material-symbols-outlined" style="font-size:15px;">lock</span> Save Required';
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            _showPrintGuardModal({
                heading: "Save Voucher First",
                reason: "This voucher has not yet been saved.",
                detail: "Please save the voucher before printing, sharing via WhatsApp, or sending via email."
            });
        }, { once: false });
    }

    function injectVoucherActions(backdropEl) {
        const footer = backdropEl.querySelector(".drawer-footer, #drawer-footer-actions, #modal-footer");
        if (!footer) return;
        if (footer.querySelector(".smriti-voucher-sharing")) return;

        const shareContainer = document.createElement("div");
        shareContainer.className = "smriti-voucher-sharing";
        shareContainer.style = "display:flex; gap:8px; margin-top:8px; width:100%; border-top: 1px solid var(--border); padding-top: 12px;";

        const btnPrint = document.createElement("button");
        btnPrint.className = "btn btn-secondary flex-1";
        btnPrint.style = "display:flex; align-items:center; justify-content:center; gap:6px; background:#475569; color:white; padding:8px 12px; border:none; border-radius:6px; cursor:pointer;";
        btnPrint.innerHTML = '<span class="material-symbols-outlined" style="font-size:18px;">print</span> Print';
        btnPrint.addEventListener("click", () => {
            const info = getActiveDocInfo();
            if (info && info.name) {
                handleSharePrint(info.doctype, info.name);
            } else {
                _showPrintGuardModal({
                    heading: "Save Voucher First",
                    reason: "This voucher has not yet been saved.",
                    detail: "Please save the voucher before opening Print Preview."
                });
            }
        });

        const btnWA = document.createElement("button");
        btnWA.className = "btn btn-success flex-1";
        btnWA.style = "display:flex; align-items:center; justify-content:center; gap:6px; background:#10b981; color:white; padding:8px 12px; border:none; border-radius:6px; cursor:pointer;";
        btnWA.innerHTML = '<span class="material-symbols-outlined" style="font-size:18px;">chat</span> WhatsApp';
        btnWA.addEventListener("click", () => {
            const info = getActiveDocInfo();
            if (info && info.name) {
                handleShareWhatsApp(info.doctype, info.name);
            } else {
                _showPrintGuardModal({
                    heading: "Save Voucher First",
                    reason: "This voucher has not yet been saved.",
                    detail: "Please save the voucher before sharing via WhatsApp."
                });
            }
        });

        const btnEmail = document.createElement("button");
        btnEmail.className = "btn btn-primary flex-1";
        btnEmail.style = "display:flex; align-items:center; justify-content:center; gap:6px; background:#3b82f6; color:white; padding:8px 12px; border:none; border-radius:6px; cursor:pointer;";
        btnEmail.innerHTML = '<span class="material-symbols-outlined" style="font-size:18px;">mail</span> Email';
        btnEmail.addEventListener("click", () => {
            const info = getActiveDocInfo();
            if (info && info.name) {
                handleShareEmail(info.doctype, info.name);
            } else {
                _showPrintGuardModal({
                    heading: "Save Voucher First",
                    reason: "This voucher has not yet been saved.",
                    detail: "Please save the voucher before sending via email."
                });
            }
        });

        shareContainer.appendChild(btnPrint);
        shareContainer.appendChild(btnWA);
        shareContainer.appendChild(btnEmail);

        footer.appendChild(shareContainer);
    }

    function initReportsSharing() {
        const printBtn = document.querySelector('button[onclick="printReport()"]');
        if (!printBtn) return;
        const parent = printBtn.parentElement;
        if (!parent || parent.querySelector(".smriti-report-share")) return;

        const shareWrapper = document.createElement("div");
        shareWrapper.className = "smriti-report-share";
        shareWrapper.style = "display:inline-flex; gap:8px;";

        const btnWA = document.createElement("button");
        btnWA.className = "btn-export";
        btnWA.title = "WhatsApp Report";
        btnWA.style = "background:#10b981; border:none; color:white; border-radius:4px; padding:4px 8px; cursor:pointer; display:inline-flex; align-items:center; gap:4px; font-size:13px; font-weight:600;";
        btnWA.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px;">chat</span> WhatsApp';
        btnWA.addEventListener("click", () => shareReport("whatsapp"));

        const btnEmail = document.createElement("button");
        btnEmail.className = "btn-export";
        btnEmail.title = "Email Report";
        btnEmail.style = "background:#3b82f6; border:none; color:white; border-radius:4px; padding:4px 8px; cursor:pointer; display:inline-flex; align-items:center; gap:4px; font-size:13px; font-weight:600;";
        btnEmail.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px;">mail</span> Email';
        btnEmail.addEventListener("click", () => shareReport("email"));

        shareWrapper.appendChild(btnWA);
        shareWrapper.appendChild(btnEmail);
        parent.insertBefore(shareWrapper, printBtn.nextSibling);
    }

    async function loadHtml2Pdf() {
        if (window.html2pdf) return window.html2pdf;
        return new Promise((resolve) => {
            const script = document.createElement("script");
            script.src = "https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js";
            script.onload = () => resolve(window.html2pdf);
            document.head.appendChild(script);
        });
    }

    async function shareReport(mode) {
        if (!window.activeReportKey) {
            alert("No report data loaded.");
            return;
        }

        const targetEl = document.getElementById("report-table-wrapper") || document.querySelector(".table-wrap");
        if (!targetEl) {
            alert("Report element not found.");
            return;
        }

        let inputVal = "";
        if (mode === "whatsapp") {
            inputVal = prompt("Enter recipient WhatsApp number (with country code, e.g. 919876543210):");
        } else {
            inputVal = prompt("Enter recipient email address:");
        }
        if (!inputVal) return;

        const toast = window.toast || ((msg) => alert(msg));
        toast("Generating report PDF...", "info");

        const html2pdf = await loadHtml2Pdf();
        const opt = {
            margin: 10,
            filename: `${window.activeReportKey}_report.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
        };

        try {
            const pdfBlob = await html2pdf().from(targetEl).set(opt).outputPdf('blob');
            const reader = new FileReader();
            reader.readAsDataURL(pdfBlob);
            reader.onloadend = async function() {
                const base64data = reader.result.split(',')[1];
                const fileName = `${window.activeReportKey}_report.pdf`;

                if (mode === "whatsapp") {
                    const res = await smriti.api.call("smriti_retail_os.print_framework.api.print_api.save_pdf_public", {
                        pdf_base64: base64data,
                        file_name: fileName
                    });
                    if (res && res.file_url) {
                        const message = encodeURIComponent(`Please find your Report here: ${res.file_url}`);
                        const waUrl = `https://api.whatsapp.com/send?phone=${inputVal}&text=${message}`;
                        window.open(waUrl, "_blank");
                    } else {
                        alert("Failed to generate WhatsApp link.");
                    }
                } else {
                    const res = await smriti.api.call("smriti_retail_os.print_framework.api.print_api.send_pdf_email", {
                        email_address: inputVal,
                        pdf_base64: base64data,
                        file_name: fileName,
                        subject: `SMRITI Report - ${window.activeReportKey.toUpperCase()}`
                    });
                    if (res && res.success) {
                        alert("Report emailed successfully.");
                    } else {
                        alert("Failed to email report.");
                    }
                }
            };
        } catch (err) {
            console.error(err);
            alert("Error rendering PDF: " + err.message);
        }
    }

    // ── Global Shortcuts FAB Menu ──
    function initGlobalShortcutsMenu() {
        if (document.getElementById("smriti-shortcuts-root")) return;

        const rootDiv = document.createElement("div");
        rootDiv.id = "smriti-shortcuts-root";
        document.body.appendChild(rootDiv);

        const scripts = [
            "https://unpkg.com/react@18/umd/react.production.min.js",
            "https://unpkg.com/react-dom@18/umd/react-dom.production.min.js",
            "https://unpkg.com/framer-motion@10.16.4/dist/framer-motion.js"
        ];

        function loadScriptSeries(urls, callback) {
            if (urls.length === 0) return callback();
            const url = urls.shift();
            if ((url.includes("react.production") && window.React) || 
                (url.includes("react-dom.production") && window.ReactDOM) ||
                (url.includes("framer-motion") && (window.Motion || window.framerMotion))) {
                return loadScriptSeries(urls, callback);
            }
            const script = document.createElement("script");
            script.src = url;
            script.crossOrigin = "anonymous";
            script.onload = () => loadScriptSeries(urls, callback);
            document.head.appendChild(script);
        }

        loadScriptSeries(scripts, () => {
            renderShortcutsReact(rootDiv);
        });
    }

    function renderShortcutsReact(container) {
        const React = window.React;
        const ReactDOM = window.ReactDOM;
        const motion = (window.Motion || window.framerMotion || {}).motion;

        if (!React || !ReactDOM || !motion) {
            console.error("Shortcuts Menu: Failed to load UI dependencies.");
            return;
        }

        function App() {
            const [isOpen, setIsOpen] = React.useState(false);

            const shortcuts = [
                { id: "sale", label: "Quick Sale", icon: "point_of_sale", route: "/billing" },
                { id: "prod", label: "New Product", icon: "add_box", route: "/item_master" },
                { id: "cust", label: "Add Customer", icon: "person_add", route: "/customers" },
                { id: "quote", label: "Create Quote", icon: "request_quote", route: "/smriti-quotation" }
            ];

            const toggleMenu = () => setIsOpen(!isOpen);

            const navigateTo = (route) => {
                setIsOpen(false);
                if (window.smriti && window.smriti.navigation && typeof window.smriti.navigation.go === "function") {
                    window.smriti.navigation.go(route);
                } else {
                    window.location.href = route;
                }
            };

            return React.createElement(
                React.Fragment,
                null,
                isOpen && React.createElement(
                    motion.div,
                    {
                        initial: { opacity: 0 },
                        animate: { opacity: 1 },
                        exit: { opacity: 0 },
                        onClick: toggleMenu,
                        style: {
                            position: "fixed",
                            inset: 0,
                            zIndex: 9998,
                            background: "rgba(3, 7, 18, 0.4)",
                            backdropFilter: "blur(2px)"
                        }
                    }
                ),
                React.createElement(
                    motion.div,
                    {
                        initial: { opacity: 0, scale: 0.85, y: 20 },
                        animate: isOpen ? { opacity: 1, scale: 1, y: 0 } : { opacity: 0, scale: 0.85, y: 20 },
                        transition: { duration: 0.2 },
                        style: {
                            position: "fixed",
                            bottom: "80px",
                            right: "24px",
                            zIndex: 9999,
                            display: isOpen ? "flex" : "none",
                            flexDirection: "column",
                            gap: "8px",
                            pointerEvents: isOpen ? "auto" : "none"
                        }
                    },
                    shortcuts.map((s) =>
                        React.createElement(
                            motion.div,
                            {
                                key: s.id,
                                whileHover: { scale: 1.05, x: -4 },
                                whileTap: { scale: 0.95 },
                                onClick: () => navigateTo(s.route),
                                style: {
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "10px",
                                    background: "var(--smriti-color-bg-primary, #1e293b)",
                                    border: "1px solid var(--smriti-color-border-strong, #334155)",
                                    borderRadius: "8px",
                                    padding: "10px 16px",
                                    color: "var(--smriti-color-text-primary, #f8fafc)",
                                    cursor: "pointer",
                                    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                                    userSelect: "none"
                                }
                            },
                            React.createElement(
                                "span",
                                {
                                    className: "material-symbols-outlined",
                                    style: { color: "var(--smriti-color-brand-light, #a78bfa)", fontSize: "20px" }
                                },
                                s.icon
                            ),
                            React.createElement(
                                "span",
                                { style: { fontSize: "14px", fontWeight: "600" } },
                                s.label
                            )
                        )
                    )
                ),
                React.createElement(
                    motion.button,
                    {
                        whileHover: { scale: 1.1, rotate: isOpen ? -90 : 0 },
                        whileTap: { scale: 0.9 },
                        onClick: toggleMenu,
                        style: {
                            position: "fixed",
                            bottom: "20px",
                            right: "24px",
                            zIndex: 9999,
                            width: "52px",
                            height: "52px",
                            borderRadius: "50%",
                            background: "var(--smriti-color-brand-light, #a78bfa)",
                            border: "none",
                            color: "var(--smriti-color-bg-primary, #0f172a)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer",
                            boxShadow: "0 4px 16px rgba(167, 139, 250, 0.4)",
                            outline: "none"
                        }
                    },
                    React.createElement(
                        "span",
                        {
                            className: "material-symbols-outlined",
                            style: { fontSize: "26px", fontWeight: "bold" }
                        },
                        isOpen ? "close" : "bolt"
                    )
                )
            );
        }

        const root = ReactDOM.createRoot(container);
        root.render(React.createElement(App));
    }

    function runSetup() {
        initGlobalShortcutsMenu();

        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === "attributes" && mutation.attributeName === "class") {
                    const el = mutation.target;
                    if (el.classList.contains("drawer-backdrop") && el.classList.contains("open")) {
                        injectVoucherActions(el);
                    }
                }
            });
        });
        observer.observe(document.body, {
            attributes: true,
            subtree: true,
            attributeFilter: ["class"]
        });

        initReportsSharing();
    }

    if (document.readyState === "complete" || document.readyState === "interactive") {
        runSetup();
    } else {
        document.addEventListener("DOMContentLoaded", runSetup);
    }

}(window.SMRITI));
