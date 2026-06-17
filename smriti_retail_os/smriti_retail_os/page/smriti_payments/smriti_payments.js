/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_payments/smriti_payments.js
 * @description: SMRITI Payments / Receipts (Payment Entry) ledger page controller.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.0.0
 * @license: MIT
 */

frappe.pages['smriti-payments'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Payments & Receipts Ledger'),
        single_column: true
    });

    wrapper.controller = new SmritiPaymentsController(wrapper, page);
}

frappe.pages['smriti-payments'].refresh = function(wrapper) {
    var route = frappe.get_route();
    var type = route[1] || 'Receive';
    if (wrapper.controller) {
        wrapper.controller.set_payment_type(type);
    }
}

class SmritiPaymentsController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterPaymentsList = [];
        this.activePaymentDoc = null;
        this.paymentType = 'Receive';

        this.setup_layout();
        this.bind_actions();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-payments-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active" id="topbar-title">${__('Payments / Receipts Ledger')}</span>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-py-search" placeholder="${__('Search by payment no, party or reference...')}">
                    <select class="form-input filter-select" id="smriti-py-filter-status">
                        <option value="">${__('All Statuses')}</option>
                        <option value="Submitted">${__('Submitted')}</option>
                        <option value="Draft">${__('Draft')}</option>
                        <option value="Cancelled">${__('Cancelled')}</option>
                    </select>
                </div>

                <!-- Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Voucher Number')}</th>
                                <th>${__('Posting Date')}</th>
                                <th>${__('Party Type')}</th>
                                <th>${__('Party Name')}</th>
                                <th>${__('Mode of Payment')}</th>
                                <th style="text-align:right;">${__('Amount')}</th>
                                <th style="text-align:center;">${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-payments-tbody">
                            <tr>
                                <td colspan="7" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading payment ledger...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Slide Drawer -->
                <div class="drawer-backdrop" id="smriti-py-drawer-backdrop">
                    <div class="drawer" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="drw-id">${__('Payment Details')}</div>
                            <button class="drawer-close" id="smriti-py-drawer-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <div class="section-card">
                                <div class="section-title">${__('General Summary')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Posting Date')}</span><span class="meta-value" id="drw-date"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Payment Type')}</span><span class="meta-value" id="drw-type"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Party Type')}</span><span class="meta-value" id="drw-party-type"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Party Name')}</span><span class="meta-value" id="drw-party"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Status')}</span><span id="drw-status"></span></div>
                            </div>

                            <div class="section-card">
                                <div class="section-title">${__('Payment Attributes')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Mode of Payment')}</span><span class="meta-value" id="drw-mode"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Reference No')}</span><span class="meta-value" id="drw-ref"></span></div>
                                <div class="meta-row" style="margin-top:10px; flex-direction:column; gap:4px;">
                                    <span class="meta-label">${__('Remarks')}</span>
                                    <p id="drw-remarks" style="font-size:0.85rem; line-height:1.5; color:var(--text-color); background:rgba(0,0,0,0.15); padding:8px; border-radius:4px; border:1px solid var(--border-dark);"></p>
                                </div>
                            </div>

                            <div class="section-card">
                                <div class="section-title">${__('Breakdown')}</div>
                                <div class="meta-row" style="font-size:1.05rem;"><span class="meta-label" style="color:var(--text-color); font-weight:700;">${__('Transaction Amount')}</span><span class="meta-value" id="drw-amount" style="color:var(--success-color); font-weight:800;"></span></div>
                            </div>
                        </div>
                        <div class="drawer-footer">
                            <button class="btn-print" id="btn-print-voucher">
                                <span class="material-symbols-outlined">print</span> ${__('Print Voucher')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#smriti-py-search").on("input", () => me.apply_filters());
        this.wrapper.find("#smriti-py-filter-status").on("change", () => me.apply_filters());

        this.wrapper.find("#smriti-py-drawer-close").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-py-drawer-backdrop").on("click", () => me.close_drawer());
        this.wrapper.find("#btn-print-voucher").on("click", () => me.print_payment());
    }

    set_payment_type(type) {
        this.paymentType = type;
        if (this.paymentType === 'Receive') {
            this.wrapper.find('#topbar-title').text(__('Receipts Voucher Ledger'));
            this.page.set_title(__('SMRITI Receipts Ledger'));
        } else {
            this.wrapper.find('#topbar-title').text(__('Payments Voucher Ledger'));
            this.page.set_title(__('SMRITI Payments Ledger'));
        }
        this.load_payments();
    }

    load_payments() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Payment Entry',
                filters: { payment_type: me.paymentType },
                fields: ['name', 'posting_date', 'payment_type', 'party_type', 'party', 'paid_amount', 'received_amount', 'mode_of_payment', 'reference_no', 'status', 'docstatus'],
                order_by: 'posting_date desc, name desc',
                limit_page_length: 150
            },
            callback: function(r) {
                me.masterPaymentsList = r.message || [];
                me.render_table(me.masterPaymentsList);
            }
        });
    }

    render_table(list) {
        var me = this;
        const tbody = this.wrapper.find('#smriti-payments-tbody');
        tbody.empty();

        if (!list.length) {
            tbody.html(`<tr><td colspan="7" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No vouchers tracked in this ledger.')}</td></tr>`);
            return;
        }

        list.forEach(pe => {
            const statusText = pe.docstatus === 1 ? 'Submitted' : pe.docstatus === 2 ? 'Cancelled' : 'Draft';
            const statusCls = statusText.toLowerCase();
            const amt = me.paymentType === 'Receive' ? pe.received_amount : pe.paid_amount;
            const tr = $(`
                <tr data-id="${pe.name}">
                    <td><span class="invoice-badge">${pe.name}</span></td>
                    <td><div style="font-weight:600;">${pe.posting_date}</div></td>
                    <td><div style="font-size:0.85rem; color:var(--text-muted-color);">${pe.party_type}</div></td>
                    <td style="font-weight:600; color:var(--text-color);">${pe.party}</td>
                    <td><div style="font-size:0.85rem; color:var(--text-muted-color);">${pe.mode_of_payment || '—'}</div></td>
                    <td style="text-align:right; font-weight:700; color:var(--success-color);">Rs. ${parseFloat(amt).toFixed(2)}</td>
                    <td style="text-align:center;">
                        <span class="status-badge ${statusCls}">${statusText}</span>
                    </td>
                </tr>
            `);
            tr.on("click", function() {
                me.load_payment_details($(this).data("id"));
            });
            tbody.append(tr);
        });
    }

    apply_filters() {
        const q = this.wrapper.find('#smriti-py-search').val().toLowerCase();
        const status = this.wrapper.find('#smriti-py-filter-status').val();

        let filtered = this.masterPaymentsList;

        if (q) {
            filtered = filtered.filter(pe => 
                pe.name.toLowerCase().includes(q) ||
                pe.party.toLowerCase().includes(q) ||
                (pe.reference_no && pe.reference_no.toLowerCase().includes(q))
            );
        }
        if (status) {
            filtered = filtered.filter(pe => {
                const statusText = pe.docstatus === 1 ? 'Submitted' : pe.docstatus === 2 ? 'Cancelled' : 'Draft';
                return statusText === status;
            });
        }

        this.render_table(filtered);
    }

    load_payment_details(paymentId) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Payment Entry',
                name: paymentId
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.activePaymentDoc = doc;

                    me.wrapper.find('#drw-id').text(doc.name);
                    me.wrapper.find('#drw-date').text(doc.posting_date);
                    me.wrapper.find('#drw-type').text(doc.payment_type);
                    me.wrapper.find('#drw-party-type').text(doc.party_type);
                    me.wrapper.find('#drw-party').text(doc.party);
                    
                    const statusEl = me.wrapper.find('#drw-status');
                    const statusText = doc.docstatus === 1 ? 'Submitted' : doc.docstatus === 2 ? 'Cancelled' : 'Draft';
                    statusEl.attr('class', `status-badge ${statusText.toLowerCase()}`);
                    statusEl.text(statusText);

                    me.wrapper.find('#drw-mode').text(doc.mode_of_payment || '—');
                    me.wrapper.find('#drw-ref').text(doc.reference_no || '—');
                    me.wrapper.find('#drw-remarks').text(doc.remarks || __('No remarks provided.'));

                    const amt = me.paymentType === 'Receive' ? doc.received_amount : doc.paid_amount;
                    me.wrapper.find('#drw-amount').text(`Rs. ${parseFloat(amt).toFixed(2)}`);
                    me.wrapper.find('#smriti-py-drawer-backdrop').addClass('open');
                }
            }
        });
    }

    print_payment() {
        if (!this.activePaymentDoc) return;
        const url = `/printview?doctype=Payment%20Entry&name=${encodeURIComponent(this.activePaymentDoc.name)}`;
        window.open(url, '_blank');
    }

    close_drawer() {
        this.wrapper.find('#smriti-py-drawer-backdrop').removeClass('open');
        this.activePaymentDoc = null;
    }
}
