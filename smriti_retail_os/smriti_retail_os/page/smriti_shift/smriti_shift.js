/**
 * @file: smriti_retail_os/public/js/smriti_shift.js
 * @description: Frontend controller for SMRITI shift opening/closing..
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Retail OS — Day Open / Day Close Controller
   Phase 5 — uses standard POS Opening Entry & POS Closing Entry
   ============================================================ */

frappe.pages['smriti-shift'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SMRITI Day Open / Close',
        single_column: true
    });
    window.smriti_shift = new SmritiShiftPage(wrapper);
};

class SmritiShiftPage {
    constructor(wrapper) {
        this.wrapper       = wrapper;
        this.pos_profiles  = [];
        this.payment_modes = [];
        this.active_shift  = null;
        this.shift_summary = null;

        // Indian currency denominations (notes + coins)
        this.denominations = [2000, 500, 200, 100, 50, 20, 10, 5, 2, 1];

        this._inject_css();
        this._render_shell();
        this._load_initial_data();
    }

    // ─── CSS injection ────────────────────────────────────────
    _inject_css() {
        if (!document.getElementById('smriti-shift-css')) {
            const link = document.createElement('link');
            link.id   = 'smriti-shift-css';
            link.rel  = 'stylesheet';
            link.href = '/assets/smriti_retail_os/css/smriti-shift.css';
            document.head.appendChild(link);
        }
    }

