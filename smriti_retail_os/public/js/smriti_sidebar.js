/**
 * @file: smriti_retail_os/public/js/smriti_sidebar.js
 * @description: Frontend controller for SMRITI responsive sidebar toggle.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-12
 * @version: 1.9.1
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Sidebar Component
   ============================================================ */

window.SMRITI = window.SMRITI || {};

SMRITI.handleItemClick = function(route) {
    if (route.startsWith("/app/")) {
        const clean = route.replace("/app/", "");
        const parts = clean.split("?");
        const routeParts = parts[0].split("/");
        if (parts[1]) {
            window.location.href = route;
        } else {
            frappe.set_route(routeParts);
        }
    } else {
        window.location.href = route;
    }
};

SMRITI.sidebarSchema = [];


SMRITI.renderSidebar = function(active_page) {
    var sidebar = document.getElementById("smriti-sidebar");
    if (sidebar) {
        // If sidebar is already present, just update active states and close mobile drawer
        SMRITI._updateSidebarActiveState(active_page);
        
        // Optionally fetch and update shift status asynchronously to keep it fresh
        SMRITI._updateShiftStatusAsync();
        return;
    }

    // Shift status fetch
    frappe.call({
        method: "smriti_retail_os.shift_api.get_shift_status",
        callback: function(r) {
            const status = r.message || {
                status: "Closed", cashier: frappe.session.user
            };
            SMRITI._buildSidebarDOM(
                active_page, status
            );
        }
    });
};

function getSidebarCollapsed() {
    try {
        return localStorage.getItem("smriti-sidebar-collapsed") === "true";
    } catch (e) {
        return false;
    }
}

function setSidebarCollapsed(collapsed) {
    try {
        localStorage.setItem("smriti-sidebar-collapsed", collapsed);
    } catch (e) {
        // localStorage unavailable — ignore
    }
}

SMRITI._updateSidebarActiveState = function(active_page) {
    var sidebar = document.getElementById("smriti-sidebar");
    if (!sidebar) return;
    
    // Update active class on items
    sidebar.querySelectorAll(".smriti-side-item, .smriti-side-sub-item").forEach(function(item) {
        if (item.getAttribute("data-id") === active_page) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });
    
    // Close mobile menu drawer on routing
    sidebar.classList.remove("open-mobile");
    document.body.classList.remove("smriti-mobile-sidebar-open");
};

SMRITI._updateShiftStatusAsync = function() {
    frappe.call({
        method: "smriti_retail_os.shift_api.get_shift_status",
        callback: function(r) {
            if (!r.message) return;
            var badge = document.getElementById("smriti-shift-badge");
            if (badge) {
                var shift_status = r.message.status || "Closed";
                badge.textContent = shift_status;
                badge.className = "smriti-side-shift-badge " + (shift_status.toLowerCase() === "open" ? "open" : "closed");
            }
        }
    });
};

SMRITI._setupBackdropDOM = function() {
    var backdrop = document.getElementById("smriti-sidebar-backdrop");
    if (!backdrop) {
        backdrop = document.createElement("div");
        backdrop.id = "smriti-sidebar-backdrop";
        backdrop.className = "smriti-sidebar-backdrop";
        document.body.appendChild(backdrop);
        
        // Clicking backdrop closes the mobile sidebar drawer
        backdrop.addEventListener("click", function() {
            var sidebar = document.getElementById("smriti-sidebar");
            if (sidebar) {
                sidebar.classList.remove("open-mobile");
            }
            document.body.classList.remove("smriti-mobile-sidebar-open");
        });
    }
};

SMRITI.setupMobileToggle = function() {
    // Only proceed if window is small enough or on mobile
    if (window.innerWidth > 768) {
        // Remove any residual mobile hamburger button if present
        document.getElementById("smriti-mobile-hamburger-btn")?.remove();
        return;
    }

    var navbar = document.querySelector(".navbar, header, .navbar-container");
    if (!navbar) return;

    var existing_btn = document.getElementById("smriti-mobile-hamburger-btn");
    if (existing_btn) return;

    var btn = document.createElement("button");
    btn.id = "smriti-mobile-hamburger-btn";
    btn.className = "smriti-mobile-hamburger";
    btn.title = "Toggle Menu";
    btn.innerHTML = '<span class="material-symbols-outlined">menu</span>';
    
    // Add click handler to toggle open mobile drawer
    btn.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        var sidebar = document.getElementById("smriti-sidebar");
        if (sidebar) {
            sidebar.classList.toggle("open-mobile");
            var isOpen = sidebar.classList.contains("open-mobile");
            if (isOpen) {
                document.body.classList.add("smriti-mobile-sidebar-open");
            } else {
                document.body.classList.remove("smriti-mobile-sidebar-open");
            }
        }
    });

    // Insert as the first element in the navbar brand/container
    var brand = navbar.querySelector(".navbar-brand, .brand-logo, .navbar-left");
    if (brand) {
        navbar.insertBefore(btn, brand);
    } else {
        navbar.insertBefore(btn, navbar.firstChild);
    }
};

