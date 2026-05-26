/* ============================================================
   SMRITI Sidebar Component
   ============================================================ */

window.SMRITI = window.SMRITI || {};

SMRITI.renderSidebar = function(active_page) {
    if (!window.frappe || !frappe.session) return;

    // 1. System Manager bypass
    if (frappe.user.has_role("System Manager")) return;

    // 2. Hide ERPNext default sidebar
    document.querySelector(
        ".layout-side-section"
    )?.style.setProperty("display", "none", "important");

    // 3. Remove existing SMRITI sidebar if present
    document.getElementById("smriti-sidebar")?.remove();

    // 4. Build sidebar HTML
    const is_manager = frappe.user.has_role("SMRITI Store Manager");

    const nav_items = [
        {id:"billing",    icon:"💳", label:"Billing",
         url:"/app/smriti-billing"},
        {id:"inventory",  icon:"📦", label:"Inventory",
         url:"/app/smriti-inventory"},
        {id:"barcode",    icon:"🏷️",  label:"Barcodes",
         url:"/app/smriti-barcode"},
        {id:"customers",  icon:"👥", label:"Customers",
         url:"/app/customer"},
        {id:"purchase",   icon:"🛒", label:"Purchase",
         url:"/app/smriti-purchase"},
        ...(is_manager ? [
            {id:"reports", icon:"📊", label:"Reports",
             url:"/app/smriti-reports"},
            {id:"desk",    icon:"🏠", label:"Dashboard",
             url:"/app/smriti-desk"}
        ] : [])
    ];

    // 5. Shift status fetch
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

SMRITI._buildSidebarDOM = function(nav_items, active_page, shift) {
    var layout_container = document.querySelector(".layout-container");
    if (!layout_container) {
        // Try again in 100ms if container is not ready
        setTimeout(function() { SMRITI._buildSidebarDOM(nav_items, active_page, shift); }, 100);
        return;
    }

    // Double check that we don't have multiple sidebars
    document.getElementById("smriti-sidebar")?.remove();

    var sidebar = document.createElement("div");
    sidebar.id = "smriti-sidebar";
    
    // Check if collapsed state is cached
    if (getSidebarCollapsed()) {
        sidebar.classList.add("collapsed");
    }

    // Load stylesheet dynamically if not present
    if (!document.getElementById("smriti-sidebar-styles")) {
        var link = document.createElement("link");
        link.id = "smriti-sidebar-styles";
        link.rel = "stylesheet";
        link.href = "/assets/smriti_retail_os/css/smriti_sidebar.css";
        document.head.appendChild(link);
    }

    var is_collapsed = sidebar.classList.contains("collapsed");
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
                <span>${item.label}</span>
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

    var footer_html = `
        <div class="smriti-side-footer">
            <div class="smriti-side-shift" style="cursor: pointer;" onclick="frappe.set_route('smriti-shift')" title="Open Shift Page">
                <span>Shift:</span>
                <span class="smriti-side-shift-badge ${shift_class}" id="smriti-shift-badge">${shift_status}</span>
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
    layout_container.insertBefore(sidebar, layout_container.firstChild);

    // Bind event listeners
    var toggle_btn = sidebar.querySelector(".smriti-side-toggle");
    if (toggle_btn) {
        toggle_btn.addEventListener("click", function() {
            sidebar.classList.toggle("collapsed");
            var collapsed = sidebar.classList.contains("collapsed");
            setSidebarCollapsed(collapsed);
            
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
};