    // ─── Shell HTML ───────────────────────────────────────────
    _render_shell() {
        $(this.wrapper).find('.page-content').html(`
            <div id="smriti-shift-root">
                <!-- Header -->
                <div class="shift-header">
                    <div class="brand">
                        <div class="brand-icon">🏪</div>
                        <div>
                            <div class="brand-title">SMRITI Retail OS</div>
                            <div class="brand-sub">Day Open / Close</div>
                        </div>
                    </div>
                    <div id="shift-status-badge" class="shift-status-badge closed">
                        <div class="dot"></div>
                        <span>Loading…</span>
                    </div>
                </div>

                <div class="shift-main">
                    <!-- Tabs -->
                    <div class="shift-tabs" id="shift-tabs">
                        <button class="shift-tab active" data-tab="open-tab">🌅 Day Open</button>
                        <button class="shift-tab" data-tab="close-tab">🌙 Day Close</button>
                        <button class="shift-tab" data-tab="summary-tab">📊 Shift Summary</button>
                    </div>

                    <!-- ══ DAY OPEN SCREEN ══ -->
                    <div id="open-tab" class="shift-screen active">

                        <div class="glass-card" id="no-shift-panel">
                            <div class="card-title">
                                <div class="icon">🌅</div>
                                Open Today's Shift
                            </div>

                            <div class="form-group">
                                <label class="form-label">POS Profile</label>
                                <select id="pos-profile-select" class="form-control">
                                    <option value="">Loading profiles…</option>
                                </select>
                            </div>

                            <div class="card-title" style="margin-top:24px;">
                                <div class="icon">💵</div>
                                Opening Cash Float
                            </div>
                            <p style="font-size:13px;color:var(--text-muted);margin-bottom:16px;">
                                Enter the physical cash in drawer and float for each payment mode.
                            </p>

                            <div id="opening-payment-rows" class="payment-rows">
                                <!-- Rows injected dynamically -->
                            </div>

                            <div class="btn-row">
                                <button id="btn-open-shift" class="btn-shift btn-success">
                                    ✅ Open Shift
                                </button>
                            </div>
                        </div>

                        <!-- Already open info -->
                        <div class="glass-card" id="shift-open-info" style="display:none;">
                            <div class="card-title">
                                <div class="icon">✅</div>
                                Shift is Active
                            </div>
                            <div id="active-shift-info-bar" class="shift-info-bar"></div>
                            <p style="font-size:14px;color:var(--text-secondary);">
                                A shift is currently open. Go to <strong>Day Close</strong> tab to close it,
                                or <strong>Shift Summary</strong> to view real-time sales totals.
                            </p>
                            <div class="btn-row" style="margin-top:16px;">
                                <button class="btn-shift btn-ghost" onclick="smriti_shift._show_tab('summary-tab')">
                                    📊 View Summary
                                </button>
                                <button class="btn-shift btn-danger" onclick="smriti_shift._show_tab('close-tab')">
                                    🌙 Go to Day Close
                                </button>
                            </div>
                        </div>

                    </div>

                    <!-- ══ DAY CLOSE SCREEN ══ -->
                    <div id="close-tab" class="shift-screen">

                        <!-- No shift warning -->
                        <div class="glass-card" id="no-active-shift-msg" style="display:none;">
                            <div class="card-title"><div class="icon">⚠️</div>No Active Shift</div>
                            <p style="color:var(--text-muted);font-size:14px;">
                                There is no open shift to close. Please open a shift first.
                            </p>
                            <div class="btn-row">
                                <button class="btn-shift btn-primary" onclick="smriti_shift._show_tab('open-tab')">
                                    🌅 Open Shift
                                </button>
                            </div>
                        </div>

                        <!-- Close form -->
                        <div id="close-shift-form">
                            <!-- KPIs injected after loading summary -->
                            <div class="kpi-grid" id="close-kpi-grid"></div>

                            <!-- Cash denomination count -->
                            <div class="glass-card">
                                <div class="card-title">
                                    <div class="icon">💵</div>
                                    Cash Count by Denomination
                                </div>
                                <div class="denom-grid" id="denom-grid"></div>
                                <div class="cash-total-display">
                                    Cash Total: ₹<span id="denom-cash-total">0.00</span>
                                </div>
                            </div>

                            <!-- Other payment modes -->
                            <div class="glass-card">
                                <div class="card-title">
                                    <div class="icon">💳</div>
                                    Other Payment Modes
                                </div>
                                <div id="other-payment-rows" class="payment-rows"></div>
                            </div>

                            <!-- Difference summary -->
                            <div class="glass-card">
                                <div class="card-title">
                                    <div class="icon">📋</div>
                                    Closing Reconciliation
                                </div>
                                <table class="summary-table">
                                    <thead>
                                        <tr>
                                            <th>Mode</th>
                                            <th>Expected</th>
                                            <th>Counted</th>
                                            <th>Difference</th>
                                        </tr>
                                    </thead>
                                    <tbody id="reconciliation-body"></tbody>
                                </table>
                            </div>

                            <!-- Difference alert -->
                            <div id="diff-alert" class="diff-alert" style="display:none;"></div>

                            <!-- Manager override panel -->
                            <div id="override-panel" class="override-panel">
                                <div class="override-title">🔐 Manager Approval Required</div>
                                <p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px;">
                                    Cash difference exceeds the allowed threshold. Enter manager password to proceed.
                                </p>
                                <div class="form-group">
                                    <label class="form-label">Manager Password</label>
                                    <input type="password" id="manager-override-pin"
                                           class="form-control" placeholder="Enter manager password"
                                           autocomplete="new-password" />
                                </div>
                            </div>

                            <!-- Notes -->
                            <div class="form-group">
                                <label class="form-label">Closing Notes (optional)</label>
                                <textarea id="closing-notes" class="form-control" rows="2"
                                          placeholder="Any notes for this shift…"></textarea>
                            </div>

                            <div class="btn-row">
                                <button class="btn-shift btn-ghost" onclick="smriti_shift._load_close_screen()">
                                    🔄 Refresh
                                </button>
                                <button id="btn-close-shift" class="btn-shift btn-danger">
                                    🌙 Close Shift
                                </button>
                            </div>
                        </div>

                    </div>

                    <!-- ══ SHIFT SUMMARY SCREEN ══ -->
                    <div id="summary-tab" class="shift-screen">

                        <div class="glass-card" id="no-summary-msg" style="display:none;">
                            <div class="card-title"><div class="icon">📊</div>No Active Shift</div>
                            <p style="color:var(--text-muted);font-size:14px;">Open a shift to view summary.</p>
                        </div>

                        <div id="summary-content">
                            <div class="kpi-grid" id="summary-kpi-grid"></div>
                            <div class="glass-card">
                                <div class="card-title"><div class="icon">📋</div>Sales by Payment Mode</div>
                                <table class="summary-table">
                                    <thead>
                                        <tr>
                                            <th>Mode</th>
                                            <th>Opening Float</th>
                                            <th>Sales</th>
                                            <th>Expected Closing</th>
                                        </tr>
                                    </thead>
                                    <tbody id="summary-mode-body"></tbody>
                                </table>
                            </div>
                            <div class="btn-row">
                                <button class="btn-shift btn-ghost" onclick="smriti_shift._load_summary()">
                                    🔄 Refresh
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- Toast -->
                <div id="shift-toast" class="shift-toast"></div>
            </div>
        `);

        // Tab switching
        $('#shift-tabs .shift-tab').on('click', (e) => {
            const tab = $(e.currentTarget).data('tab');
            this._show_tab(tab);
        });

        // Open shift
        $('#btn-open-shift').on('click', () => this._open_shift());

        // Close shift
        $('#btn-close-shift').on('click', () => this._close_shift());

        // Denomination inputs → live cash total
        $(document).on('input', '.denom-input', () => this._recalculate_denom_total());
    }