SMRITI._buildSidebarDOM = function(active_page, shift) {
    // Double check that we don't have multiple sidebars
    document.getElementById("smriti-sidebar")?.remove();

    var sidebar = document.createElement("div");
    sidebar.id = "smriti-sidebar";
    
    // Check if collapsed state is cached
    var is_collapsed = getSidebarCollapsed();
    if (is_collapsed) {
        sidebar.classList.add("collapsed");
        document.body.classList.add("smriti-sidebar-collapsed");
    } else {
        document.body.classList.remove("smriti-sidebar-collapsed");
    }

    // Load stylesheet dynamically if not present
    if (!document.getElementById("smriti-sidebar-styles")) {
        var link = document.createElement("link");
        link.id = "smriti-sidebar-styles";
        link.rel = "stylesheet";
        link.href = "/assets/smriti_retail_os/css/smriti_sidebar.css";
        document.head.appendChild(link);
    }

    var toggle_icon = is_collapsed ? "menu" : "menu_open";
    var brand_html = `
        <div class="smriti-side-brand">
            <img src="/assets/smriti_retail_os/images/logo.svg" class="smriti-side-logo" alt="SMRITI">
            <span class="smriti-side-title">SMRITI Retail OS</span>
            <button class="smriti-side-toggle" title="Collapse Menu">
                <span class="material-symbols-outlined icon">${toggle_icon}</span>
            </button>
        </div>
    `;

    // SECTION EMOJIS
    const SECTION_EMOJIS = {
        "masters": "📦",
        "cge": "📈",
        "psv": "🌐",
        "sales": "🛒",
        "purchase": "📥",
        "inventory": "🏬",
        "finance": "💰",
        "reports": "📑",
        "administration": "⚙️",
        "help_desk": "🆘",
        "ai_hub": "🤖"
    };

    // Site Config feature flags check
    const siteConfig = Object.assign({
        "ai_hub_enabled": false,
        "intelligence_enabled": false,
        "cge_enabled": false
    }, (frappe.boot && frappe.boot.smriti_site_config) || {});

    // Role restrictions for sections
    const user_roles = (frappe.boot && frappe.boot.smriti && frappe.boot.smriti.user_roles) || frappe.user_roles || [];
    const is_admin_account = frappe.session.user === "Admin" || frappe.session.user === "admin@erpnbook.com";
    
    function hasRoleAccess(sectionId) {
        const SECTION_ROLE_RESTRICTIONS = {
            "cge": ["System Manager", "SMRITI Store Manager", "SMRITI Auditor"],
            "psv": ["System Manager", "SMRITI Store Manager"],
            "finance": ["System Manager", "SMRITI Store Manager"],
            "administration": ["System Manager", "SMRITI Store Manager"]
        };
        const allowed = SECTION_ROLE_RESTRICTIONS[sectionId];
        if (!allowed) return true;
        return allowed.some(role => user_roles.includes(role));
    }

    function isItemActive(item, active_page) {
        if (item.id === active_page) return true;
        const pathname = window.location.pathname;
        if (item.route && item.route === pathname) return true;
        if (item.route && pathname.startsWith(item.route + "/")) return true;

        const hash = window.location.hash;
        if (item.route && item.route.startsWith("/app/") && hash) {
            const deskRoute = item.route.replace("/app/", "");
            const cleanHash = hash.replace("#", "").toLowerCase();
            const cleanRoute = deskRoute.toLowerCase();
            if (cleanHash.startsWith("list/" + cleanRoute) || 
                cleanHash.startsWith("form/" + cleanRoute) ||
                cleanHash === cleanRoute || 
                cleanHash === "workspace/" + cleanRoute) {
                return true;
            }
        }
        return false;
    }

    const navConfig = typeof SMRITI_NAV !== 'undefined' ? SMRITI_NAV : { sections: [] };

    var menu_html = '<div class="smriti-side-menu">';

    navConfig.sections.forEach(section => {
        // 1. Hidden sections never render
        if (section.status === "hidden") return;

        // 2. Feature flag check
        const flagKey = section.id + "_enabled";
        if (siteConfig.hasOwnProperty(flagKey) && !siteConfig[flagKey]) return;

        // 3. Role Access check
        if (!hasRoleAccess(section.id)) return;

        // 4. Filter non-hidden items
        const visibleItems = (section.items || []).filter(item => item.status !== "hidden");

        // 5. Auto-hide section if no visible items
        if (visibleItems.length === 0) return;

        const isCatOpen = localStorage.getItem(`smriti-sidebar-cat-${section.id}`) !== 'closed';
        const openCls = isCatOpen ? 'open' : '';

        let isSubActive = false;
        let subItemsHtml = '';

        visibleItems.forEach(item => {
            if (is_admin_account && (item.id === 'security' || item.id === 'security_workflows')) return;

            if (item.type === "header") {
                subItemsHtml += `
                    <div class="smriti-side-sub-header" style="opacity: 0.7; margin-top: 8px; padding-left: 8px; font-weight: 800; font-size: 11px; color: var(--smriti-color-text-muted);">
                        ${item.label}
                    </div>
                `;
                return;
            }

            const isItemActiveFlag = isItemActive(item, active_page);
            if (isItemActiveFlag) isSubActive = true;

            const subActiveCls = isItemActiveFlag ? 'active' : '';

            let item_url = "";
            let item_onclick = "";
            let item_style = "";
            let badge_html = "";

            if (item.status === "active") {
                item_url = item.route;
                item_style = "opacity: 1; cursor: pointer;";
                item_onclick = `event.preventDefault(); SMRITI.handleItemClick('${item.route}');`;
            } else if (item.status === "coming_soon") {
                const comingSoonUrl = "/coming-soon?feature=" +
                    encodeURIComponent(item.label) +
                    "&progress=" + (item.progress || 0) +
                    "&eta=" + encodeURIComponent(item.eta || "Coming Soon");
                item_url = comingSoonUrl;
                item_style = "opacity: 0.6; cursor: pointer;";
                item_onclick = `event.preventDefault(); SMRITI.handleItemClick('${comingSoonUrl}');`;
                badge_html = `<span class="smriti-soon-badge" style="margin-left:auto; background:#EFF6FF; color:#2563EB; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px;">Soon</span>`;
            } else if (item.status === "disabled") {
                item_url = "#";
                item_style = "opacity: 0.4; cursor: not-allowed;";
                item_onclick = "event.preventDefault();";
            }

            subItemsHtml += `
                <a class="smriti-side-sub-item ${subActiveCls}" data-nav-id="${item.id}" data-status="${item.status}" style="${item_style}" href="${item_url}" onclick="${item_onclick}">
                    <span class="side-item-label">${item.label}</span>
                    ${badge_html}
                    ${item.status === 'active' ? `
                    <button class="smriti-side-item-popout" title="Open in Popout Window" onclick="event.preventDefault(); event.stopPropagation(); SMRITI.openPopout('${item_url}');">
                        <span class="material-symbols-outlined" style="font-size:14px;">open_in_new</span>
                    </button>` : ''}
                </a>
            `;
        });

        const headerActiveCls = isSubActive ? 'active' : '';
        const emoji = SECTION_EMOJIS[section.id] || "📁";

        menu_html += `
            <div class="smriti-side-category ${openCls}" id="cat-block-${section.id}" data-nav-id="${section.id}">
                <div class="smriti-side-category-header ${headerActiveCls}" onclick="SMRITI.toggleCategory('${section.id}')">
                    <span class="side-item-emoji">${emoji}</span>
                    <span class="side-item-label">${section.label}</span>
                    <span class="material-symbols-outlined arrow">chevron_right</span>
                </div>
                <div class="smriti-side-category-body">
                    ${subItemsHtml}
                </div>
            </div>
        `;
    });
    menu_html += '</div>';

    var shift_status = shift.status || "Closed";
    var shift_class = shift_status.toLowerCase() === "open" ? "open" : "closed";
    
    var fullname = frappe.session.user_fullname || frappe.session.user || "Cashier";
    var first_letter = fullname.charAt(0).toUpperCase();
    var roles = frappe.user_roles || [];
    var role_label = "Cashier";
    if (roles.includes("SMRITI Store Manager")) {
        role_label = "Store Manager";
    }

    var is_minimalist = document.body.classList.contains("theme-minimalist");
    var style_hybrid_active = is_minimalist ? "" : "active";
    var style_minimalist_active = is_minimalist ? "active" : "";

    var footer_html = `
        <div class="smriti-side-footer">
            <div class="smriti-side-shift" style="cursor: pointer;" onclick="frappe.set_route('smriti-shift')" title="Open Shift Page">
                <span>Shift:</span>
                <span class="smriti-side-shift-badge ${shift_class}" id="smriti-shift-badge">${shift_status}</span>
            </div>
            
            <div class="smriti-side-theme-toggle-bar">
                <button class="smriti-side-theme-pill ${style_hybrid_active}" data-style="hybrid" title="Tactile Neumorphic Hybrid Theme">
                    <span>🎛️ Hybrid</span>
                </button>
                <button class="smriti-side-theme-pill ${style_minimalist_active}" data-style="minimalist" title="Clean Minimalist Enterprise Theme">
                    <span>🖥️ Minimal</span>
                </button>
            </div>
 
            <div class="smriti-side-cashier">
                <div class="smriti-side-avatar" id="smriti-cashier-avatar">${first_letter}</div>
                <div class="smriti-side-info">
                    <span class="smriti-side-name" id="smriti-cashier-name">${fullname}</span>
                    <span class="smriti-side-role" id="smriti-cashier-role">${role_label}</span>
                </div>
            </div>
            <button class="smriti-side-logout" title="Sign Out">
                <span class="material-symbols-outlined icon">logout</span>
                <span>Logout</span>
            </button>
        </div>
    `;

    sidebar.innerHTML = brand_html + menu_html + footer_html;
    document.body.appendChild(sidebar);

    // Setup backdrop overlay DOM element and listeners
    SMRITI._setupBackdropDOM();

    // Setup mobile toggle hamburger button in the navbar
    SMRITI.setupMobileToggle();

    // Bind event listeners
    var toggle_btn = sidebar.querySelector(".smriti-side-toggle");
    if (toggle_btn) {
        toggle_btn.addEventListener("click", function() {
            sidebar.classList.toggle("collapsed");
            var collapsed = sidebar.classList.contains("collapsed");
            setSidebarCollapsed(collapsed);
            
            if (collapsed) {
                document.body.classList.add("smriti-sidebar-collapsed");
            } else {
                document.body.classList.remove("smriti-sidebar-collapsed");
            }
            
            var icon_el = toggle_btn.querySelector(".icon");
            if (icon_el) {
                icon_el.textContent = collapsed ? "menu" : "menu_open";
            }
        });
    }

    var logout_btn = sidebar.querySelector(".smriti-side-logout");
    if (logout_btn) {
        logout_btn.addEventListener("click", function() {
            frappe.confirm(__('Are you sure you want to log out from SMRITI Retail OS?'), function() {
                frappe.app.logout();
            });
        });
    }

    // Bind Popout Button click listeners
    $(sidebar).on("click", ".smriti-side-item-popout", function(e) {
        e.preventDefault();
        e.stopPropagation();
        var url = $(this).attr("data-url");
        SMRITI.openPopout(url);
    });

    // Bind Theme Toggle click listeners
    $(sidebar).on("click", ".smriti-side-theme-pill", function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var style = $(this).attr("data-style");
        sidebar.querySelectorAll(".smriti-side-theme-pill").forEach(function(pill) {
            if (pill.getAttribute("data-style") === style) {
                pill.classList.add("active");
            } else {
                pill.classList.remove("active");
            }
        });

        if (style === "minimalist") {
            document.body.classList.add("theme-minimalist");
            localStorage.setItem("smriti-theme-style", "minimalist");
        } else {
            document.body.classList.remove("theme-minimalist");
            localStorage.setItem("smriti-theme-style", "hybrid");
        }
        
        $(document).trigger("smriti-theme-style-changed", [style]);
    });
};

SMRITI.openPopout = function(url) {
    if (!url) return;
    var popout_url = url;
    if (popout_url.indexOf('?') === -1) {
        popout_url += '?popout=true';
    } else if (popout_url.indexOf('popout=true') === -1) {
        popout_url += '&popout=true';
    }
    
    if (popout_url.startsWith('/')) {
        popout_url = window.location.origin + popout_url;
    }
    
    const w = screen.width - 60;
    const h = screen.height - 60;
    const left = 30;
    const top = 30;
    const win = window.open(popout_url, "smriti-popout-window", `width=${w},height=${h},top=${top},left=${left},menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=yes`);
    if (win) {
        win.focus();
    }
};

SMRITI.toggleCategory = function(catId) {
    const block = document.getElementById(`cat-block-${catId}`);
    if (!block) return;
    
    block.classList.toggle("open");
    const isOpen = block.classList.contains("open");
    try {
        localStorage.setItem(`smriti-sidebar-cat-${catId}`, isOpen ? "open" : "closed");
    } catch (e) {}
};

// Handle resize events to dynamically add or remove the mobile hamburger menu
window.addEventListener("resize", function() {
    if (document.body.classList.contains("smriti-sidebar-active")) {
        SMRITI.setupMobileToggle();
    }
});

