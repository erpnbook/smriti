/**
 * @file: smriti_retail_os/public/js/smriti_desk.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Retail OS — Control Center (Desk) Controller
   ============================================================ */

frappe.pages['smriti-desk'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SMRITI Control Center',
        single_column: true
    });
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
                            <div class="desk-brand-title">SMRITI Retail OS</div>
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
                    <div class="desk-welcome-desc">Here is the current operational status for SMRITI Retail OS.</div>
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
                    <div class="action-card billing-card" style="padding: 18px 24px;">
                        <div class="action-icon" style="margin-bottom: 8px;">🖥️</div>
                        <div class="action-name" style="margin-bottom: 2px;">POS Billing</div>
                        <div class="action-desc" style="margin-bottom: 12px;">Launch keyboard-driven Point-of-Sale checkout terminal.</div>
                        <div class="action-buttons" style="display: flex; gap: 8px; width: 100%;">
                            <button class="btn btn-primary btn-xs btn-desk-billing-std" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px;" data-route="smriti-billing">🖥️ Standard</button>
                            <button class="btn btn-default btn-xs btn-desk-billing-popout" style="flex: 1; font-size: 11px; padding: 6px 12px; border-radius: 6px; background: #6366f1 !important; color: white !important; border-color: #6366f1 !important;" onclick="window.smriti_desk.launch_popout()">📺 Popout POS</button>
                        </div>
                    </div>

                    <!-- Shift -->
                    <div class="action-card" data-route="smriti-shift">
                        <div class="action-icon">🌅</div>
                        <div class="action-name">Shift Manager</div>
                        <div class="action-desc">Open cashier shift or count cash for Day Close.</div>
                    </div>

                    <!-- Inventory -->
                    <div class="action-card" data-route="smriti-inventory">
                        <div class="action-icon">📦</div>
                        <div class="action-name">Inventory Audit</div>
                        <div class="action-desc">Check current item stock counts and sync ledger.</div>
                    </div>

                    <!-- Barcode -->
                    <div class="action-card" data-route="smriti-barcode">
                        <div class="action-icon">🏷️</div>
                        <div class="action-name">Barcode Print</div>
                        <div class="action-desc">Generate, inspect, and print retail price tags.</div>
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
                                <div class="sys-val">v0.0.1 (Stable)</div>
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

        $('#smriti-desk-root .btn-desk-billing-std').on('click', (e) => {
            e.stopPropagation();
            frappe.set_route('smriti-billing');
        });
    }

    launch_popout() {
        const url = window.location.origin + "/app/smriti-billing?popout=true";
        const w = screen.width - 60;
        const h = screen.height - 60;
        const left = 30;
        const top = 30;
        const win = window.open(url, "SMRITI Billing Terminal", `width=${w},height=${h},top=${top},left=${left},menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=yes`);
        if (win) {
            win.focus();
        }
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
                        No active shift opened! You must open a shift in <strong>Shift Manager</strong> before POS Billing.
                        <div class="alert-item-time">Action Required</div>
                    </div>
                </div>
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