    // ─── Initial Data Load ────────────────────────────────────
    async _load_initial_data() {
        try {
            const [profiles, modes] = await Promise.all([
                this._call('smriti_retail_os.shift_api.get_pos_profiles'),
                this._call('smriti_retail_os.shift_api.get_payment_modes')
            ]);
            this.pos_profiles  = profiles || [];
            this.payment_modes = modes   || [];

            this._populate_pos_profiles();
            this._render_opening_payment_rows();
            await this._check_active_shift();
        } catch(err) {
            this._toast('Failed to load shift data. ' + (err.message || ''), 'error');
        }
    }

    _populate_pos_profiles() {
        const sel = $('#pos-profile-select');
        sel.empty();
        if (!this.pos_profiles.length) {
            sel.append('<option value="">No POS Profiles found</option>');
            return;
        }
        this.pos_profiles.forEach(p => {
            sel.append(`<option value="${p.name}">${p.name} (${p.company})</option>`);
        });
    }

    _render_opening_payment_rows() {
        const container = $('#opening-payment-rows');
        container.empty();
        const modes = this.payment_modes.length
            ? this.payment_modes
            : [{name: 'Cash'}, {name: 'Card'}, {name: 'UPI'}];

        modes.forEach(m => {
            const icon = this._mode_icon(m.name);
            container.append(`
                <div class="payment-row">
                    <div class="payment-row-label">
                        <div class="mode-icon ${this._mode_class(m.name)}">${icon}</div>
                        ${m.name}
                    </div>
                    <input type="number" min="0" step="0.01" value="0"
                           class="opening-amount-input" data-mode="${m.name}"
                           placeholder="0.00" />
                </div>
            `);
        });
    }

    async _check_active_shift() {
        try {
            const shift = await this._call('smriti_retail_os.shift_api.get_active_shift', {
                cashier: frappe.session.user
            });
            this.active_shift = shift || null;
            this._update_status_badge();

            if (this.active_shift) {
                this._show_active_shift_info();
            } else {
                $('#no-shift-panel').show();
                $('#shift-open-info').hide();
            }

            // Pre-load close + summary screens if shift is open
            if (this.active_shift) {
                this._load_close_screen();
                this._load_summary();
            } else {
                $('#no-active-shift-msg').show();
                $('#close-shift-form').hide();
                $('#no-summary-msg').show();
                $('#summary-content').hide();
            }
        } catch(e) {
            console.error('Check active shift error:', e);
        }
    }

    _show_active_shift_info() {
        $('#no-shift-panel').hide();
        $('#shift-open-info').show();

        const s = this.active_shift;
        const start = frappe.datetime.str_to_user(s.period_start_date) || s.period_start_date;
        $('#active-shift-info-bar').html(`
            <div class="shift-info-item">
                <div class="si-label">Cashier</div>
                <div class="si-value">${frappe.session.user_info?.fullname || frappe.session.user}</div>
            </div>
            <div class="sep"></div>
            <div class="shift-info-item">
                <div class="si-label">POS Profile</div>
                <div class="si-value">${s.pos_profile}</div>
            </div>
            <div class="sep"></div>
            <div class="shift-info-item">
                <div class="si-label">Opened At</div>
                <div class="si-value">${start}</div>
            </div>
            <div class="sep"></div>
            <div class="shift-info-item">
                <div class="si-label">Entry</div>
                <div class="si-value">${s.name}</div>
            </div>
        `);
    }

    _update_status_badge() {
        const badge = $('#shift-status-badge');
        if (this.active_shift) {
            badge.removeClass('closed').addClass('open');
            badge.html('<div class="dot"></div><span>Shift Open</span>');
        } else {
            badge.removeClass('open').addClass('closed');
            badge.html('<div class="dot"></div><span>No Active Shift</span>');
        }
    }

