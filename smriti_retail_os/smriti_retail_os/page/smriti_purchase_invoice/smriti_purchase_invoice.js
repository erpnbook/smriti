/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_purchase_invoice/smriti_purchase_invoice.js
 * @description: SMRITI Purchase Invoices Tracker page controller.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.8.6
 * @license: MIT
 */

frappe.pages['smriti-purchase-invoice'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Purchase Invoices Tracker'),
        single_column: true
    });

    var controller = new SmritiPurchaseInvoiceController(wrapper, page);
}

class SmritiPurchaseInvoiceController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterInvoicesList = [];
        this.activeInvoiceDoc = null;

        this.setup_layout();
        this.bind_actions();
        this.init();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-purchase-invoice-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Purchase Invoices Tracker')}</span>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-pi-search" placeholder="${__('Search by invoice no or supplier name...')}">
                    <select class="form-input filter-select" id="smriti-pi-filter-status">
                        <option value="">${__('All Statuses')}</option>
                        <option value="Paid">${__('Paid')}</option>
                        <option value="Unpaid">${__('Unpaid')}</option>
                        <option value="Overdue">${__('Overdue')}</option>
                        <option value="Draft">${__('Draft')}</option>
                    </select>
                </div>

                <!-- Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Invoice Number')}</th>
                                <th>${__('Date & Time')}</th>
                                <th>${__('Supplier')}</th>
                                <th style="text-align:right;">${__('Grand Total')}</th>
                                <th style="text-align:right;">${__('Outstanding')}</th>
                                <th style="text-align:center;">${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-invoices-tbody">
                            <tr>
                                <td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading Purchase Invoices...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Slide Drawer -->
                <div class="drawer-backdrop" id="smriti-pi-drawer-backdrop">
                    <div class="drawer" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="drw-id">${__('Purchase Invoice Details')}</div>
                            <button class="drawer-close" id="smriti-pi-drawer-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <div class="section-card">
                                <div class="section-title">${__('General Summary')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Date & Time')}</span><span class="meta-value" id="drw-date"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Supplier')}</span><span class="meta-value" id="drw-supplier"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Outstanding')}</span><span class="meta-value" id="drw-outstanding" style="color:var(--danger-color);"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Status')}</span><span id="drw-status"></span></div>
                            </div>

                            <div class="section-card">
                                <div class="section-title">${__('Invoice Items')}</div>
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
                            <button class="btn-print" id="btn-print-invoice">
                                <span class="material-symbols-outlined">print</span> ${__('Print Invoice')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#smriti-pi-search").on("input", () => me.apply_filters());
        this.wrapper.find("#smriti-pi-filter-status").on("change", () => me.apply_filters());

        this.wrapper.find("#smriti-pi-drawer-close").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-pi-drawer-backdrop").on("click", () => me.close_drawer());
        this.wrapper.find("#btn-print-invoice").on("click", () => me.print_invoice());
    }

    init() {
        this.load_invoices();
    }

    load_invoices() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Purchase Invoice',
                fields: ['name', 'posting_date', 'posting_time', 'supplier_name', 'grand_total', 'outstanding_amount', 'status'],
                order_by: 'posting_date desc, posting_time desc',
                limit_page_length: 150
            },
            callback: function(r) {
                me.masterInvoicesList = r.message || [];
                me.render_table(me.masterInvoicesList);
            }
        });
    }

    render_table(list) {
        var me = this;
        const tbody = this.wrapper.find('#smriti-invoices-tbody');
        tbody.empty();

        if (!list.length) {
            tbody.html(`<tr><td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No Purchase Invoices tracked.')}</td></tr>`);
            return;
        }

        list.forEach(inv => {
            const statusCls = inv.status.toLowerCase();
            const tr = $(`
                <tr data-id="${inv.name}">
                    <td><span class="invoice-badge">${inv.name}</span></td>
                    <td>
                        <div style="font-weight:600;">${inv.posting_date}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted-color); margin-top:2px;">${inv.posting_time || ''}</div>
                    </td>
                    <td style="font-weight:600; color:var(--text-color);">${inv.supplier_name}</td>
                    <td style="text-align:right; font-weight:700; color:var(--success-color);">Rs. ${parseFloat(inv.grand_total).toFixed(2)}</td>
                    <td style="text-align:right; font-weight:600; color:${parseFloat(inv.outstanding_amount) > 0 ? 'var(--danger-color)' : 'var(--text-muted-color)'};">Rs. ${parseFloat(inv.outstanding_amount).toFixed(2)}</td>
                    <td style="text-align:center;">
                        <span class="status-badge ${statusCls}">${inv.status}</span>
                    </td>
                </tr>
            `);
            tr.on("click", function() {
                me.load_invoice_details($(this).data("id"));
            });
            tbody.append(tr);
        });
    }

    apply_filters() {
        const q = this.wrapper.find('#smriti-pi-search').val().toLowerCase();
        const status = this.wrapper.find('#smriti-pi-filter-status').val();

        let filtered = this.masterInvoicesList;

        if (q) {
            filtered = filtered.filter(inv => 
                inv.name.toLowerCase().includes(q) ||
                inv.supplier_name.toLowerCase().includes(q)
            );
        }
        if (status) {
            filtered = filtered.filter(inv => inv.status === status);
        }

        this.render_table(filtered);
    }

    load_invoice_details(invoiceId) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Purchase Invoice',
                name: invoiceId
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.activeInvoiceDoc = doc;

                    me.wrapper.find('#drw-id').text(doc.name);
                    me.wrapper.find('#drw-date').text(`${doc.posting_date} | ${doc.posting_time || ''}`);
                    me.wrapper.find('#drw-supplier').text(doc.supplier_name);
                    me.wrapper.find('#drw-outstanding').text(`Rs. ${parseFloat(doc.outstanding_amount).toFixed(2)}`);
                    
                    const statusEl = me.wrapper.find('#drw-status');
                    statusEl.attr('class', `status-badge ${doc.status.toLowerCase()}`);
                    statusEl.text(doc.status);

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
                    me.wrapper.find('#smriti-pi-drawer-backdrop').addClass('open');
                }
            }
        });
    }

    print_invoice() {
        if (!this.activeInvoiceDoc) return;
        const url = `/printview?doctype=Purchase%20Invoice&name=${encodeURIComponent(this.activeInvoiceDoc.name)}`;
        window.open(url, '_blank');
    }

    close_drawer() {
        this.wrapper.find('#smriti-pi-drawer-backdrop').removeClass('open');
        this.activeInvoiceDoc = null;
    }
}
