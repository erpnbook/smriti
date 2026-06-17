/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_sales_invoices/smriti_sales_invoices.js
 * @description: SMRITI Sales Invoices (Billing Invoices Tracker) page controller.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.0.0
 * @license: MIT
 */

frappe.pages['smriti-sales-invoices'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Billing Invoices Tracker'),
        single_column: true
    });

    var smriti_sales_invoices = new SmritiSalesInvoicesController(wrapper, page);
}

class SmritiSalesInvoicesController {
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
            <div class="smriti-sales-invoices-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Billing Invoices Tracker')}</span>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-inv-search" placeholder="${__('Search by invoice no or customer name...')}">
                    <select class="form-input filter-select" id="smriti-inv-filter-status">
                        <option value="">${__('All Statuses')}</option>
                        <option value="Paid">${__('Paid')}</option>
                        <option value="Unpaid">${__('Unpaid')}</option>
                        <option value="Overdue">${__('Overdue')}</option>
                        <option value="Draft">${__('Draft')}</option>
                    </select>
                </div>

                <!-- Transactions Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Invoice Number')}</th>
                                <th>${__('Date & Time')}</th>
                                <th>${__('Customer')}</th>
                                <th style="text-align:right;">${__('Grand Total')}</th>
                                <th style="text-align:right;">${__('Outstanding')}</th>
                                <th style="text-align:center;">${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-invoices-tbody">
                            <tr>
                                <td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading transactions...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Slide Drawer for Detail View -->
                <div class="drawer-backdrop" id="smriti-inv-drawer-backdrop">
                    <div class="drawer" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="drw-id">${__('Invoice Details')}</div>
                            <button class="drawer-close" id="smriti-inv-drawer-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <!-- Summary card -->
                            <div class="section-card">
                                <div class="section-title">${__('General Summary')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Date & Time')}</span><span class="meta-value" id="drw-date"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Customer')}</span><span class="meta-value" id="drw-customer"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Outstanding')}</span><span class="meta-value" id="drw-outstanding" style="color:var(--danger-color);"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Status')}</span><span id="drw-status"></span></div>
                            </div>

                            <!-- Items card -->
                            <div class="section-card">
                                <div class="section-title">${__('Items Checklist')}</div>
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

                            <!-- Totals card -->
                            <div class="section-card">
                                <div class="section-title">${__('Receipt Breakdown')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Net Amount')}</span><span class="meta-value" id="drw-net"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Taxes (GST)')}</span><span class="meta-value" id="drw-tax"></span></div>
                                <div class="meta-row" style="border-top:1px solid var(--border-dark); padding-top:8px; margin-top:8px; font-size:1.05rem;"><span class="meta-label" style="color:var(--text-color); font-weight:700;">${__('Grand Total')}</span><span class="meta-value" id="drw-grand" style="color:var(--success-color); font-weight:800;"></span></div>
                            </div>

                            <!-- e-Way Bill card -->
                            <div class="section-card" id="drw-eway-card" style="display:none;">
                                <div class="section-title">${__('e-Way Bill Generation')}</div>
                                <div class="meta-row" id="eway-number-row" style="display:none; justify-content:space-between;">
                                    <span class="meta-label">${__('E-way Bill No.')}</span>
                                    <span class="meta-value" id="eway-number-val" style="color:var(--success-color); font-weight:bold;"></span>
                                </div>
                                <div id="eway-form-fields">
                                    <div style="margin-bottom:10px;">
                                        <label style="font-size:0.75rem; color:var(--text-muted-color); display:block; margin-bottom:4px;">${__('Vehicle Number')}</label>
                                        <input type="text" class="form-input" id="eway-vehicle" style="width:100%;" placeholder="e.g. MH-04-GP-1234">
                                    </div>
                                    <div style="margin-bottom:10px;">
                                        <label style="font-size:0.75rem; color:var(--text-muted-color); display:block; margin-bottom:4px;">${__('Distance (in km)')}</label>
                                        <input type="number" class="form-input" id="eway-distance" style="width:100%;" placeholder="e.g. 520">
                                    </div>
                                    <button class="btn-print" id="btn-generate-eway" style="background:var(--accent-color); width:100%; margin-top:8px; border:none; border-radius:4px; font-weight:700; color:var(--bg-dark);">
                                        <span class="material-symbols-outlined" style="vertical-align: middle;">local_shipping</span> ${__('Generate e-Way Bill')}
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="drawer-footer" style="display:flex; flex-direction:column; gap:8px;">
                            <button class="btn-print" id="btn-print-b2b" style="display:none; background:var(--success-color);" >
                                <span class="material-symbols-outlined">receipt_long</span> ${__('Print B2B Invoice')}
                            </button>
                            <button class="btn-print" id="btn-print-pos">
                                <span class="material-symbols-outlined">print</span> ${__('Print POS Receipt')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#smriti-inv-drawer-close").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-inv-drawer-backdrop").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-inv-search").on("input", () => me.apply_filters());
        this.wrapper.find("#smriti-inv-filter-status").on("change", () => me.apply_filters());
        this.wrapper.find("#btn-print-b2b").on("click", () => me.print_b2b_invoice());
        this.wrapper.find("#btn-print-pos").on("click", () => me.print_receipt());
        this.wrapper.find("#btn-generate-eway").on("click", () => me.generate_eway_bill());
    }

    init() {
        this.load_invoices();
    }

    load_invoices() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Sales Invoice',
                filters: { is_return: 0 },
                fields: ['name', 'posting_date', 'posting_time', 'customer_name', 'grand_total', 'outstanding_amount', 'status'],
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
            tbody.html(`<tr><td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No invoices tracked.')}</td></tr>`);
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
                    <td style="font-weight:600; color:var(--text-color);">${inv.customer_name}</td>
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
        const q = this.wrapper.find('#smriti-inv-search').val().toLowerCase();
        const status = this.wrapper.find('#smriti-inv-filter-status').val();

        let filtered = this.masterInvoicesList;

        if (q) {
            filtered = filtered.filter(inv => 
                inv.name.toLowerCase().includes(q) ||
                inv.customer_name.toLowerCase().includes(q)
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
                doctype: 'Sales Invoice',
                name: invoiceId
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.activeInvoiceDoc = doc;

                    me.wrapper.find('#drw-id').text(doc.name);
                    me.wrapper.find('#drw-date').text(`${doc.posting_date} | ${doc.posting_time || ''}`);
                    me.wrapper.find('#drw-customer').text(doc.customer_name);
                    me.wrapper.find('#drw-outstanding').text(`Rs. ${parseFloat(doc.outstanding_amount).toFixed(2)}`);
                    
                    const statusEl = me.wrapper.find('#drw-status');
                    statusEl.attr('class', `status-badge ${doc.status.toLowerCase()}`);
                    statusEl.text(doc.status);

                    // Render Items table
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

                    me.wrapper.find('#drw-net').text(`Rs. ${parseFloat(doc.net_total).toFixed(2)}`);
                    me.wrapper.find('#drw-tax').text(`Rs. ${parseFloat(doc.total_taxes_and_charges || 0).toFixed(2)}`);
                    me.wrapper.find('#drw-grand').text(`Rs. ${parseFloat(doc.grand_total).toFixed(2)}`);

                    // e-Way Bill UI handler
                    const ewayCard = me.wrapper.find('#drw-eway-card');
                    if (parseFloat(doc.grand_total) >= 50000) {
                        ewayCard.show();
                        if (doc.ewaybill) {
                            me.wrapper.find('#eway-number-row').css('display', 'flex');
                            me.wrapper.find('#eway-number-val').text(doc.ewaybill);
                            me.wrapper.find('#eway-form-fields').hide();
                        } else {
                            me.wrapper.find('#eway-number-row').hide();
                            me.wrapper.find('#eway-form-fields').show();
                            me.wrapper.find('#eway-vehicle').val('');
                            me.wrapper.find('#eway-distance').val('');
                        }
                    } else {
                        ewayCard.hide();
                    }

                    // B2B print button
                    const isB2B = doc.custom_sizewise_json || (doc.remarks && doc.remarks.includes('_sizewise_matrix'));
                    me.wrapper.find('#btn-print-b2b').css('display', isB2B ? 'flex' : 'none');

                    me.wrapper.find('#smriti-inv-drawer-backdrop').addClass('open');
                }
            }
        });
    }

    close_drawer() {
        this.wrapper.find('#smriti-inv-drawer-backdrop').removeClass('open');
        this.activeInvoiceDoc = null;
    }

    print_b2b_invoice() {
        if (!this.activeInvoiceDoc) return;
        window.open(`/sizewise_invoice?invoice=${this.activeInvoiceDoc.name}`, '_blank');
    }

    print_receipt() {
        if (!this.activeInvoiceDoc) return;
        const printUrl = `/printview?doctype=Sales%20Invoice&name=${encodeURIComponent(this.activeInvoiceDoc.name)}`;
        window.open(printUrl, '_blank');
    }

    generate_eway_bill() {
        var me = this;
        if (!this.activeInvoiceDoc) return;
        const vehicle = this.wrapper.find('#eway-vehicle').val().trim();
        const distance = this.wrapper.find('#eway-distance').val().trim();
        
        if (!vehicle) {
            frappe.show_alert({message: __('Vehicle Number is required!'), indicator: 'red'});
            return;
        }

        frappe.call({
            method: 'smriti_retail_os.billing_api.generate_mock_eway_bill',
            args: {
                invoice_name: this.activeInvoiceDoc.name,
                vehicle_no: vehicle,
                distance: distance
            },
            freeze: true,
            freeze_message: __('Connecting to GST e-Way Bill System...'),
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({message: __('E-way Bill generated successfully!'), indicator: 'green'});
                    me.load_invoice_details(me.activeInvoiceDoc.name);
                    me.load_invoices();
                }
            }
        });
    }
}