    // ─── Day Open ─────────────────────────────────────────────
    async _open_shift() {
        const pos_profile = $('#pos-profile-select').val();
        if (!pos_profile) {
            this._toast('Please select a POS Profile.', 'error');
            return;
        }

        const entries = [];
        $('.opening-amount-input').each(function() {
            entries.push({
                mode_of_payment: $(this).data('mode'),
                opening_amount: parseFloat($(this).val()) || 0
            });
        });

        const btn = $('#btn-open-shift');
        btn.prop('disabled', true).html('<div class="shift-spinner"></div> Opening…');

        try {
            const result = await this._call('smriti_retail_os.shift_api.open_shift', {
                cashier: frappe.session.user,
                pos_profile,
                opening_entries: JSON.stringify(entries)
            });

            this._toast(result.message || 'Shift opened successfully!', 'success');
            await this._check_active_shift();
            this._show_tab('summary-tab');
        } catch(err) {
            this._toast(err.message || 'Failed to open shift.', 'error');
        } finally {
            btn.prop('disabled', false).html('✅ Open Shift');
        }
    }

    // ─── Day Close Screen ─────────────────────────────────────
    async _load_close_screen() {
        if (!this.active_shift) {
            $('#no-active-shift-msg').show();
            $('#close-shift-form').hide();
            return;
        }

        $('#no-active-shift-msg').hide();
        $('#close-shift-form').show();

        try {
            this.shift_summary = await this._call(
                'smriti_retail_os.shift_api.get_shift_summary',
                { opening_entry_name: this.active_shift.name }
            );
            this._render_close_kpis();
            this._render_denom_grid();
            this._render_other_modes();
            this._update_reconciliation();
        } catch(err) {
            this._toast('Failed to load shift summary: ' + (err.message || ''), 'error');
        }
    }

    _render_close_kpis() {
        const s = this.shift_summary;
        $('#close-kpi-grid').html(`
            <div class="kpi-card">
                <div class="kpi-value">₹${this._fmt(s.total_sales)}</div>
                <div class="kpi-label">Total Sales</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">${s.invoice_count}</div>
                <div class="kpi-label">Invoices</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">${frappe.datetime.str_to_user(s.period_start_date) || '—'}</div>
                <div class="kpi-label">Shift Started</div>
            </div>
        `);
    }

    _render_denom_grid() {
        const grid = $('#denom-grid');
        grid.empty();
        this.denominations.forEach(d => {
            grid.append(`
                <div class="denom-card">
                    <div class="denom-label">₹${d}</div>
                    <input type="number" min="0" step="1" value="0"
                           class="denom-input" data-value="${d}" placeholder="0" />
                    <div class="denom-total" id="denom-total-${d}">= ₹0</div>
                </div>
            `);
        });
        this._recalculate_denom_total();
    }

    _render_other_modes() {
        const container = $('#other-payment-rows');
        container.empty();

        const s = this.shift_summary;
        const cash_key = 'Cash';

        // Show expected amounts for non-cash modes
        (s.closing_summary || []).filter(r => r.mode_of_payment !== cash_key).forEach(row => {
            const icon = this._mode_icon(row.mode_of_payment);
            container.append(`
                <div class="payment-row">
                    <div class="payment-row-label">
                        <div class="mode-icon ${this._mode_class(row.mode_of_payment)}">${icon}</div>
                        ${row.mode_of_payment}
                        <span style="font-size:11px;color:var(--text-muted);margin-left:8px;">
                            (Expected: ₹${this._fmt(row.expected_amount)})
                        </span>
                    </div>
                    <input type="number" min="0" step="0.01"
                           value="${this._fmt_raw(row.expected_amount)}"
                           class="closing-other-input" data-mode="${row.mode_of_payment}"
                           placeholder="0.00" />
                </div>
            `);
        });

        // Live reconciliation update
        $(document).off('input.closing').on('input.closing', '.closing-other-input', () => {
            this._update_reconciliation();
        });
    }

    _recalculate_denom_total() {
        let total = 0;
        $('.denom-input').each(function() {
            const count = parseInt($(this).val()) || 0;
            const val   = parseInt($(this).data('value'));
            const sub   = count * val;
            total += sub;
            $(`#denom-total-${val}`).text(`= ₹${sub.toLocaleString('en-IN')}`);
        });
        $('#denom-cash-total').text(total.toLocaleString('en-IN', {minimumFractionDigits: 2}));
        this._update_reconciliation();
    }

