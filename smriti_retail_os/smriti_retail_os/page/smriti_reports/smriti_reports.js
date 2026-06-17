/**
 * @file: smriti_retail_os/public/js/smriti_reports.js
 * @description: Frontend controller for SMRITI Custom Reports page..
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ─────────────────────────────────────────────
   SMRITI Reports — Phase 6
   4 Report types: Sales | Stock | GST | Outstanding
   All data from ERPNbook via reports_api.py
   ───────────────────────────────────────────── */

window.SMRITIReports = (function () {

    const API = "smriti_retail_os.reports_api";
    let _wrapper = null;
    let _activeTab = "sales";
    let _state = {};

    // ── Format helpers ──────────────────────
    function fmt_currency(v) {
        if (v === undefined || v === null) return "₹0";
        return "₹" + parseFloat(v).toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    function fmt_qty(v) {
        return parseFloat(v || 0).toLocaleString("en-IN");
    }
    function today_str() {
        return frappe.datetime.get_today();
    }
    function month_start() {
        const d = new Date();
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-01`;
    }
    function yesterday_str() {
        return frappe.datetime.add_days(today_str(), -1);
    }
    function week_start() {
        return frappe.datetime.add_days(today_str(), -6);
    }

    // ── Init ──────────────────────────────
    function init(wrapper) {
        _wrapper = wrapper;
        _state = {
            sales: { from: today_str(), to: today_str(), gran: "hourly" },
            stock: { warehouse: "", item_group: "", show_zero: 0 },
            gst:   { from: month_start(), to: today_str() },
            outstanding: { days: 0 }
        };

        $(wrapper).find(".page-head").hide();
        const $body = $(wrapper).find(".page-content, .container, main").first();
        if ($body.length === 0) {
            $(wrapper).append('<div class="smriti-reports-wrap" id="sr-root"></div>');
        } else {
            $body.html('<div class="smriti-reports-wrap" id="sr-root"></div>');
        }
        _render();
    }

    // ── Root render ───────────────────────
    function _render() {
        const $root = $("#sr-root");
        $root.html(`
            ${_html_tabs()}
            <div id="sr-filter-area"></div>
            <div class="sr-content" id="sr-main"></div>
        `);
        _bind_tabs();
        _switch_tab(_activeTab);
    }

    // ── Tabs ──────────────────────────────
    function _html_tabs() {
        const tabs = [
            { id: "sales",       icon: "💳", label: "Sales" },
            { id: "stock",       icon: "📦", label: "Stock" },
            { id: "gst",         icon: "🧾", label: "GST" },
            { id: "outstanding", icon: "⏳", label: "Outstanding" }
        ];
        return `<div class="sr-tabs">
            ${tabs.map(t => `
                <div class="sr-tab ${_activeTab === t.id ? "active" : ""}"
                     data-tab="${t.id}">
                    <span class="tab-icon">${t.icon}</span>${t.label}
                </div>`).join("")}
        </div>`;
    }

    function _bind_tabs() {
        $(document).on("click.sr-tabs", ".sr-tab", function () {
            _activeTab = $(this).data("tab");
            $(".sr-tab").removeClass("active");
            $(this).addClass("active");
            _switch_tab(_activeTab);
        });
    }

    function _switch_tab(tab) {
        const filterFns = {
            sales:       _render_sales_filters,
            stock:       _render_stock_filters,
            gst:         _render_gst_filters,
            outstanding: _render_outstanding_filters
        };
        const loadFns = {
            sales:       _load_sales,
            stock:       _load_stock,
            gst:         _load_gst,
            outstanding: _load_outstanding
        };
        filterFns[tab] && filterFns[tab]();
        loadFns[tab] && loadFns[tab]();
    }

    // ── Loading / Empty ───────────────────
    function _show_loading() {
        $("#sr-main").html(`<div class="sr-loading">
            <div class="sr-spinner"></div> Loading report…
        </div>`);
    }
    function _show_empty(icon, msg) {
        $("#sr-main").html(`<div class="sr-empty">
            <div class="sr-empty-icon">${icon}</div>
            <div class="sr-empty-text">${msg}</div>
        </div>`);
    }

    // ─────────────────────────────────────
    // ══ SALES REPORT ══
    // ─────────────────────────────────────

    function _render_sales_filters() {
        const s = _state.sales;
        $("#sr-filter-area").html(`
            <div class="sr-filter-bar">
                <label>From</label>
                <input type="date" id="sr-sf-from" value="${s.from}">
                <label>To</label>
                <input type="date" id="sr-sf-to" value="${s.to}">
                <button class="sr-btn sr-btn-primary" id="sr-sf-go">
                    📊 Generate
                </button>
                <div class="sr-quick-btns">
                    <button class="sr-quick-btn" data-range="today">Today</button>
                    <button class="sr-quick-btn" data-range="yesterday">Yesterday</button>
                    <button class="sr-quick-btn" data-range="week">This Week</button>
                    <button class="sr-quick-btn" data-range="month">This Month</button>
                </div>
            </div>
        `);

        $("#sr-sf-go").on("click", function () {
            _state.sales.from = $("#sr-sf-from").val();
            _state.sales.to   = $("#sr-sf-to").val();
            _state.sales.gran = (_state.sales.from === _state.sales.to) ? "hourly" : "daily";
            _load_sales();
        });

        $(".sr-quick-btn").on("click", function () {
            $(".sr-quick-btn").removeClass("active");
            $(this).addClass("active");
            const range = $(this).data("range");
            let from, to;
            if (range === "today")     { from = to = today_str(); }
            if (range === "yesterday") { from = to = yesterday_str(); }
            if (range === "week")      { from = week_start(); to = today_str(); }
            if (range === "month")     { from = month_start(); to = today_str(); }
            _state.sales.from = from;
            _state.sales.to   = to;
            _state.sales.gran = (from === to) ? "hourly" : "daily";
            $("#sr-sf-from").val(from);
            $("#sr-sf-to").val(to);
            _load_sales();
        });
    }

    function _load_sales() {
        _show_loading();
        frappe.call({
            method: `${API}.get_sales_report`,
            args: {
                from_date:   _state.sales.from,
                to_date:     _state.sales.to,
                granularity: _state.sales.gran
            },
            callback: function (r) {
                if (r.message) _render_sales(r.message);
                else _show_empty("📊", "No sales data for selected period.");
            }
        });
    }

    function _render_sales(d) {
        const s = d.summary;
        const growth_icon = s.sales_growth > 0 ? "▲" : "▼";
        const growth_cls  = s.sales_growth > 0 ? "kpi-up" : "kpi-down";

        // KPI cards
        let kpi_html = `<div class="sr-kpis">
            <div class="sr-kpi" style="--kpi-color:#e94560">
                <div class="sr-kpi-icon">💳</div>
                <div class="sr-kpi-label">Total Sales</div>
                <div class="sr-kpi-value">${fmt_currency(s.total_sales)}</div>
                <div class="sr-kpi-sub">${s.total_bills} bills</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#10b981">
                <div class="sr-kpi-icon">📋</div>
                <div class="sr-kpi-label">Taxable Value</div>
                <div class="sr-kpi-value">${fmt_currency(s.total_net)}</div>
                <div class="sr-kpi-sub">Net of GST</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#f59e0b">
                <div class="sr-kpi-icon">🧾</div>
                <div class="sr-kpi-label">GST Collected</div>
                <div class="sr-kpi-value">${fmt_currency(s.total_tax)}</div>
                <div class="sr-kpi-sub">Tax amount</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#8b5cf6">
                <div class="sr-kpi-icon">🎁</div>
                <div class="sr-kpi-label">Discounts</div>
                <div class="sr-kpi-value">${fmt_currency(s.total_discount)}</div>
                <div class="sr-kpi-sub">Given away</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#06b6d4">
                <div class="sr-kpi-icon">📈</div>
                <div class="sr-kpi-label">Avg Bill Value</div>
                <div class="sr-kpi-value">${fmt_currency(s.avg_bill)}</div>
                <div class="sr-kpi-sub">Per transaction</div>
            </div>
        </div>`;

        // Chart breakdown
        const breakdown = d.breakdown || [];
        const max_val   = Math.max(...breakdown.map(b => b.sales), 1);
        let chart_html  = breakdown.map(b => {
            const pct = Math.max((b.sales / max_val) * 100, 2).toFixed(1);
            const label = _state.sales.gran === "hourly" ? (b.hour || b.date) : b.date;
            return `<div class="sr-bar-row">
                <div class="sr-bar-label">${label}</div>
                <div class="sr-bar-track">
                    <div class="sr-bar-fill" style="width:${pct}%"></div>
                </div>
                <div class="sr-bar-value">${fmt_currency(b.sales)}</div>
            </div>`;
        }).join("") || '<div style="color:var(--smriti-text-muted);font-size:13px;text-align:center;padding:20px">No breakdown data</div>';

        // Payment breakdown
        const pmode_icons = { "Cash": "💵", "Card": "💳", "UPI": "📱", "Cheque": "📝" };
        let pay_html = (d.payment_breakdown || []).map(p => {
            const icon = pmode_icons[p.mode_of_payment] || "💰";
            return `<div class="sr-payment-pill">
                <div class="sr-pill-icon" style="background:rgba(233,69,96,0.1)">${icon}</div>
                <div class="sr-pill-info">
                    <div class="sr-pill-name">${p.mode_of_payment}</div>
                    <div class="sr-pill-amount">${fmt_currency(p.total)}</div>
                </div>
            </div>`;
        }).join("") || '<div style="color:var(--smriti-text-muted);font-size:12px">No payment data</div>';

        // Top items
        let items_html = `<div class="sr-table-wrap"><table class="sr-table">
            <thead><tr>
                <th>#</th><th>Item</th>
                <th class="num">Qty Sold</th>
                <th class="num">Amount</th>
            </tr></thead><tbody>
            ${(d.top_items || []).map((item, i) => `<tr>
                <td>${i + 1}</td>
                <td>${frappe.utils.escape_html(item.item_name || item.item_code)}</td>
                <td class="num">${fmt_qty(item.total_qty)}</td>
                <td class="num">${fmt_currency(item.total_amount)}</td>
            </tr>`).join("") || '<tr><td colspan="4" style="text-align:center;color:var(--smriti-text-muted)">No items data</td></tr>'}
            </tbody></table></div>`;

        // Cashier summary
        let cashier_html = `<div class="sr-table-wrap"><table class="sr-table">
            <thead><tr>
                <th>Cashier</th>
                <th class="num">Bills</th>
                <th class="num">Sales</th>
            </tr></thead><tbody>
            ${(d.cashier_summary || []).map(c => `<tr>
                <td>${frappe.utils.escape_html(c.cashier || "Unknown")}</td>
                <td class="num">${c.bills}</td>
                <td class="num">${fmt_currency(c.total_sales)}</td>
            </tr>`).join("") || '<tr><td colspan="3" style="text-align:center;color:var(--smriti-text-muted)">No cashier data</td></tr>'}
            </tbody></table></div>`;

        $("#sr-main").html(`
            ${kpi_html}
            <div class="sr-section-title">📈 ${_state.sales.gran === "hourly" ? "Hourly" : "Daily"} Trend</div>
            <div class="sr-card" style="margin-bottom:24px">
                <div class="sr-bar-chart">${chart_html}</div>
            </div>
            <div class="sr-grid-2">
                <div class="sr-card">
                    <div class="sr-card-title">💳 Payment Methods</div>
                    <div class="sr-payment-pills">${pay_html}</div>
                </div>
                <div class="sr-card">
                    <div class="sr-card-title">👥 Cashier Performance</div>
                    ${cashier_html}
                </div>
            </div>
            <div class="sr-section-title">🏆 Top Items by Quantity</div>
            ${items_html}
        `);
    }

    // ─────────────────────────────────────
    // ══ STOCK REPORT ══
    // ─────────────────────────────────────

    function _render_stock_filters() {
        $("#sr-filter-area").html(`
            <div class="sr-filter-bar">
                <label>Warehouse</label>
                <select id="sr-stk-wh"><option value="">All Warehouses</option></select>
                <label>Item Group</label>
                <input type="text" id="sr-stk-grp" placeholder="All groups"
                    style="background:var(--smriti-surface2);border:1px solid var(--smriti-border);color:var(--smriti-text);padding:7px 12px;border-radius:6px;font-size:13px;font-family:Inter,sans-serif">
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
                    <input type="checkbox" id="sr-stk-zero"> Show zero stock
                </label>
                <button class="sr-btn sr-btn-primary" id="sr-stk-go">📊 Generate</button>
            </div>
        `);

        // Load warehouses
        frappe.call({
            method: `${API}.get_stock_report`,
            args: { warehouse: "", show_zero: 0 },
            callback: function (r) {
                if (r.message && r.message.warehouses) {
                    r.message.warehouses.forEach(w => {
                        $("#sr-stk-wh").append(
                            `<option value="${w.name}">${w.warehouse_name}</option>`
                        );
                    });
                }
                _render_stock(r.message);
            }
        });

        $("#sr-stk-go").on("click", function () {
            _state.stock.warehouse  = $("#sr-stk-wh").val();
            _state.stock.item_group = $("#sr-stk-grp").val();
            _state.stock.show_zero  = $("#sr-stk-zero").is(":checked") ? 1 : 0;
            _load_stock();
        });
    }

    function _load_stock() {
        _show_loading();
        frappe.call({
            method: `${API}.get_stock_report`,
            args: {
                warehouse:  _state.stock.warehouse,
                item_group: _state.stock.item_group,
                show_zero:  _state.stock.show_zero
            },
            callback: function (r) {
                if (r.message) _render_stock(r.message);
                else _show_empty("📦", "No stock data found.");
            }
        });
    }

    function _render_stock(d) {
        if (!d) return _show_empty("📦", "No stock data found.");
        const items = d.items || [];

        let kpi_html = `<div class="sr-kpis">
            <div class="sr-kpi" style="--kpi-color:#10b981">
                <div class="sr-kpi-icon">📦</div>
                <div class="sr-kpi-label">Total SKUs</div>
                <div class="sr-kpi-value">${d.total_items}</div>
                <div class="sr-kpi-sub">With stock</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#e94560">
                <div class="sr-kpi-icon">💰</div>
                <div class="sr-kpi-label">Stock Value</div>
                <div class="sr-kpi-value">${fmt_currency(d.total_value)}</div>
                <div class="sr-kpi-sub">At cost</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#f59e0b">
                <div class="sr-kpi-icon">⚠️</div>
                <div class="sr-kpi-label">Low Stock Items</div>
                <div class="sr-kpi-value">${(d.low_stock || []).length}</div>
                <div class="sr-kpi-sub">≤ 5 units</div>
            </div>
        </div>`;

        let table_html = `<div class="sr-table-wrap"><table class="sr-table">
            <thead><tr>
                <th>Item Code</th>
                <th>Item Name</th>
                <th>Group</th>
                <th class="num">On Hand</th>
                <th class="num">Reserved</th>
                <th class="num">Available</th>
                <th class="num">Rate (₹)</th>
                <th class="num">Value (₹)</th>
                <th>Warehouse</th>
            </tr></thead><tbody>
            ${items.length ? items.map(item => {
                const low = item.available_qty <= 5;
                return `<tr class="${low ? "low-stock-row" : ""}">
                    <td><code style="color:var(--smriti-primary)">${frappe.utils.escape_html(item.item_code)}</code></td>
                    <td>${frappe.utils.escape_html(item.item_name)}</td>
                    <td>${frappe.utils.escape_html(item.item_group || "—")}</td>
                    <td class="num">${fmt_qty(item.actual_qty)}</td>
                    <td class="num">${fmt_qty(item.reserved_qty)}</td>
                    <td class="num">${low ? `<span class="sr-badge sr-badge-red">` : ""}${fmt_qty(item.available_qty)}${low ? "</span>" : ""}</td>
                    <td class="num">${fmt_currency(item.valuation_rate)}</td>
                    <td class="num">${fmt_currency(item.stock_value)}</td>
                    <td style="font-size:11px;color:var(--smriti-text-muted)">${frappe.utils.escape_html(item.warehouse)}</td>
                </tr>`;
            }).join("") : '<tr><td colspan="9" style="text-align:center;color:var(--smriti-text-muted);padding:40px">No items found</td></tr>'}
            </tbody></table></div>`;

        $("#sr-main").html(`
            ${kpi_html}
            <div class="sr-section-title" style="justify-content:space-between">
                <span>📦 Stock Position</span>
                <button class="sr-export-btn" id="sr-stk-export">⬇️ Export CSV</button>
            </div>
            ${table_html}
        `);

        $("#sr-stk-export").on("click", function () {
            _export_csv(items, [
                "item_code", "item_name", "item_group",
                "actual_qty", "reserved_qty", "available_qty",
                "valuation_rate", "stock_value", "warehouse"
            ], "smriti_stock_report");
        });
    }

    // ─────────────────────────────────────
    // ══ GST REPORT ══
    // ─────────────────────────────────────

    function _render_gst_filters() {
        const s = _state.gst;
        $("#sr-filter-area").html(`
            <div class="sr-filter-bar">
                <label>From</label>
                <input type="date" id="sr-gst-from" value="${s.from}">
                <label>To</label>
                <input type="date" id="sr-gst-to" value="${s.to}">
                <button class="sr-btn sr-btn-primary" id="sr-gst-go">📊 Generate</button>
                <div class="sr-quick-btns">
                    <button class="sr-quick-btn" data-grange="month">This Month</button>
                    <button class="sr-quick-btn" data-grange="last_month">Last Month</button>
                    <button class="sr-quick-btn" data-grange="quarter">This Quarter</button>
                </div>
            </div>
        `);
        $("#sr-gst-go").on("click", function () {
            _state.gst.from = $("#sr-gst-from").val();
            _state.gst.to   = $("#sr-gst-to").val();
            _load_gst();
        });
        $("[data-grange]").on("click", function () {
            $("[data-grange]").removeClass("active");
            $(this).addClass("active");
            const range = $(this).data("grange");
            let from, to;
            const now = new Date();
            if (range === "month") {
                from = month_start(); to = today_str();
            } else if (range === "last_month") {
                const lm = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                from = `${lm.getFullYear()}-${String(lm.getMonth()+1).padStart(2,"0")}-01`;
                const le = new Date(now.getFullYear(), now.getMonth(), 0);
                to = `${le.getFullYear()}-${String(le.getMonth()+1).padStart(2,"0")}-${String(le.getDate()).padStart(2,"0")}`;
            } else if (range === "quarter") {
                const qm = Math.floor(now.getMonth() / 3) * 3;
                from = `${now.getFullYear()}-${String(qm+1).padStart(2,"0")}-01`;
                to = today_str();
            }
            _state.gst.from = from; _state.gst.to = to;
            $("#sr-gst-from").val(from); $("#sr-gst-to").val(to);
            _load_gst();
        });
        _load_gst();
    }

    function _load_gst() {
        _show_loading();
        frappe.call({
            method: `${API}.get_gst_report`,
            args: { from_date: _state.gst.from, to_date: _state.gst.to },
            callback: function (r) {
                if (r.message) _render_gst(r.message);
                else _show_empty("🧾", "No GST data for selected period.");
            }
        });
    }

    function _render_gst(d) {
        const s   = d.summary || {};
        const b2c = d.b2c || {};
        const tax  = d.tax_breakdown || [];

        let kpi_html = `<div class="sr-kpis">
            <div class="sr-kpi" style="--kpi-color:#e94560">
                <div class="sr-kpi-icon">🧾</div>
                <div class="sr-kpi-label">Total Invoices</div>
                <div class="sr-kpi-value">${s.total_invoices || 0}</div>
                <div class="sr-kpi-sub">Submitted bills</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#10b981">
                <div class="sr-kpi-icon">📋</div>
                <div class="sr-kpi-label">Taxable Value</div>
                <div class="sr-kpi-value">${fmt_currency(s.taxable_value)}</div>
                <div class="sr-kpi-sub">Net amount</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#f59e0b">
                <div class="sr-kpi-icon">💸</div>
                <div class="sr-kpi-label">Total GST</div>
                <div class="sr-kpi-value">${fmt_currency(s.total_tax)}</div>
                <div class="sr-kpi-sub">To deposit</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#8b5cf6">
                <div class="sr-kpi-icon">💰</div>
                <div class="sr-kpi-label">Gross Turnover</div>
                <div class="sr-kpi-value">${fmt_currency(s.total_with_tax)}</div>
                <div class="sr-kpi-sub">Incl. GST</div>
            </div>
        </div>`;

        // Tax breakdown table
        let tax_table = `<div class="sr-table-wrap"><table class="sr-table">
            <thead><tr>
                <th>Account Head</th>
                <th class="num">Rate %</th>
                <th class="num">Tax Amount</th>
                <th class="num">Invoices</th>
            </tr></thead><tbody>
            ${tax.length ? tax.map(t => `<tr>
                <td>${frappe.utils.escape_html(t.description || t.account_head)}</td>
                <td class="num">${flt(t.rate, 1)}%</td>
                <td class="num">${fmt_currency(t.tax_amount)}</td>
                <td class="num">${t.invoice_count}</td>
            </tr>`).join("") : '<tr><td colspan="4" style="text-align:center;color:var(--smriti-text-muted);padding:30px">No tax breakdown data</td></tr>'}
            </tbody></table></div>`;

        // B2C card
        let b2c_html = `<div class="sr-card">
            <div class="sr-card-title">🛒 B2C Summary (Walk-In / No GSTIN)</div>
            <div class="sr-kpis" style="margin-bottom:0">
                <div class="sr-kpi" style="--kpi-color:#06b6d4">
                    <div class="sr-kpi-label">Bills</div>
                    <div class="sr-kpi-value">${b2c.bills || 0}</div>
                </div>
                <div class="sr-kpi" style="--kpi-color:#06b6d4">
                    <div class="sr-kpi-label">Taxable</div>
                    <div class="sr-kpi-value">${fmt_currency(b2c.taxable)}</div>
                </div>
                <div class="sr-kpi" style="--kpi-color:#06b6d4">
                    <div class="sr-kpi-label">GST</div>
                    <div class="sr-kpi-value">${fmt_currency(b2c.tax)}</div>
                </div>
                <div class="sr-kpi" style="--kpi-color:#06b6d4">
                    <div class="sr-kpi-label">Total</div>
                    <div class="sr-kpi-value">${fmt_currency(b2c.total)}</div>
                </div>
            </div>
        </div>`;

        $("#sr-main").html(`
            ${kpi_html}
            ${b2c_html}
            <div class="sr-section-title" style="margin-top:24px">📊 Tax Account-wise Breakdown</div>
            ${tax_table}
            <div style="margin-top:16px;padding:14px 16px;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.3);border-radius:8px;font-size:12px;color:#f59e0b">
                ⚠️ This is a summary view only. For GSTR-1 statutory filing, contact your accountant or administrator — access India Compliance GST Reports via SMRITI Platform Center.
            </div>
        `);
    }

    // ─────────────────────────────────────
    // ══ OUTSTANDING REPORT ══
    // ─────────────────────────────────────

    function _render_outstanding_filters() {
        $("#sr-filter-area").html(`
            <div class="sr-filter-bar">
                <label>Customer</label>
                <input type="text" id="sr-out-cust" placeholder="All customers"
                    style="background:var(--smriti-surface2);border:1px solid var(--smriti-border);color:var(--smriti-text);padding:7px 12px;border-radius:6px;font-size:13px;font-family:Inter,sans-serif">
                <label>Overdue ≥</label>
                <select id="sr-out-days">
                    <option value="0">All</option>
                    <option value="1">1+ Days</option>
                    <option value="30">30+ Days</option>
                    <option value="60">60+ Days</option>
                    <option value="90">90+ Days</option>
                </select>
                <button class="sr-btn sr-btn-primary" id="sr-out-go">📊 Generate</button>
            </div>
        `);
        $("#sr-out-go").on("click", function () {
            _state.outstanding.customer = $("#sr-out-cust").val();
            _state.outstanding.days     = $("#sr-out-days").val();
            _load_outstanding();
        });
        _load_outstanding();
    }

    function _load_outstanding() {
        _show_loading();
        frappe.call({
            method: `${API}.get_outstanding_report`,
            args: {
                customer:    _state.outstanding.customer || "",
                days_overdue: _state.outstanding.days || 0
            },
            callback: function (r) {
                if (r.message) _render_outstanding(r.message);
                else _show_empty("⏳", "No outstanding invoices.");
            }
        });
    }

    function _render_outstanding(d) {
        const aging = d.aging || {};

        let kpi_html = `<div class="sr-kpis">
            <div class="sr-kpi" style="--kpi-color:#e94560">
                <div class="sr-kpi-icon">💰</div>
                <div class="sr-kpi-label">Total Outstanding</div>
                <div class="sr-kpi-value">${fmt_currency(d.total_outstanding)}</div>
                <div class="sr-kpi-sub">${d.total_invoices} invoices</div>
            </div>
            <div class="sr-kpi" style="--kpi-color:#f59e0b">
                <div class="sr-kpi-icon">⚠️</div>
                <div class="sr-kpi-label">Overdue Invoices</div>
                <div class="sr-kpi-value">${d.overdue_count}</div>
                <div class="sr-kpi-sub">Past due date</div>
            </div>
        </div>`;

        let aging_html = `<div class="sr-aging">
            <div class="sr-aging-bucket">
                <div class="bucket-label">Current</div>
                <div class="bucket-value">${fmt_currency(aging.current)}</div>
            </div>
            <div class="sr-aging-bucket">
                <div class="bucket-label">1–30 Days</div>
                <div class="bucket-value">${fmt_currency(aging["1_30"])}</div>
            </div>
            <div class="sr-aging-bucket">
                <div class="bucket-label">31–60 Days</div>
                <div class="bucket-value">${fmt_currency(aging["31_60"])}</div>
            </div>
            <div class="sr-aging-bucket">
                <div class="bucket-label">61–90 Days</div>
                <div class="bucket-value">${fmt_currency(aging["61_90"])}</div>
            </div>
            <div class="sr-aging-bucket" style="border-color:rgba(239,68,68,0.4)">
                <div class="bucket-label">90+ Days</div>
                <div class="bucket-value" style="color:#ef4444">${fmt_currency(aging.above_90)}</div>
            </div>
        </div>`;

        let table_html = `<div class="sr-table-wrap"><table class="sr-table">
            <thead><tr>
                <th>Invoice</th>
                <th>Customer</th>
                <th>Posting Date</th>
                <th>Due Date</th>
                <th class="num">Invoice Amt</th>
                <th class="num">Outstanding</th>
                <th>Status</th>
            </tr></thead><tbody>
            ${d.invoices.length ? d.invoices.map(inv => {
                const badge_cls = inv.overdue_days > 90 ? "sr-badge-red"
                    : inv.overdue_days > 0 ? "sr-badge-yellow"
                    : "sr-badge-green";
                const badge_txt = inv.overdue_days > 0
                    ? `${inv.overdue_days}d overdue`
                    : "Current";
                return `<tr>
                    <td><a href="/app/sales-invoice/${inv.invoice}" style="color:var(--smriti-primary)">${inv.invoice}</a></td>
                    <td>${frappe.utils.escape_html(inv.customer_name || inv.customer)}</td>
                    <td>${inv.posting_date}</td>
                    <td>${inv.due_date}</td>
                    <td class="num">${fmt_currency(inv.grand_total)}</td>
                    <td class="num" style="font-weight:600;color:var(--smriti-primary)">${fmt_currency(inv.outstanding)}</td>
                    <td><span class="sr-badge ${badge_cls}">${badge_txt}</span></td>
                </tr>`;
            }).join("") : '<tr><td colspan="7" style="text-align:center;color:var(--smriti-text-muted);padding:40px">No outstanding invoices</td></tr>'}
            </tbody></table></div>`;

        $("#sr-main").html(`
            ${kpi_html}
            <div class="sr-section-title">⏳ Aging Buckets</div>
            ${aging_html}
            <div class="sr-section-title" style="justify-content:space-between">
                <span>📋 Invoice Details</span>
                <button class="sr-export-btn" id="sr-out-export">⬇️ Export CSV</button>
            </div>
            ${table_html}
        `);

        $("#sr-out-export").on("click", function () {
            _export_csv(d.invoices, [
                "invoice", "customer", "customer_name",
                "posting_date", "due_date",
                "grand_total", "outstanding", "overdue_days", "status"
            ], "smriti_outstanding_report");
        });
    }

    // ─────────────────────────────────────
    // ══ CSV EXPORT ══
    // ─────────────────────────────────────

    function _export_csv(data, cols, filename) {
        if (!data || !data.length) {
            frappe.msgprint("No data to export."); return;
        }
        const header = cols.join(",");
        const rows   = data.map(row =>
            cols.map(c => {
                const v = row[c];
                if (v === null || v === undefined) return "";
                const s = String(v).replace(/"/g, '""');
                return /[,"\n]/.test(s) ? `"${s}"` : s;
            }).join(",")
        );
        const csv_content = [header, ...rows].join("\n");
        const blob  = new Blob([csv_content], { type: "text/csv;charset=utf-8;" });
        const url   = URL.createObjectURL(blob);
        const link  = document.createElement("a");
        link.href   = url;
        link.setAttribute("download", `${filename}_${today_str()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    // Small flt helper (like Python's flt)
    function flt(v, decimals) {
        const n = parseFloat(v || 0);
        return isNaN(n) ? 0 : decimals !== undefined ? parseFloat(n.toFixed(decimals)) : n;
    }

    return { init };

})();
