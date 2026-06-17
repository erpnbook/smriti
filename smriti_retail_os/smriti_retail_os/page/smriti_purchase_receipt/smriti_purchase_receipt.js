/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_purchase_receipt/smriti_purchase_receipt.js
 * @description: SMRITI Purchase Receipts (GRN) Tracker page controller.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.0.0
 * @license: MIT
 */

frappe.pages['smriti-purchase-receipt'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Purchase Receipts (GRN) Tracker'),
        single_column: true
    });

    var controller = new SmritiPurchaseReceiptController(wrapper, page);
}

class SmritiPurchaseReceiptController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterReceiptsList = [];
        this.activeReceiptDoc = null;

        this.setup_layout();
        this.bind_actions();
        this.init();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-purchase-receipt-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Purchase Receipts (GRN) Tracker')}</span>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-pr-search" placeholder="${__('Search by GRN no or supplier name...')}">
                    <select class="form-input filter-select" id="smriti-pr-filter-status">
                        <option value="">${__('All Statuses')}</option>
                        <option value="Submitted">${__('Submitted')}</option>
                        <option value="Draft">${__('Draft')}</option>
                    </select>
                </div>

                <!-- Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Receipt Number (GRN)')}</th>
                                <th>${__('Date & Time')}</th>
                                <th>${__('Supplier')}</th>
                                <th style="text-align:right;">${__('Grand Total')}</th>
                                <th style="text-align:center;">${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-receipts-tbody">
                            <tr>
                                <td colspan="5" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading Purchase Receipts...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Slide Drawer -->
                <div class="drawer-backdrop" id="smriti-pr-drawer-backdrop">
                    <div class="drawer" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="drw-id">${__('Purchase Receipt Details')}</div>
                            <button class="drawer-close" id="smriti-pr-drawer-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <div class="section-card">
                                <div class="section-title">${__('General Summary')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Date & Time')}</span><span class="meta-value" id="drw-date"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Supplier')}</span><span class="meta-value" id="drw-supplier"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Status')}</span><span id="drw-status"></span></div>
                            </div>

                            <div class="section-card">
                                <div class="section-title">${__('Received Items')}</div>
                                <table class="invoice-items-table">
                                    <thead>
                                        <tr>
                                            <th>${__('Product Description')}</th>
                                            <th style="text-align:center;">${__('Qty')}</th>
                                            <th style="text-align:right;">${__('Rate')}</th>
                                            <th style="text-align:right;">${__('Total')}</th>
                                        </tr>
                                    </thead>
                                    <tbody id="drw-items-tbody"></tbody>
                                </table>
                            </div>

                            <div class="section-card">
                                <div class="section-title">${__('Breakdown')}</div>
                                <div class="meta-row" style="border-top:1px solid var(--border-dark); padding-top:8px; margin-top:8px; font-size:1.05rem;"><span class="meta-label" style="color:var(--text-color); font-weight:700;">${__('Grand Total')}</span><span class="meta-value" id="drw-grand" style="color:var(--success-color); font-weight:800;"></span></div>
                            </div>
                        </div>
                        <div class="drawer-footer">
                            <button class="btn-print" id="btn-print-grn">
                                <span class="material-symbols-outlined">print</span> ${__('Print GRN')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#smriti-pr-search").on("input", () => me.apply_filters());
        this.wrapper.find("#smriti-pr-filter-status").on("change", () => me.apply_filters());

        this.wrapper.find("#smriti-pr-drawer-close").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-pr-drawer-backdrop").on("click", () => me.close_drawer());
        this.wrapper.find("#btn-print-grn").on("click", () => me.print_receipt());
    }

    init() {
        this.load_receipts();
    }

    load_receipts() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Purchase Receipt',
                fields: ['name', 'posting_date', 'posting_time', 'supplier_name', 'grand_total', 'status', 'docstatus'],
                order_by: 'posting_date desc, posting_time desc',
                limit_page_length: 150
            },
            callback: function(r) {
                me.masterReceiptsList = r.message || [];
                me.render_table(me.masterReceiptsList);
            }
        });
    }

    render_table(list) {
        var me = this;
        const tbody = this.wrapper.find('#smriti-receipts-tbody');
        tbody.empty();

        if (!list.length) {
            tbody.html(`<tr><td colspan="5" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No Purchase Receipts tracked.')}</td></tr>`);
            return;
        }

        list.forEach(pr => {
            const statusText = pr.docstatus === 1 ? 'Submitted' : 'Draft';
            const statusCls = statusText.toLowerCase();
            const tr = $(`
                <tr data-id="${pr.name}">
                    <td><span class="invoice-badge">${pr.name}</span></td>
                    <td>
                        <div style="font-weight:600;">${pr.posting_date}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted-color); margin-top:2px;">${pr.posting_time || ''}</div>
                    </td>
                    <td style="font-weight:600; color:var(--text-color);">${pr.supplier_name}</td>
                    <td style="text-align:right; font-weight:700; color:var(--success-color);">Rs. ${parseFloat(pr.grand_total).toFixed(2)}</td>
                    <td style="text-align:center;">
                        <span class="status-badge ${statusCls}">${statusText}</span>
                    </td>
                </tr>
            `);
            tr.on("click", function() {
                me.load_receipt_details($(this).data("id"));
            });
            tbody.append(tr);
        });
    }

    apply_filters() {
        const q = this.wrapper.find('#smriti-pr-search').val().toLowerCase();
        const status = this.wrapper.find('#smriti-pr-filter-status').val();

        let filtered = this.masterReceiptsList;

        if (q) {
            filtered = filtered.filter(pr => 
                pr.name.toLowerCase().includes(q) ||
                pr.supplier_name.toLowerCase().includes(q)
            );
        }
        if (status) {
            filtered = filtered.filter(pr => {
                const statusText = pr.docstatus === 1 ? 'Submitted' : 'Draft';
                return statusText === status;
            });
        }

        this.render_table(filtered);
    }

    load_receipt_details(receiptId) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Purchase Receipt',
                name: receiptId
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.activeReceiptDoc = doc;

                    me.wrapper.find('#drw-id').text(doc.name);
                    me.wrapper.find('#drw-date').text(`${doc.posting_date} | ${doc.posting_time || ''}`);
                    me.wrapper.find('#drw-supplier').text(doc.supplier_name);
                    
                    const statusEl = me.wrapper.find('#drw-status');
                    const statusText = doc.docstatus === 1 ? 'Submitted' : 'Draft';
                    statusEl.attr('class', `status-badge ${statusText.toLowerCase()}`);
                    statusEl.text(statusText);

                    // Render Items
                    const tbody = me.wrapper.find('#drw-items-tbody');
                    tbody.empty();
                    doc.items.forEach(it => {
                        tbody.append(`
                            <tr>
                                <td>
                                    <div style="font-weight:600;color:var(--text-color);">${it.item_name}</div>
                                    <div style="font-size:0.75rem;color:var(--text-muted-color);margin-top:2px;">${it.item_code}</div>
                                </td>
                                <td style="text-align:center;font-weight:600;">${it.qty}</td>
                                <td style="text-align:right;">Rs. ${parseFloat(it.rate).toFixed(2)}</td>
                                <td style="text-align:right;font-weight:600;">Rs. ${parseFloat(it.amount).toFixed(2)}</td>
                            </tr>
                        `);
                    });

                    me.wrapper.find('#drw-grand').text(`Rs. ${parseFloat(doc.grand_total).toFixed(2)}`);
                    me.wrapper.find('#smriti-pr-drawer-backdrop').addClass('open');
                }
            }
        });
    }

    print_receipt() {
        if (!this.activeReceiptDoc) return;
        const url = `/printview?doctype=Purchase%20Receipt&name=${encodeURIComponent(this.activeReceiptDoc.name)}`;
        window.open(url, '_blank');
    }

    close_drawer() {
        this.wrapper.find('#smriti-pr-drawer-backdrop').removeClass('open');
        this.activeReceiptDoc = null;
    }
}