    _get_closing_entries() {
        const entries = {};

        // Cash from denominations
        let cash_total = 0;
        $('.denom-input').each(function() {
            cash_total += (parseInt($(this).val()) || 0) * parseInt($(this).data('value'));
        });
        entries['Cash'] = cash_total;

        // Other modes
        $('.closing-other-input').each(function() {
            entries[$(this).data('mode')] = parseFloat($(this).val()) || 0;
        });

        return entries;
    }

    _update_reconciliation() {
        if (!this.shift_summary) return;

        const closing_map = this._get_closing_entries();
        const tbody = $('#reconciliation-body');
        tbody.empty();

        let max_diff = 0;

        (this.shift_summary.closing_summary || []).forEach(row => {
            const mode = row.mode_of_payment;
            const expected = parseFloat(row.expected_amount) || 0;
            const counted  = parseFloat(closing_map[mode] || 0);
            const diff     = counted - expected;

            if (Math.abs(diff) > Math.abs(max_diff)) max_diff = diff;

            const diff_class = diff > 0 ? 'diff-positive' : diff < 0 ? 'diff-negative' : 'diff-zero';
            const diff_str   = diff === 0 ? '—' : (diff > 0 ? '+' : '') + '₹' + this._fmt(Math.abs(diff));

            tbody.append(`
                <tr>
                    <td>${mode}</td>
                    <td>₹${this._fmt(expected)}</td>
                    <td>₹${this._fmt(counted)}</td>
                    <td class="${diff_class}">${diff_str}</td>
                </tr>
            `);
        });

        // Difference alert
        const alert_div = $('#diff-alert');
        const THRESHOLD = 500;
        if (Math.abs(max_diff) === 0) {
            alert_div.hide();
        } else if (Math.abs(max_diff) <= THRESHOLD) {
            alert_div.show().removeClass('danger').addClass('warning').html(
                `⚠️ Cash variance of ₹${this._fmt(Math.abs(max_diff))} detected. Within acceptable threshold.`
            );
            $('#override-panel').removeClass('visible');
        } else {
            alert_div.show().removeClass('warning').addClass('danger').html(
                `🚨 Cash variance of ₹${this._fmt(Math.abs(max_diff))} exceeds threshold! Manager approval required.`
            );
            $('#override-panel').addClass('visible');
        }
    }

    // ─── Close Shift ──────────────────────────────────────────
    async _close_shift() {
        if (!this.active_shift) {
            this._toast('No active shift found.', 'error');
            return;
        }

        const closing_map = this._get_closing_entries();
        const entries = Object.entries(closing_map).map(([mode, amt]) => ({
            mode_of_payment: mode,
            closing_amount: amt
        }));

        const manager_pin = $('#manager-override-pin').val() || null;
        const notes       = $('#closing-notes').val() || null;

        const btn = $('#btn-close-shift');
        btn.prop('disabled', true).html('<div class="shift-spinner"></div> Closing…');

        try {
            const result = await this._call('smriti_retail_os.shift_api.close_shift', {
                opening_entry_name: this.active_shift.name,
                closing_entries: JSON.stringify(entries),
                manager_pin,
                notes
            });

            if (result.requires_override) {
                // Show override panel and prompt
                $('#override-panel').addClass('visible');
                $('#manager-override-pin').focus();
                this._toast(result.message, 'info');
                return;
            }

            // Success — shift closed
            this._show_close_success(result);
            this.active_shift  = null;
            this.shift_summary = null;
            this._update_status_badge();

            $('#shift-open-info').hide();
            $('#no-shift-panel').show();
            $('#no-active-shift-msg').show();
            $('#close-shift-form').hide();
            $('#no-summary-msg').show();
            $('#summary-content').hide();

        } catch(err) {
            this._toast(err.message || 'Failed to close shift.', 'error');
        } finally {
            btn.prop('disabled', false).html('🌙 Close Shift');
        }
    }

