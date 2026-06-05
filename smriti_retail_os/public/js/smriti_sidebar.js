/**
 * @file: smriti_retail_os/public/js/smriti_sidebar.js
 * @description: Frontend controller for SMRITI responsive sidebar toggle..
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Sidebar Component
   ============================================================ */

window.SMRITI = window.SMRITI || {};

SMRITI.renderSidebar = function(active_page) {
    const is_manager = frappe.user.has_role("SMRITI Store Manager");
    const is_admin_account = frappe.session.user === "Admin" || frappe.session.user === "admin@smriti.io";

    const nav_items = [
        {id:"billing",    icon:"💳", label:"Billing",
         url:"/billing"},   // Standalone billing terminal — zero Frappe chrome
        {id:"shift",      icon:"🌅", label:"Shift Management",
         url:"/shift"},
        {id:"inventory",  icon:"📦", label:"Inventory",
         url:"/inventory"},
        {id:"products",   icon:"🛍️", label:"Products",
         url:"/products"},
        {id:"barcode",    icon:"🏷️",  label:"Barcode Printing",
         url:"/barcode"},
        {id:"customers",  icon:"👥", label:"Customers",
         url:"/customers"},
        {id:"sales_invoices", icon:"📄", label:"Sales Invoices",
         url:"/sales_invoices"},
        {id:"purchase",   icon:"🛒", label:"Purchase Manager",
         url:"/purchase"},
        ...(is_manager ? [
            {id:"item_import", icon:"📥", label:"Item Master Import",
             url:"/app/smriti-item-master"},
            {id:"print_templates", icon:"📐", label:"Print Templates",
             url:"/app/smriti-print-template"},
            {id:"purchase_orders", icon:"📝", label:"Purchase Orders",
             url:"/app/purchase-order"},
            {id:"purchase_receipts", icon:"🚚", label:"Purchase Receipts",
             url:"/app/purchase-receipt"},
            {id:"suppliers",   icon:"🏢", label:"Suppliers",
             url:"/suppliers"},
            {id:"reports", icon:"📊", label:"Reports",
             url:"/reports"},
            {id:"loyalty", icon:"🎁", label:"Loyalty & Promotions",
             url:"/app/smriti-loyalty"},
            {id:"backup", icon:"🔄", label:"Backup & Restore",
             url:"/app/smriti-backup"},
            {id:"configure", icon:"⚙️", label:"Config Portal",
             url:"/configure"},
            ...(!is_admin_account ? [
                {id:"security", icon:"🔒", label:"Security & Workflows",
                 url:"/security"}
            ] : []),
            {id:"desk",    icon:"🏠", label:"Control Center",
             url:"/app/smriti-desk"}
        ] : []),
        ...((frappe.session.user === "Administrator" || frappe.session.user === "Admin") ? [
            {id:"platform_center", icon:"🛠️", label:"Platform Center",
             url:"/platform_center"}
        ] : [])
    ];

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
                nav_items, active_page, status
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
    sidebar.querySelectorAll(".smriti-side-item").forEach(function(item) {
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

SMRITI._buildSidebarDOM = function(nav_items, active_page, shift) {
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

    var menu_html = '<div class="smriti-side-menu">';
    nav_items.forEach(function(item) {
        var active_class = item.id === active_page ? 'active' : '';
        menu_html += `
            <a class="smriti-side-item ${active_class}" data-id="${item.id}" href="${item.url}">
                <span class="side-item-emoji">${item.icon}</span>
                <span class="side-item-label">${item.label}</span>
                <button class="smriti-side-item-popout" title="Open in Popout Window" data-url="${item.url}">
                    <span class="material-symbols-outlined">open_in_new</span>
                </button>
            </a>
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

// Handle resize events to dynamically add or remove the mobile hamburger menu
window.addEventListener("resize", function() {
    if (document.body.classList.contains("smriti-sidebar-active")) {
        SMRITI.setupMobileToggle();
    }
});
