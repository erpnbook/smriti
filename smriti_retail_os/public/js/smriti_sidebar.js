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

SMRITI.sidebarSchema = [
    {
        type: 'link',
        id: 'desk',
        emoji: '🏠',
        label: 'Dashboard',
        url: '/smriti'
    },
    {
        type: 'category',
        id: 'masters',
        emoji: '📦',
        label: 'Masters',
        items: [
            { type: 'subheader', label: 'Product Masters' },
            { id: 'products', label: '├─ Product Catalog', url: '/products' },
            { id: 'item_master', label: '├─ Item Master', url: '/item_master' },
            { id: 'sizewise_item', label: '├─ Sizewise Creator', url: '/sizewise_item' },
            { id: 'brand_master', label: '├─ Brand Master', url: '/smriti-coming-soon?feature=Brand+Master&progress=60&eta=Q3+2026' },
            { id: 'item_group', label: '├─ Item Group', url: '/smriti-coming-soon?feature=Item+Group&progress=45&eta=Q3+2026' },
            { id: 'category_hierarchy', label: '├─ Category Hierarchy', url: '/smriti-coming-soon?feature=Category+Hierarchy&progress=50&eta=Q3+2026' },
            { id: 'season_collection', label: '├─ Season / Collection', url: '/smriti-coming-soon?feature=Season+/+Collection&progress=40&eta=Q3+2026' },
            { id: 'uom_master', label: '└─ UOM Master', url: '/smriti-coming-soon?feature=UOM+Master&progress=70&eta=Q3+2026' },
            
            { type: 'subheader', label: 'Party Masters' },
            { id: 'customers', label: '├─ Customers', url: '/customers' },
            { id: 'customer_group', label: '├─ Customer Group', url: '/smriti-coming-soon?feature=Customer+Group&progress=30&eta=Q4+2026' },
            { id: 'territory_zone', label: '├─ Territory / Zone', url: '/smriti-coming-soon?feature=Territory+/+Zone&progress=20&eta=Q4+2026' },
            { id: 'suppliers', label: '├─ Suppliers', url: '/suppliers' },
            { id: 'supplier_group', label: '├─ Supplier Group', url: '/smriti-coming-soon?feature=Supplier+Group&progress=30&eta=Q4+2026' },
            { id: 'salespersons', label: '└─ Salespersons', url: '/smriti-coming-soon?feature=Salespersons&progress=15&eta=Q4+2026' },
            
            { type: 'subheader', label: 'Compliance Masters' },
            { id: 'hsn_master', label: '├─ HSN Master', url: '/smriti-coming-soon?feature=HSN+Master&progress=75&eta=Q3+2026' },
            { id: 'tax_templates', label: '├─ Tax Templates', url: '/smriti-coming-soon?feature=Tax+Templates&progress=65&eta=Q3+2026' },
            { id: 'gst_configuration', label: '└─ GST Configuration', url: '/smriti-coming-soon?feature=GST+Configuration&progress=80&eta=Q3+2026' },
            
            { type: 'subheader', label: 'System Masters' },
            { id: 'warehouses', label: '├─ Warehouses', url: '/smriti-coming-soon?feature=Warehouses&progress=70&eta=Q3+2026' },
            { id: 'payment_terms', label: '├─ Payment Terms', url: '/smriti-coming-soon?feature=Payment+Terms&progress=50&eta=Q4+2026' },
            { id: 'shipping_courier', label: '├─ Shipping / Courier', url: '/smriti-coming-soon?feature=Shipping+/+Courier&progress=40&eta=Q4+2026' },
            { id: 'reason_codes', label: '└─ Reason Codes', url: '/smriti-coming-soon?feature=Reason+Codes&progress=85&eta=Q3+2026' }
        ]
    },
    {
        type: 'category',
        id: 'pricing',
        emoji: '💰',
        label: 'Pricing',
        items: [
            { id: 'price_lists', label: '├─ Price Lists', url: '/smriti-coming-soon?feature=Price+Lists&progress=80&eta=Q3+2026' },
            { id: 'customer_pricing', label: '├─ Customer Pricing', url: '/smriti-coming-soon?feature=Customer+Pricing&progress=65&eta=Q3+2026' },
            { id: 'scheme_discount', label: '├─ Scheme / Discount', url: '/smriti-coming-soon?feature=Scheme+/+Discount&progress=50&eta=Q4+2026' },
            { id: 'promotions', label: '├─ Promotions', url: '/smriti-coming-soon?feature=Promotions&progress=45&eta=Q4+2026' },
            { id: 'price_revision', label: '├─ Price Revision', url: '/smriti-coming-soon?feature=Price+Revision&progress=30&eta=Q4+2026' },
            { id: 'price_audit', label: '└─ Price Audit History', url: '/smriti-coming-soon?feature=Price+Audit+History&progress=25&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'channel_stock',
        emoji: '🌐',
        label: 'Party Stock Visibility',
        items: [
            { id: 'psv_dashboard', label: '├─ PSV Dashboard', url: '/psv-dashboard' },
            { id: 'psa', label: '├─ Distributor Accounts', url: '/psa' },
            { id: 'psv_opening_balance', label: '├─ Opening Balances', url: '/psv-opening-balance' },
            { id: 'sales_upload', label: '├─ Sales Uploads', url: '/sales-upload' },
            { id: 'psv_audit', label: '├─ Stock Audits', url: '/stock-audit' },
            { id: 'replenishment_insights', label: '└─ Replenishment Insights', url: '/smriti-coming-soon?feature=Replenishment+Insights&progress=35&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'sales',
        emoji: '🛒',
        label: 'Sales',
        items: [
            { id: 'day_open', label: '├─ Day Open', url: '/shift' },
            { id: 'sales_order', label: '├─ Sales Order', url: '/smriti-coming-soon?feature=Sales+Order&progress=80&eta=Q3+2026' },
            { id: 'proforma_invoice', label: '├─ Proforma Invoice', url: '/smriti-coming-soon?feature=Proforma+Invoice&progress=70&eta=Q3+2026' },
            { id: 'billing', label: '├─ POS Billing', url: '/billing' },
            { id: 'sales_invoices', label: '├─ Tax Invoice', url: '/sales_invoices' },
            { id: 'sales_return', label: '├─ Sales Return', url: '/sales_return' },
            { id: 'delivery_challan', label: '├─ Delivery Challan', url: '/delivery_challan' },
            { id: 'customer_outward', label: '├─ Customer Outward', url: '/smriti-coming-soon?feature=Customer+Outward&progress=45&eta=Q4+2026' },
            { id: 'day_close', label: '└─ Day Close', url: '/shift' }
        ]
    },
    {
        type: 'category',
        id: 'purchase',
        emoji: '📥',
        label: 'Purchase',
        items: [
            { id: 'purchase_order', label: '├─ Purchase Order', url: '/smriti-coming-soon?feature=Purchase+Order&progress=85&eta=Q3+2026' },
            { id: 'grn', label: '├─ GRN / Receipts', url: '/purchase_receipt' },
            { id: 'purchase_invoice', label: '├─ Purchase Invoice', url: '/purchase_invoice' },
            { id: 'landed_cost', label: '├─ Landed Cost Voucher', url: '/smriti-coming-soon?feature=Landed+Cost+Voucher&progress=30&eta=Q4+2026' },
            { id: 'supplier_return', label: '├─ Supplier Return', url: '/smriti-coming-soon?feature=Supplier+Return&progress=50&eta=Q3+2026' },
            { id: 'cost_adjustments', label: '└─ Cost Adjustments', url: '/smriti-coming-soon?feature=Cost+Adjustments&progress=40&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'inventory',
        emoji: '🏬',
        label: 'Inventory',
        items: [
            { id: 'inventory_ops', label: '├─ Stock Ledger', url: '/inventory' },
            { id: 'stock_transfer', label: '├─ Stock Transfer', url: '/inventory?tab=transfer' },
            { id: 'stock_adjust', label: '├─ Stock Adjustment', url: '/inventory?tab=adjust' },
            { id: 'stock_audit_wh', label: '├─ Stock Audit', url: '/smriti-coming-soon?feature=Stock+Audit&progress=60&eta=Q3+2026' },
            { id: 'barcode', label: '├─ Barcode Center', url: '/barcode' },
            { id: 'print_templates', label: '├─ Print Templates', url: '/print_templates' },
            { id: 'batch_management', label: '├─ Batch Management', url: '/smriti-coming-soon?feature=Batch+Management&progress=50&eta=Q4+2026' },
            { id: 'reorder_planning', label: '└─ Reorder Planning', url: '/smriti-coming-soon?feature=Reorder+Planning&progress=45&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'intelligence',
        emoji: '📊',
        label: 'Intelligence',
        items: [
            { id: 'exec_dashboard', label: '├─ Executive Dashboard', url: '/smriti-coming-soon?feature=Executive+Dashboard&progress=30&eta=Q4+2026', feature_flag: 'exec_dashboard_enabled' },
            { id: 'gmroi', label: '├─ GMROI', url: '/smriti-coming-soon?feature=GMROI&progress=40&eta=Q4+2026', feature_flag: 'gmroi_enabled' },
            { id: 'sell_through', label: '├─ Sell Through', url: '/smriti-coming-soon?feature=Sell+Through&progress=35&eta=Q4+2026', feature_flag: 'sell_through_enabled' },
            { id: 'coverage_days', label: '├─ Coverage Days', url: '/smriti-coming-soon?feature=Coverage+Days&progress=20&eta=Q4+2026', feature_flag: 'coverage_days_enabled' },
            { id: 'inventory_aging', label: '├─ Inventory Aging', url: '/smriti-coming-soon?feature=Inventory+Aging&progress=25&eta=Q4+2026', feature_flag: 'inventory_aging_enabled' },
            { id: 'capital_locked', label: '├─ Capital Locked', url: '/smriti-coming-soon?feature=Capital+Locked&progress=15&eta=Q4+2026', feature_flag: 'capital_locked_enabled' },
            { id: 'dead_stock', label: '└─ Dead Stock Recovery', url: '/smriti-coming-soon?feature=Dead+Stock+Recovery&progress=10&eta=Q4+2026', feature_flag: 'dead_stock_enabled' }
        ]
    },
    {
        type: 'category',
        id: 'ai_hub',
        emoji: '🤖',
        label: 'AI Hub',
        items: [
            { id: 'demand_forecast', label: '├─ Demand Forecast', url: '/smriti-coming-soon?feature=Demand+Forecast&progress=30&eta=Q4+2026', feature_flag: 'demand_forecast_enabled' },
            { id: 'slow_mover', label: '├─ Slow Mover Detection', url: '/smriti-coming-soon?feature=Slow+Mover+Detection&progress=35&eta=Q4+2026', feature_flag: 'slow_mover_enabled' },
            { id: 'purchase_suggestions', label: '├─ Purchase Suggestions', url: '/smriti-coming-soon?feature=Purchase+Suggestions&progress=40&eta=Q4+2026', feature_flag: 'purchase_suggestions_enabled' },
            { id: 'promo_suggestions', label: '├─ Promotion Suggestions', url: '/smriti-coming-soon?feature=Promotion+Suggestions&progress=45&eta=Q4+2026', feature_flag: 'promo_suggestions_enabled' },
            { id: 'stock_risk_alerts', label: '└─ Stock Risk Alerts', url: '/smriti-coming-soon?feature=Stock+Risk+Alerts&progress=50&eta=Q4+2026', feature_flag: 'stock_risk_alerts_enabled' }
        ]
    },
    {
        type: 'category',
        id: 'reports',
        emoji: '📑',
        label: 'Reports',
        items: [
            { id: 'sales_reports', label: '├─ Sales Reports', url: '/reports?category=Sales' },
            { id: 'purchase_reports', label: '├─ Purchase Reports', url: '/reports?category=Purchase' },
            { id: 'inventory_reports', label: '├─ Inventory Reports', url: '/reports?category=Inventory' },
            { id: 'psv_reports', label: '├─ PSV Reports', url: '/reports?category=PSV' },
            { id: 'pricing_reports', label: '├─ Pricing Reports', url: '/reports?category=Pricing' },
            { id: 'saved_reports', label: '└─ Saved Reports', url: '/reports?category=Saved' }
        ]
    },
    {
        type: 'category',
        id: 'integrations',
        emoji: '🔄',
        label: 'Integrations',
        items: [
            { id: 'tally_sync', label: '├─ TallyPrime Sync', url: '/smriti-coming-soon?feature=TallyPrime+Sync&progress=85&eta=Q3+2026' },
            { id: 'export_center', label: '├─ Export Center', url: '/smriti-coming-soon?feature=Export+Center&progress=60&eta=Q3+2026' },
            { id: 'import_center', label: '├─ Import Center', url: '/smriti-coming-soon?feature=Import+Center&progress=70&eta=Q3+2026' },
            { id: 'sync_history', label: '├─ Sync History', url: '/smriti-coming-soon?feature=Sync+History&progress=40&eta=Q3+2026' },
            { id: 'integration_settings', label: '└─ Integration Settings', url: '/smriti-coming-soon?feature=Integration+Settings&progress=50&eta=Q3+2026' }
        ]
    },
    {
        type: 'category',
        id: 'admin',
        emoji: '⚙️',
        label: 'Administration',
        items: [
            { id: 'users', label: '├─ Users', url: '/smriti-coming-soon?feature=Users+Management&progress=80&eta=Q3+2026' },
            { id: 'roles', label: '├─ Roles', url: '/smriti-coming-soon?feature=Roles+Management&progress=75&eta=Q3+2026' },
            { id: 'security', label: '├─ Security & Workflow', url: '/security' },
            { id: 'audit_logs', label: '├─ Audit Logs', url: '/smriti-coming-soon?feature=Audit+Logs&progress=90&eta=Q3+2026' },
            { id: 'activity_logs', label: '├─ Activity Logs', url: '/smriti-coming-soon?feature=Activity+Logs&progress=85&eta=Q3+2026' },
            { id: 'backup', label: '├─ Backup Center', url: '/backup' },
            { id: 'configure', label: '└─ System Settings', url: '/configure' }
        ]
    },
    {
        type: 'link',
        id: 'help',
        emoji: '🆘',
        label: 'Help Desk',
        url: '/smriti-coming-soon?feature=Help+Desk&progress=80&eta=Q3+2026'
    }
];

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

    // Feature Flag Policy
    function isFeatureEnabled(flag) {
        if (!flag) return true;
        const SMRITI_FEATURE_FLAGS = {
            "intelligence_enabled": false,
            "ai_hub_enabled": false,
            "coverage_days_enabled": false,
            "exec_dashboard_enabled": false,
            "gmroi_enabled": false,
            "sell_through_enabled": false,
            "inventory_aging_enabled": false,
            "capital_locked_enabled": false,
            "dead_stock_enabled": false,
            "demand_forecast_enabled": false,
            "slow_mover_enabled": false,
            "purchase_suggestions_enabled": false,
            "promo_suggestions_enabled": false,
            "stock_risk_alerts_enabled": false
        };
        return !!SMRITI_FEATURE_FLAGS[flag];
    }

    let business_type = "Footwear";
    if (window.frappe && frappe.boot && frappe.boot.smriti_business_type) {
        business_type = frappe.boot.smriti_business_type;
    }

    const filteredSchema = JSON.parse(JSON.stringify(SMRITI.sidebarSchema));
    const renderedSchema = [];

    filteredSchema.forEach(cat => {
        // Exclude category by feature flag
        if (cat.feature_flag && !isFeatureEnabled(cat.feature_flag)) {
            return;
        }

        if (cat.type === 'category') {
            if (cat.items) {
                cat.items = cat.items.filter(item => {
                    // Exclude items by feature flag
                    if (item.feature_flag && !isFeatureEnabled(item.feature_flag)) {
                        return false;
                    }
                    if (business_type !== "Footwear") {
                        // FMCG / Others (hide footwear size attributes)
                        if (['sizewise_item', 'sizewise_invoice'].includes(item.id)) return false;
                    }
                    return true;
                });
            }
            // AUTO-HIDE POLICY: Hide category if no child items or only subheaders are rendered
            const hasClickableItems = cat.items && cat.items.some(item => item.type !== 'subheader');
            if (!hasClickableItems) {
                return;
            }
        } else if (cat.type === 'link') {
            // Exclude links by feature flag
            if (cat.feature_flag && !isFeatureEnabled(cat.feature_flag)) {
                return;
            }
        }
        renderedSchema.push(cat);
    });

    var menu_html = '<div class="smriti-side-menu">';
    
    var is_admin_account = frappe.session.user === "Admin" || frappe.session.user === "admin@erpnbook.com";

    renderedSchema.forEach(block => {
        if (block.type === 'link') {
            if (is_admin_account && block.id === 'security') return;
            const activeCls = block.id === active_page ? 'active' : '';
            menu_html += `
                <a class="smriti-side-item ${activeCls}" data-id="${block.id}" href="${block.url}">
                    <span class="side-item-emoji">${block.emoji}</span>
                    <span class="side-item-label">${block.label}</span>
                    <button class="smriti-side-item-popout" title="Open in Popout Window" data-url="${block.url}">
                        <span class="material-symbols-outlined">open_in_new</span>
                    </button>
                </a>
            `;
        } else if (block.type === 'category') {
            const isCatOpen = localStorage.getItem(`smriti-sidebar-cat-${block.id}`) !== 'closed';
            const openCls = isCatOpen ? 'open' : '';
            
            // Check if any sub-item is active to highlight parent category
            let isSubActive = false;
            let subItemsHtml = '';
            
            block.items.forEach(sub => {
                if (is_admin_account && sub.id === 'security') return;
                
                if (sub.type === 'subheader') {
                    subItemsHtml += `
                        <div class="sidebar-sub-header smriti-side-sub-header">
                            <span>${sub.label}</span>
                        </div>
                    `;
                    return;
                }
                
                const subActiveCls = sub.id === active_page ? 'active' : '';
                if (sub.id === active_page) isSubActive = true;
                subItemsHtml += `
                    <a class="smriti-side-sub-item ${subActiveCls}" data-id="${sub.id}" href="${sub.url}">
                        <span class="side-item-label">${sub.label}</span>
                        <button class="smriti-side-item-popout" title="Open in Popout Window" data-url="${sub.url}">
                            <span class="material-symbols-outlined" style="font-size:14px;">open_in_new</span>
                        </button>
                    </a>
                `;
            });

            const headerActiveCls = isSubActive ? 'active' : '';
            
            menu_html += `
                <div class="smriti-side-category ${openCls}" id="cat-block-${block.id}">
                    <div class="smriti-side-category-header ${headerActiveCls}" onclick="SMRITI.toggleCategory('${block.id}')">
                        <span class="side-item-emoji">${block.emoji}</span>
                        <span class="side-item-label">${block.label}</span>
                        <span class="material-symbols-outlined arrow">chevron_right</span>
                    </div>
                    <div class="smriti-side-category-body">
                        ${subItemsHtml}
                    </div>
                </div>
            `;
        }
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