    _show_close_success(result) {
        frappe.msgprint({
            title: '✅ Shift Closed Successfully',
            message: `
                <div style="font-family:'Outfit',sans-serif;padding:8px 0;">
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
                        <div style="text-align:center;padding:16px;background:rgba(18,183,106,0.1);border-radius:8px;border:1px solid #12b76a;">
                            <div style="font-size:22px;font-weight:700;color:#12b76a;">₹${this._fmt(result.total_sales)}</div>
                            <div style="font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:0.6px;margin-top:4px;">Total Sales</div>
                        </div>
                        <div style="text-align:center;padding:16px;background:rgba(127,86,217,0.1);border-radius:8px;border:1px solid #7f56d9;">
                            <div style="font-size:22px;font-weight:700;color:#9e77ed;">${result.invoice_count}</div>
                            <div style="font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:0.6px;margin-top:4px;">Invoices</div>
                        </div>
                    </div>
                    <div style="font-size:13px;color:#888;text-align:center;">
                        Closing Entry: <strong style="color:#eee;">${result.closing_entry}</strong><br/>
                        Cash difference: <strong style="color:${result.cash_difference >= 0 ? '#12b76a' : '#f04438'};">
                            ${result.cash_difference >= 0 ? '+' : ''}₹${this._fmt(Math.abs(result.cash_difference))}
                        </strong>
                    </div>
                </div>
            `,
            indicator: 'green'
        });
    }

    // ─── Summary Screen ───────────────────────────────────────
    async _load_summary() {
        if (!this.active_shift) {
            $('#no-summary-msg').show();
            $('#summary-content').hide();
            return;
        }

        $('#no-summary-msg').hide();
        $('#summary-content').show();

        try {
            this.shift_summary = await this._call(
                'smriti_retail_os.shift_api.get_shift_summary',
                { opening_entry_name: this.active_shift.name }
            );
            this._render_summary();
        } catch(err) {
            this._toast('Failed to load summary.', 'error');
        }
    }

    _render_summary() {
        const s = this.shift_summary;
        const start = frappe.datetime.str_to_user(s.period_start_date) || s.period_start_date;

        $('#summary-kpi-grid').html(`
            <div class="kpi-card">
                <div class="kpi-value">₹${this._fmt(s.total_sales)}</div>
                <div class="kpi-label">Total Sales</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">${s.invoice_count}</div>
                <div class="kpi-label">Bills</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">${s.invoice_count > 0 ? '₹' + this._fmt(s.total_sales / s.invoice_count) : '—'}</div>
                <div class="kpi-label">Avg. Bill Value</div>
            </div>
        `);

        const tbody = $('#summary-mode-body');
        tbody.empty();
        (s.closing_summary || []).forEach(row => {
            tbody.append(`
                <tr>
                    <td>${row.mode_of_payment}</td>
                    <td>₹${this._fmt(row.opening_amount)}</td>
                    <td>₹${this._fmt(row.sales_amount)}</td>
                    <td>₹${this._fmt(row.expected_amount)}</td>
                </tr>
            `);
        });

        if (!(s.closing_summary || []).length) {
            tbody.append('<tr><td colspan="4" style="text-align:center;color:var(--text-muted);padding:20px;">No sales recorded yet.</td></tr>');
        }
    }

    // ─── Tab Navigation ───────────────────────────────────────
    _show_tab(tab_id) {
        $('.shift-tab').removeClass('active');
        $(`.shift-tab[data-tab="${tab_id}"]`).addClass('active');
        $('.shift-screen').removeClass('active');
        $(`#${tab_id}`).addClass('active');

        // Refresh data on tab switch
        if (tab_id === 'close-tab')   this._load_close_screen();
        if (tab_id === 'summary-tab') this._load_summary();
    }

    // ─── Helpers ─────────────────────────────────────────────
    _mode_icon(mode) {
        const m = (mode || '').toLowerCase();
        if (m.includes('cash'))  return '💵';
        if (m.includes('card'))  return '💳';
        if (m.includes('upi'))   return '📱';
        if (m.includes('cheque') || m.includes('check')) return '📄';
        return '💰';
    }

    _mode_class(mode) {
        const m = (mode || '').toLowerCase();
        if (m.includes('cash')) return 'cash';
        if (m.includes('card')) return 'card';
        if (m.includes('upi'))  return 'upi';
        return 'other';
    }

    _fmt(val) {
        return parseFloat(val || 0).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    _fmt_raw(val) {
        return parseFloat(val || 0).toFixed(2);
    }

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

    _toast(msg, type = 'info') {
        const el = $('#shift-toast');
        el.removeClass('success error info show').addClass(type);
        el.text(msg).addClass('show');
        clearTimeout(this._toast_timer);
        this._toast_timer = setTimeout(() => el.removeClass('show'), 3500);
    }
}
