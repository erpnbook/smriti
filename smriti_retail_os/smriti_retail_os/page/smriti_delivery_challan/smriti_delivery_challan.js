/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_delivery_challan/smriti_delivery_challan.js
 * @description: SMRITI Delivery Challans Tracker page controller.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.8.6
 * @license: MIT
 */

frappe.pages['smriti-delivery-challan'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Delivery Challans Tracker'),
        single_column: true
    });

    var controller = new SmritiDeliveryChallanController(wrapper, page);
}

class SmritiDeliveryChallanController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterChallansList = [];
        this.activeChallanDoc = null;

        this.setup_layout();
        this.bind_actions();
        this.init();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-delivery-challan-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Delivery Challans Tracker')}</span>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-dc-search" placeholder="${__('Search by challan no or customer name...')}">
                    <select class="form-input filter-select" id="smriti-dc-filter-status">
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
                                <th>${__('Challan Number')}</th>
                                <th>${__('Date & Time')}</th>
                                <th>${__('Customer')}</th>
                                <th style="text-align:right;">${__('Grand Total')}</th>
                                <th style="text-align:center;">${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-challans-tbody">
                            <tr>
                                <td colspan="5" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading Delivery Challans...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Slide Drawer -->
                <div class="drawer-backdrop" id="smriti-dc-drawer-backdrop">
                    <div class="drawer" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="drw-id">${__('Challan Details')}</div>
                            <button class="drawer-close" id="smriti-dc-drawer-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <div class="section-card">
                                <div class="section-title">${__('General Summary')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Date & Time')}</span><span class="meta-value" id="drw-date"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Customer')}</span><span class="meta-value" id="drw-customer"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Status')}</span><span id="drw-status"></span></div>
                            </div>

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

                            <div class="section-card">
                                <div class="section-title">${__('Breakdown')}</div>
                                <div class="meta-row" style="border-top:1px solid var(--border-dark); padding-top:8px; margin-top:8px; font-size:1.05rem;"><span class="meta-label" style="color:var(--text-color); font-weight:700;">${__('Grand Total')}</span><span class="meta-value" id="drw-grand" style="color:var(--success-color); font-weight:800;"></span></div>
                            </div>
                        </div>
                        <div class="drawer-footer">
                            <button class="btn-print" id="btn-print-challan">
                                <span class="material-symbols-outlined">print</span> ${__('Print Delivery Challan')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#smriti-dc-search").on("input", () => me.apply_filters());
        this.wrapper.find("#smriti-dc-filter-status").on("change", () => me.apply_filters());

        this.wrapper.find("#smriti-dc-drawer-close").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-dc-drawer-backdrop").on("click", () => me.close_drawer());
        this.wrapper.find("#btn-print-challan").on("click", () => me.print_challan());
    }

    init() {
        this.load_challans();
    }

    load_challans() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Delivery Note',
                fields: ['name', 'posting_date', 'posting_time', 'customer_name', 'grand_total', 'status', 'docstatus'],
                order_by: 'posting_date desc, posting_time desc',
                limit_page_length: 150
            },
            callback: function(r) {
                me.masterChallansList = r.message || [];
                me.render_table(me.masterChallansList);
            }
        });
    }

    render_table(list) {
        var me = this;
        const tbody = this.wrapper.find('#smriti-challans-tbody');
        tbody.empty();

        if (!list.length) {
            tbody.html(`<tr><td colspan="5" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No Delivery Challans tracked.')}</td></tr>`);
            return;
        }

        list.forEach(ch => {
            const statusText = ch.docstatus === 1 ? 'Submitted' : 'Draft';
            const statusCls = statusText.toLowerCase();
            const tr = $(`
                <tr data-id="${ch.name}">
                    <td><span class="invoice-badge">${ch.name}</span></td>
                    <td>
                        <div style="font-weight:600;">${ch.posting_date}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted-color); margin-top:2px;">${ch.posting_time || ''}</div>
                    </td>
                    <td style="font-weight:600; color:var(--text-color);">${ch.customer_name}</td>
                    <td style="text-align:right; font-weight:700; color:var(--success-color);">Rs. ${parseFloat(ch.grand_total).toFixed(2)}</td>
                    <td style="text-align:center;">
                        <span class="status-badge ${statusCls}">${statusText}</span>
                    </td>
                </tr>
            `);
            tr.on("click", function() {
                me.load_challan_details($(this).data("id"));
            });
            tbody.append(tr);
        });
    }

    apply_filters() {
        const q = this.wrapper.find('#smriti-dc-search').val().toLowerCase();
        const status = this.wrapper.find('#smriti-dc-filter-status').val();

        let filtered = this.masterChallansList;

        if (q) {
            filtered = filtered.filter(ch => 
                ch.name.toLowerCase().includes(q) ||
                ch.customer_name.toLowerCase().includes(q)
            );
        }
        if (status) {
            filtered = filtered.filter(ch => {
                const statusText = ch.docstatus === 1 ? 'Submitted' : 'Draft';
                return statusText === status;
            });
        }

        this.render_table(filtered);
    }

    load_challan_details(challanId) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Delivery Note',
                name: challanId
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.activeChallanDoc = doc;

                    me.wrapper.find('#drw-id').text(doc.name);
                    me.wrapper.find('#drw-date').text(`${doc.posting_date} | ${doc.posting_time || ''}`);
                    me.wrapper.find('#drw-customer').text(doc.customer_name);
                    
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
                    me.wrapper.find('#smriti-dc-drawer-backdrop').addClass('open');
                }
            }
        });
    }

    print_challan() {
        if (!this.activeChallanDoc) return;
        const url = `/printview?doctype=Delivery%20Note&name=${encodeURIComponent(this.activeChallanDoc.name)}`;
        window.open(url, '_blank');
    }

    close_drawer() {
        this.wrapper.find('#smriti-dc-drawer-backdrop').removeClass('open');
        this.activeChallanDoc = null;
    }
}
