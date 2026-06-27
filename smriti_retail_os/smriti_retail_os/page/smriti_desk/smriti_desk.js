/**
 * @file: smriti_retail_os/page/smriti-desk/smriti-desk.js
 * @description: Frontend controller for SMRITI Desk view customizations..
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.8.6
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Retail OS — Control Center (Desk) Controller
   ============================================================ */

frappe.pages['smriti-desk'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Control Center',
        single_column: true
    });

    if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
        SMRITI.renderSidebar("desk");
    }

    window.smriti_desk = new SmritiDeskPage(wrapper);
};

class SmritiDeskPage {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.active_shift = null;
        this.shift_summary = null;

        this._inject_css();
        this._render_shell();
        this._load_dashboard_data();
    }

    // ─── CSS Injection ────────────────────────────────────────
    _inject_css() {
        if (!document.getElementById('smriti-desk-css')) {
            const link = document.createElement('link');
            link.id   = 'smriti-desk-css';
            link.rel  = 'stylesheet';
            link.href = '/assets/smriti_retail_os/css/smriti-desk.css';
            document.head.appendChild(link);
        }
    }

    // ─── Render Shell HTML ────────────────────────────────────
    _render_shell() {
        const user_fullname = (frappe.session.user_info && frappe.session.user_info.fullname) || frappe.session.user;
        
        $(this.wrapper).find('.page-content').html(`
            <div id="smriti-desk-root">
                <!-- Header -->
                <div class="desk-header">
                    <div class="desk-brand">
                        <div class="desk-brand-icon">🏪</div>
                        <div>
                            <div class="desk-brand-title">Control Center</div>
                            <div class="desk-brand-sub">Smarter Retail. Built for India.</div>
                        </div>
                    </div>
                    <div id="desk-status-badge" class="shift-status-badge closed">
                        <div class="dot"></div>
                        <span>Checking Status…</span>
                    </div>
                </div>

                <!-- Welcome Section -->
                <div class="desk-welcome-section">
                    <div class="desk-welcome-title">Welcome back, ${user_fullname}!</div>
                    <div class="desk-welcome-desc">Here is your current operational status.</div>
                </div>

                <!-- KPI Grid -->
                <div class="kpi-grid">
                    <!-- Shift Sales KPI -->
                    <div class="glass-card kpi-card">
                        <div class="kpi-title-row">
                            <span>Live Shift Sales</span>
                            <span class="kpi-icon">📈</span>
                        </div>
                        <div class="kpi-value" id="kpi-shift-sales">₹0.00</div>
                        <div class="kpi-footer" id="kpi-shift-sales-sub">No active cashier shift</div>
                    </div>

                    <!-- Bills KPI -->
                    <div class="glass-card kpi-card">
                        <div class="kpi-title-row">
                            <span>Invoices Issued</span>
                            <span class="kpi-icon">🧾</span>
                        </div>
                        <div class="kpi-value" id="kpi-bills-count">0</div>
                        <div class="kpi-footer" id="kpi-bills-count-sub">During this session</div>
                    </div>

                    <!-- Shift Time KPI -->
                    <div class="glass-card kpi-card">
                        <div class="kpi-title-row">
                            <span>Shift Period</span>
                            <span class="kpi-icon">🕒</span>
                        </div>
                        <div class="kpi-value" style="font-size: 20px; line-height: 38px;" id="kpi-shift-time">Inactive</div>
                        <div class="kpi-footer" id="kpi-shift-time-sub">Open a shift to track time</div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="actions-title">
                    <span>⚡ Quick Actions</span>
                </div>
                <div class="action-grid">
                    <!-- Billing -->
                    <div class="action-card billing-card" style="padding: 18px 24px; display: flex; flex-direction: column;">
                        <div class="action-icon" style="margin-bottom: 8px;">🖥️</div>
                        <div class="action-name" style="margin-bottom: 2px;">Retail Billing</div>
                        <div class="action-desc" style="margin-bottom: 12px; flex: 1;">Launch checkout terminal and scan barcoded items.</div>
                        <div class="action-buttons" style="display: flex; gap: 8px; width: 100%; margin-top: auto;">
                            <button class="btn btn-primary btn-xs btn-desk-billing-std" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px;">🖥️ Standard</button>
                            <button class="btn btn-default btn-xs btn-desk-billing-popout" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px; background: #6366f1 !important; color: white !important; border-color: #6366f1 !important;" onclick="SMRITI.openPopout('/app/smriti-billing')">📺 Popout</button>
                        </div>
                    </div>

                    <!-- Shift -->
                    <div class="action-card" style="padding: 18px 24px; display: flex; flex-direction: column;">
                        <div class="action-icon" style="margin-bottom: 8px;">🌅</div>
                        <div class="action-name" style="margin-bottom: 2px;">Day Open / Close</div>
                        <div class="action-desc" style="margin-bottom: 12px; flex: 1;">Open cashier shift or count cash for Day Close.</div>
                        <div class="action-buttons" style="display: flex; gap: 8px; width: 100%; margin-top: auto;">
                            <button class="btn btn-primary btn-xs btn-desk-shift-std" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px;">🌅 Standard</button>
                            <button class="btn btn-default btn-xs btn-desk-shift-popout" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px; background: #6366f1 !important; color: white !important; border-color: #6366f1 !important;" onclick="SMRITI.openPopout('/app/smriti-shift')">📺 Popout</button>
                        </div>
                    </div>

                    <!-- Inventory -->
                    <div class="action-card" style="padding: 18px 24px; display: flex; flex-direction: column;">
                        <div class="action-icon" style="margin-bottom: 8px;">📦</div>
                        <div class="action-name" style="margin-bottom: 2px;">Inventory Operations</div>
                        <div class="action-desc" style="margin-bottom: 12px; flex: 1;">Check current item stock counts and sync ledger.</div>
                        <div class="action-buttons" style="display: flex; gap: 8px; width: 100%; margin-top: auto;">
                            <button class="btn btn-primary btn-xs btn-desk-inventory-std" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px;">📦 Standard</button>
                            <button class="btn btn-default btn-xs btn-desk-inventory-popout" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px; background: #6366f1 !important; color: white !important; border-color: #6366f1 !important;" onclick="SMRITI.openPopout('/app/smriti-inventory')">📺 Popout</button>
                        </div>
                    </div>

                    <!-- Purchase -->
                    <div class="action-card" style="padding: 18px 24px; display: flex; flex-direction: column;">
                        <div class="action-icon" style="margin-bottom: 8px;">🛒</div>
                        <div class="action-name" style="margin-bottom: 2px;">Purchase Management</div>
                        <div class="action-desc" style="margin-bottom: 12px; flex: 1;">Manage Purchase Orders and record simple purchases.</div>
                        <div class="action-buttons" style="display: flex; gap: 8px; width: 100%; margin-top: auto;">
                            <button class="btn btn-primary btn-xs btn-desk-purchase-std" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px;">🛒 Standard</button>
                            <button class="btn btn-default btn-xs btn-desk-purchase-popout" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px; background: #6366f1 !important; color: white !important; border-color: #6366f1 !important;" onclick="SMRITI.openPopout('/app/smriti-purchase')">📺 Popout</button>
                        </div>
                    </div>

                    <!-- Barcode -->
                    <div class="action-card" style="padding: 18px 24px; display: flex; flex-direction: column;">
                        <div class="action-icon" style="margin-bottom: 8px;">🏷️</div>
                        <div class="action-name" style="margin-bottom: 2px;">Barcode Printing</div>
                        <div class="action-desc" style="margin-bottom: 12px; flex: 1;">Generate, inspect, and print retail price tags.</div>
                        <div class="action-buttons" style="display: flex; gap: 8px; width: 100%; margin-top: auto;">
                            <button class="btn btn-primary btn-xs btn-desk-barcode-std" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px;">🏷️ Standard</button>
                            <button class="btn btn-default btn-xs btn-desk-barcode-popout" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px; background: #6366f1 !important; color: white !important; border-color: #6366f1 !important;" onclick="SMRITI.openPopout('/app/smriti-barcode')">📺 Popout</button>
                        </div>
                    </div>
                </div>

                <!-- Quick Masters -->
                <div class="actions-title" style="margin-top: 40px;">
                    <span>📖 Quick Masters</span>
                </div>
                <div class="action-grid">
                    <!-- Add Item -->
                    <div class="action-card master-action" data-type="item">
                        <div class="action-icon">🛍️</div>
                        <div class="action-name">Add Product</div>
                        <div class="action-desc">Quickly create a new retail item with barcode and price.</div>
                    </div>

                    <!-- Add Customer -->
                    <div class="action-card master-action" data-type="customer">
                        <div class="action-icon">🤝</div>
                        <div class="action-name">Add Customer</div>
                        <div class="action-desc">Onboard a new customer for loyalty and billing.</div>
                    </div>

                    <!-- Add Supplier -->
                    <div class="action-card master-action" data-type="supplier">
                        <div class="action-icon">🚛</div>
                        <div class="action-name">Add Supplier</div>
                        <div class="action-desc">Add a new supplier for purchase orders and GRN.</div>
                    </div>
                </div>

                <!-- Bottom Panels -->
                <div class="bottom-grid">
                    <!-- Notifications Panel -->
                    <div class="glass-card">
                        <div class="panel-title">
                            <span>🔔 Operations Alert Feed</span>
                        </div>
                        <div class="alert-list" id="alerts-container">
                            <div class="alert-item info">
                                <div class="alert-item-icon">💡</div>
                                <div class="alert-item-content">
                                    Welcome to SMRITI Retail OS! Use <strong>POS Billing</strong> to start billing items immediately.
                                    <div class="alert-item-time">Just now</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Diagnostics Panel -->
                    <div class="glass-card">
                        <div class="panel-title">
                            <span>⚙️ System Diagnostics</span>
                        </div>
                        <div class="sys-list">
                            <div class="sys-row">
                                <div class="sys-label">Retail OS Version</div>
                                <div class="sys-val">v${(frappe.boot && frappe.boot.versions && frappe.boot.versions.smriti_retail_os) || "1.2.9"} (Stable)</div>
                            </div>
                            <div class="sys-row">
                                <div class="sys-label">Database Connection</div>
                                <div class="sys-val ok">● Nominal</div>
                            </div>
                            <div class="sys-row">
                                <div class="sys-label">Tax Engine (GST)</div>
                                <div class="sys-val ok">● Active</div>
                            </div>
                            <div class="sys-row">
                                <div class="sys-label">Active Terminal Profile</div>
                                <div class="sys-val" id="sys-terminal-profile">Checking…</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="desk-footer">
                    SMRITI Retail OS &copy; ${new Date().getFullYear()} &mdash; Smarter Retail. Built for India.
                </div>
            </div>
        `);

        // Bind quick action routing
        $('#smriti-desk-root .action-card').on('click', (e) => {
            if ($(e.target).closest('button').length) {
                return; // Do not trigger route if clicking card buttons
            }
            const route = $(e.currentTarget).data('route');
            if (route) {
                frappe.set_route(route);
            }
        });

        // Bind standard action buttons
        $('#smriti-desk-root .btn-desk-billing-std').on('click', (e) => {
            e.stopPropagation();
            frappe.set_route('smriti-billing');
        });
        $('#smriti-desk-root .btn-desk-shift-std').on('click', (e) => {
            e.stopPropagation();
            frappe.set_route('smriti-shift');
        });
        $('#smriti-desk-root .btn-desk-inventory-std').on('click', (e) => {
            e.stopPropagation();
            frappe.set_route('smriti-inventory');
        });
        $('#smriti-desk-root .btn-desk-purchase-std').on('click', (e) => {
            e.stopPropagation();
            frappe.set_route('smriti-purchase');
        });
        $('#smriti-desk-root .btn-desk-barcode-std').on('click', (e) => {
            e.stopPropagation();
            frappe.set_route('smriti-barcode');
        });

        // Bind master action clicks
        $('#smriti-desk-root .master-action').on('click', (e) => {
            const type = $(e.currentTarget).data('type');
            if (type === 'item') this.quick_add_item();
            else if (type === 'customer') this.quick_add_customer();
            else if (type === 'supplier') this.quick_add_supplier();
        });
    }

    quick_add_item() {
        let d = new frappe.ui.Dialog({
            title: __('📖 Quick Add Product'),
            fields: [
                { label: __('Barcode'), fieldname: 'barcode', fieldtype: 'Data', reqd: 1 },
                { label: __('Item Name'), fieldname: 'item_name', fieldtype: 'Data', reqd: 1 },
                { label: __('Selling Price'), fieldname: 'rate', fieldtype: 'Currency', reqd: 1 },
                { label: __('MRP'), fieldname: 'mrp', fieldtype: 'Currency', reqd: 1 },
                { label: __('GST %'), fieldname: 'gst_percentage', fieldtype: 'Select', options: '0\n5\n12\n18\n28', default: '18' }
            ],
            primary_action_label: __('Create Product'),
            primary_action(values) {
                frappe.call({
                    method: "smriti_retail_os.master_api.quick_create_item",
                    args: values,
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({message: __("Product Created Successfully"), indicator: 'green'});
                            d.hide();
                        }
                    }
                });
            }
        });
        d.show();
    }

    quick_add_customer() {
        let d = new frappe.ui.Dialog({
            title: __('🤝 Quick Add Customer'),
            fields: [
                { label: __('Full Name'), fieldname: 'customer_name', fieldtype: 'Data', reqd: 1 },
                { label: __('Mobile Number'), fieldname: 'mobile_no', fieldtype: 'Data' }
            ],
            primary_action_label: __('Create Customer'),
            primary_action(values) {
                frappe.call({
                    method: "smriti_retail_os.master_api.quick_create_customer",
                    args: values,
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({message: __("Customer Created Successfully"), indicator: 'green'});
                            d.hide();
                        }
                    }
                });
            }
        });
        d.show();
    }

    quick_add_supplier() {
        let d = new frappe.ui.Dialog({
            title: __('🚛 Quick Add Supplier'),
            fields: [
                { label: __('Supplier Name'), fieldname: 'supplier_name', fieldtype: 'Data', reqd: 1 },
                { label: __('Contact Number'), fieldname: 'mobile_no', fieldtype: 'Data' }
            ],
            primary_action_label: __('Create Supplier'),
            primary_action(values) {
                frappe.call({
                    method: "smriti_retail_os.master_api.quick_create_supplier",
                    args: values,
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({message: __("Supplier Created Successfully"), indicator: 'green'});
                            d.hide();
                        }
                    }
                });
            }
        });
        d.show();
    }

    // ─── Load Dashboard Data ──────────────────────────────────
    async _load_dashboard_data() {
        try {
            // Fetch shift status
            const shift = await this._call('smriti_retail_os.shift_api.get_active_shift', {
                cashier: frappe.session.user
            });
            this.active_shift = shift || null;
            this._update_shift_ui();

            if (this.active_shift) {
                // Fetch shift totals
                this.shift_summary = await this._call('smriti_retail_os.shift_api.get_shift_summary', {
                    opening_entry_name: this.active_shift.name
                });
                this._render_shift_totals();
            }
        } catch (e) {
            console.error('Failed to load dashboard data:', e);
        }
    }

    // ─── Update Shift Status UI ───────────────────────────────
    _update_shift_ui() {
        const badge = $('#desk-status-badge');
        const termVal = $('#sys-terminal-profile');
        
        if (this.active_shift) {
            badge.removeClass('closed').addClass('open');
            badge.html('<div class="dot"></div><span>Shift Active</span>');
            termVal.text(this.active_shift.pos_profile || 'Default Profile');

            // Set shift start time KPI
            const start = frappe.datetime.str_to_user(this.active_shift.period_start_date) || this.active_shift.period_start_date;
            $('#kpi-shift-time').text(this.active_shift.pos_profile);
            $('#kpi-shift-time-sub').text('Opened at ' + start.split(' ')[1]);

            // Add alert to feed
            $('#alerts-container').prepend(`
                <div class="alert-item warning">
                    <div class="alert-item-icon">🏪</div>
                    <div class="alert-item-content">
                        Shift <strong>${this.active_shift.name}</strong> is currently active for POS Profile <strong>${this.active_shift.pos_profile}</strong>.
                        <div class="alert-item-time">Active</div>
                    </div>
                </div>
            `);
        } else {
            badge.removeClass('open').addClass('closed');
            badge.html('<div class="dot"></div><span>No Active Shift</span>');
            termVal.text('None');

            $('#kpi-shift-time').text('Inactive');
            $('#kpi-shift-time-sub').text('Open a shift under Shift Manager');

            $('#alerts-container').prepend(`
                <div class="alert-item danger">
                    <div class="alert-item-icon">⚠️</div>
                    <div class="alert-item-content">
                        No active shift opened! You must open a shift in <strong>Day Open / Close</strong> before Retail Billing.
                        <div class="alert-item-time">Action Required</div>
                    </div>                </div>
            `);
        }
    }

    // ─── Render Live Shift Totals ─────────────────────────────
    _render_shift_totals() {
        if (!this.shift_summary) return;

        const s = this.shift_summary;
        
        // Update Shift Sales KPI
        $('#kpi-shift-sales').text('₹' + parseFloat(s.total_sales || 0).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }));
        $('#kpi-shift-sales-sub').html(`Active Cashier: <strong>${frappe.session.user_info?.fullname || frappe.session.user}</strong>`);

        // Update Invoices Issued KPI
        $('#kpi-bills-count').text(s.invoice_count || 0);
        $('#kpi-bills-count-sub').text('Average Bill Value: ₹' + (s.invoice_count > 0 ? parseFloat(s.total_sales / s.invoice_count).toFixed(2) : '0.00'));
    }

    // ─── Frappe Call Wrapper ──────────────────────────────────
    _call(method, args = {}) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method,
                args,
                callback: r => {
                    if (r.message !== undefined) resolve(r.message);
                    else resolve(null);
                },
                error: err => reject(err)
            });
        });
    }
}
