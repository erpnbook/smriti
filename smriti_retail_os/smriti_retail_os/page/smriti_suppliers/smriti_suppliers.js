/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_suppliers/smriti_suppliers.js
 * @description: Page controller for SMRITI Supplier Registry (Desk SPA).
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.0.0
 * @license: MIT
 */

frappe.pages['smriti-suppliers'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Supplier Registry'),
        single_column: true
    });

    var smriti_suppliers = new SmritiSuppliersController(wrapper, page);
}

class SmritiSuppliersController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterSuppliersList = [];

        this.GST_STATE_CODES = {
            "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
            "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
            "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh", "13": "Nagaland", "14": "Manipur",
            "15": "Mizoram", "16": "Tripura", "17": "Meghalaya", "18": "Assam", "19": "West Bengal",
            "20": "Jharkhand", "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
            "26": "Dadra and Nagar Haveli and Daman and Diu", "27": "Maharashtra", "29": "Karnataka",
            "30": "Goa", "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
            "35": "Andaman & Nicobar Islands", "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
            "97": "Other Territory"
        };

        this.setup_layout();
        this.bind_actions();
        this.init();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-suppliers-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Supplier Registry')}</span>
                    </div>

                    <div class="topbar-right">
                        <button class="topbtn" id="smriti-supp-btn-add" style="border-color: var(--primary-color); color: var(--primary-lt-color);">
                            <span class="material-symbols-outlined">add_business</span> ${__('Quick Add Supplier')}
                        </button>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-supp-search" placeholder="${__('Search by supplier name or code...')}">
                    <select class="form-input filter-select" id="smriti-supp-filter-group">
                        <option value="">${__('All Groups')}</option>
                    </select>
                </div>

                <!-- Directory Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Supplier Details')}</th>
                                <th>${__('Mobile Number')}</th>
                                <th>${__('Supplier Group')}</th>
                                <th>${__('Credit Days')}</th>
                                <th>${__('System Identifier')}</th>
                                <th style="text-align:right;">${__('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-suppliers-tbody">
                            <tr>
                                <td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading suppliers...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Supplier Form Modal -->
                <div class="modal-backdrop" id="smriti-supplier-modal">
                    <div class="modal" onclick="event.stopPropagation()">
                        <div class="modal-header">
                            <div class="modal-title">
                                <span class="material-symbols-outlined">add_business</span> 
                                <span id="smriti-modal-action-title">${__('Quick Add Supplier')}</span>
                            </div>
                            <button class="modal-close" id="smriti-supp-modal-close">&times;</button>
                        </div>
                        <div class="modal-body" style="max-height: 75vh; overflow-y: auto; padding-right: 6px;">
                            <input type="hidden" id="supp-name-id" value="">
                            
                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--primary-lt-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:6px;">
                                <span class="material-symbols-outlined" style="font-size:16px;">contact_page</span> 1. General Profile (Basic Details)
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                                <div class="form-group">
                                    <label class="form-label">${__('Naming Series')}</label>
                                    <select class="form-input" id="supp-naming-series"></select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Supplier Name *')}</label>
                                    <input type="text" class="form-input" id="supp-name" placeholder="e.g. Acme Footwears Ltd">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Supplier Type')}</label>
                                    <select class="form-input" id="supp-type">
                                        <option value="Individual">${__('Individual')}</option>
                                        <option value="Company" selected>${__('Company')}</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Contact Person')}</label>
                                    <input type="text" class="form-input" id="supp-contact-person" placeholder="e.g. John Doe">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Status')}</label>
                                    <select class="form-input" id="supp-status">
                                        <option value="Active" selected>${__('Active')}</option>
                                        <option value="Disabled">${__('Disabled')}</option>
                                        <option value="On Hold">${__('On Hold')}</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Mobile Number')}</label>
                                    <input type="text" class="form-input" id="supp-mobile" placeholder="e.g. 9876543210">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Email Address')}</label>
                                    <input type="email" class="form-input" id="supp-email" placeholder="e.g. sales@acme.com">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('GSTIN')}</label>
                                    <input type="text" class="form-input" id="supp-gstin" placeholder="e.g. 29AABCR1718E1ZL">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('GST Category')}</label>
                                    <select class="form-input" id="supp-gst-category">
                                        <option value="Unregistered">${__('Unregistered')}</option>
                                        <option value="Registered Regular" selected>${__('Registered Regular')}</option>
                                        <option value="Composition">${__('Composition')}</option>
                                        <option value="Overseas">${__('Overseas')}</option>
                                        <option value="SEZ">${__('SEZ')}</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('PAN (Tax ID)')}</label>
                                    <input type="text" class="form-input" id="supp-pan" placeholder="e.g. ABCDE1234F">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Vendor Code')}</label>
                                    <input type="text" class="form-input" id="supp-vendor-code" placeholder="e.g. VND-ACME">
                                </div>
                            </div>

                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--primary-lt-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:6px;">
                                <span class="material-symbols-outlined" style="font-size:16px;">home</span> 2. Address Details (Bill To)
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                                <div class="form-group" style="grid-column: span 2;">
                                    <label class="form-label">${__('Address Line 1')}</label>
                                    <input type="text" class="form-input" id="bill-line1" placeholder="e.g. Shed 4B, Peenya Industrial Area">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Address Line 2 (Optional)')}</label>
                                    <input type="text" class="form-input" id="bill-line2" placeholder="e.g. Phase 2">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('City')}</label>
                                    <input type="text" class="form-input" id="bill-city" placeholder="e.g. Bangalore">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('State')}</label>
                                    <input type="text" class="form-input" id="bill-state" placeholder="e.g. Karnataka">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Pincode')}</label>
                                    <input type="text" class="form-input" id="bill-pincode" placeholder="e.g. 560058">
                                </div>
                            </div>

                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--primary-lt-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 12px; display:flex; align-items:center; justify-content:space-between;">
                                <span style="display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:16px;">local_shipping</span> 3. Shipping Address Details (Ship To)
                                </span>
                                <label style="font-size: 0.72rem; display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
                                    <input type="checkbox" id="same-as-billing" style="accent-color:var(--primary-color);"> ${__('Same as Billing')}
                                </label>
                            </div>
                            <div id="shipping-address-section" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px;">
                                <div class="form-group" style="grid-column: span 2;">
                                    <label class="form-label">${__('Address Line 1')}</label>
                                    <input type="text" class="form-input" id="ship-line1" placeholder="e.g. Shed 4B, Peenya Industrial Area">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Address Line 2 (Optional)')}</label>
                                    <input type="text" class="form-input" id="ship-line2" placeholder="e.g. Phase 2">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('City')}</label>
                                    <input type="text" class="form-input" id="ship-city" placeholder="e.g. Bangalore">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('State')}</label>
                                    <input type="text" class="form-input" id="ship-state" placeholder="e.g. Karnataka">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Pincode')}</label>
                                    <input type="text" class="form-input" id="ship-pincode" placeholder="e.g. 560058">
                                </div>
                            </div>

                            <!-- Advanced Details Toggle -->
                            <div class="advanced-toggle" id="smriti-supp-adv-toggle" style="font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: var(--primary-lt-color); border-top: 1px solid var(--border-dark); border-bottom: 1px solid var(--border-dark); padding: 12px 0; margin: 20px 0 12px 0; display:flex; align-items:center; justify-content:space-between; cursor:pointer; user-select:none;">
                                <span style="display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:18px;">settings_applications</span> ${__('Advanced Details (Optional)')}
                                </span>
                                <span class="material-symbols-outlined" id="advanced-chevron">expand_more</span>
                            </div>

                            <!-- Advanced Section -->
                            <div id="advanced-section" style="display: none; flex-direction: column; gap: 14px;">
                                <!-- Section 1: Pricing & Defaults -->
                                <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--accent-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 8px; display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:16px;">account_balance</span> 1. Pricing & Defaults
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                                    <div class="form-group">
                                        <label class="form-label">${__('Supplier Group')}</label>
                                        <select class="form-input" id="supp-group"></select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">${__('Credit Days')}</label>
                                        <input type="number" class="form-input" id="supp-credit-days" placeholder="e.g. 30" value="0">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">${__('Payment Terms Template')}</label>
                                        <select class="form-input" id="supp-payment-terms">
                                            <option value="">${__('No Template')}</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">${__('Default Currency')}</label>
                                        <select class="form-input" id="supp-currency">
                                            <option value="">${__('Default (INR)')}</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">${__('Default Price List')}</label>
                                        <select class="form-input" id="supp-price-list">
                                            <option value="">${__('Default (Standard Buying)')}</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">${__('Company Bank Account')}</label>
                                        <select class="form-input" id="supp-bank-account">
                                            <option value="">${__('Select Bank Account')}</option>
                                        </select>
                                    </div>
                                </div>

                                <!-- Section 2: Internal & Logistics -->
                                <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--accent-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 8px; display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:16px;">local_shipping</span> 2. Internal & Logistics Settings
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; align-items: center;">
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-is-internal-supplier" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Is Internal Supplier')}
                                    </label>
                                    <div class="form-group" id="represents-company-group" style="display: none;">
                                        <label class="form-label">${__('Represents Company')}</label>
                                        <select class="form-input" id="supp-represents-company">
                                            <option value="">${__('Select Company')}</option>
                                        </select>
                                    </div>
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem; grid-column: 1;">
                                        <input type="checkbox" id="supp-is-transporter" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Is Transporter')}
                                    </label>
                                </div>

                                <!-- Section 3: Compliance & Hold Settings -->
                                <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--accent-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 8px; display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:16px;">gavel</span> 3. Purchase Controls & Holds
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-allow-invoice-no-po" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Allow Invoice without PO')}
                                    </label>
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-allow-invoice-no-receipt" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Allow Invoice without Receipt')}
                                    </label>
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-is-frozen" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Is Frozen')}
                                    </label>
                                    
                                    <div class="form-group" style="grid-column: 1 / span 2; display: none; grid-template-columns: 1fr 1fr; gap: 12px;" id="hold-settings-group">
                                        <div class="form-group">
                                            <label class="form-label">${__('Hold Type')}</label>
                                            <select class="form-input" id="supp-hold-type">
                                                <option value="All">${__('All')}</option>
                                                <option value="Invoices">${__('Invoices')}</option>
                                                <option value="Payments">${__('Payments')}</option>
                                            </select>
                                        </div>
                                        <div class="form-group">
                                            <label class="form-label">${__('Release Date')}</label>
                                            <input type="date" class="form-input" id="supp-release-date">
                                        </div>
                                    </div>
                                </div>

                                <!-- Section 4: Warning Settings -->
                                <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--accent-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 8px; display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:16px;">report_problem</span> 4. Warnings & Prevent Rules
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-warn-rfqs" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Warn RFQs')}
                                    </label>
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-prevent-rfqs" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Prevent RFQs')}
                                    </label>
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-warn-pos" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Warn POs')}
                                    </label>
                                    <label style="display: inline-flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.85rem;">
                                        <input type="checkbox" id="supp-prevent-pos" style="accent-color:var(--primary-color); width:16px; height:16px;"> ${__('Prevent POs')}
                                    </label>
                                </div>

                                <!-- Section 5: Metadata & Descriptions -->
                                <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--accent-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 8px; display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:16px;">info</span> 5. Extra Metadata
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                                    <div class="form-group">
                                        <label class="form-label">${__('Website')}</label>
                                        <input type="text" class="form-input" id="supp-website" placeholder="e.g. www.acme.com">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">${__('Language')}</label>
                                        <select class="form-input" id="supp-language">
                                            <option value="">${__('Default (English)')}</option>
                                        </select>
                                    </div>
                                    <div class="form-group" style="grid-column: span 2;">
                                        <label class="form-label">${__('Supplier Details / Description')}</label>
                                        <textarea class="form-input" id="supp-details" rows="3" placeholder="Enter supplier profile description..."></textarea>
                                    </div>
                                </div>
                            </div>

                            <button class="btn-submit" id="btn-save" style="margin-top: 15px;">
                                <span class="material-symbols-outlined">save</span> ${__('Save Supplier Record')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#smriti-supp-btn-add").on("click", () => me.open_add_supplier_modal());
        this.wrapper.find("#smriti-supp-modal-close").on("click", () => me.close_supplier_modal());
        this.wrapper.find("#smriti-supplier-modal").on("click", () => me.close_supplier_modal());
        
        this.wrapper.find("#smriti-supp-search").on("input", function() {
            me.apply_filters();
        });

        this.wrapper.find("#smriti-supp-filter-group").on("change", function() {
            me.apply_filters();
        });

        this.wrapper.find("#same-as-billing").on("change", function() {
            me.toggle_same_as_billing($(this).is(":checked"));
        });

        this.wrapper.find("#supp-gstin").on("change", function() {
            me.auto_resolve_state($(this).val(), 'bill');
        });

        this.wrapper.find("#smriti-supp-adv-toggle").on("click", () => me.toggle_advanced_details());
        this.wrapper.find("#supp-is-internal-supplier").on("change", function() {
            me.toggle_internal_supplier($(this).is(":checked"));
        });
        this.wrapper.find("#supp-status").on("change", function() {
            me.handle_status_change($(this).val());
        });

        this.wrapper.find("#btn-save").on("click", () => me.save_supplier_detail());
    }

    init() {
        this.load_suppliers();
        this.load_filter_options();
        this.load_dropdown_options();
    }

    load_suppliers() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Supplier',
                fields: ['name', 'supplier_name', 'supplier_group', 'mobile_no', 'custom_credit_days', 'custom_vendor_code'],
                order_by: 'creation desc',
                limit_page_length: 200
            },
            callback: function(r) {
                me.masterSuppliersList = r.message || [];
                me.render_table(me.masterSuppliersList);
            }
        });
    }

    load_filter_options() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Supplier Group',
                fields: ['name'],
                order_by: 'name asc',
                limit_page_length: 100
            },
            callback: function(r) {
                const grpSel = me.wrapper.find('#smriti-supp-filter-group');
                grpSel.html(`<option value="">${__('All Groups')}</option>`);
                if (r.message) {
                    r.message.forEach(g => {
                        grpSel.append(`<option value="${g.name}">${g.name}</option>`);
                    });
                }
            }
        });
    }

    load_dropdown_options() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Supplier Group',
                fields: ['name'],
                order_by: 'name asc',
                limit_page_length: 100
            },
            callback: function(r) {
                const grpSel = me.wrapper.find('#supp-group');
                grpSel.empty();
                if (r.message) {
                    r.message.forEach(g => {
                        grpSel.append(`<option value="${g.name}">${g.name}</option>`);
                    });
                }
            }
        });

        // Load Naming Series options
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'DocField',
                filters: { parent: 'Supplier', fieldname: 'naming_series' },
                fieldname: 'options'
            },
            callback: function(r) {
                let seriesOptions = ['SUP-.YYYY.-'];
                if (r.message && r.message.options) {
                    seriesOptions = r.message.options.split('\n').map(x => x.trim()).filter(x => x);
                }
                const seriesSel = me.wrapper.find('#supp-naming-series');
                seriesSel.empty();
                seriesOptions.forEach(optVal => {
                    seriesSel.append(`<option value="${optVal}">${optVal}</option>`);
                });
            }
        });

        // Load Payment Terms Templates
        frappe.call({
            method: 'frappe.client.get_list',
            args: { doctype: 'Payment Terms Template', fields: ['name'], limit_page_length: 100 },
            callback: function(r) {
                const termSel = me.wrapper.find('#supp-payment-terms');
                termSel.html(`<option value="">${__('No Template')}</option>`);
                if (r.message) {
                    r.message.forEach(t => {
                        termSel.append(`<option value="${t.name}">${t.name}</option>`);
                    });
                }
            }
        });

        // Load Currencies
        frappe.call({
            method: 'frappe.client.get_list',
            args: { doctype: 'Currency', fields: ['name'], filters: { enabled: 1 }, limit_page_length: 250 },
            callback: function(r) {
                const currSel = me.wrapper.find('#supp-currency');
                currSel.html(`<option value="">${__('Default (INR)')}</option>`);
                if (r.message) {
                    r.message.forEach(c => {
                        currSel.append(`<option value="${c.name}">${c.name}</option>`);
                    });
                }
            }
        });

        // Load Price Lists
        frappe.call({
            method: 'frappe.client.get_list',
            args: { doctype: 'Price List', fields: ['name'], filters: { buying: 1, enabled: 1 }, limit_page_length: 100 },
            callback: function(r) {
                const plSel = me.wrapper.find('#supp-price-list');
                plSel.html(`<option value="">${__('Default (Standard Buying)')}</option>`);
                if (r.message) {
                    r.message.forEach(pl => {
                        plSel.append(`<option value="${pl.name}">${pl.name}</option>`);
                    });
                }
            }
        });

        // Load Bank Accounts
        frappe.call({
            method: 'frappe.client.get_list',
            args: { doctype: 'Bank Account', fields: ['name'], limit_page_length: 100 },
            callback: function(r) {
                const bankSel = me.wrapper.find('#supp-bank-account');
                bankSel.html(`<option value="">${__('Select Bank Account')}</option>`);
                if (r.message) {
                    r.message.forEach(ba => {
                        bankSel.append(`<option value="${ba.name}">${ba.name}</option>`);
                    });
                }
            }
        });

        // Load Companies
        frappe.call({
            method: 'frappe.client.get_list',
            args: { doctype: 'Company', fields: ['name'], limit_page_length: 50 },
            callback: function(r) {
                const compSel = me.wrapper.find('#supp-represents-company');
                compSel.html(`<option value="">${__('Select Company')}</option>`);
                if (r.message) {
                    r.message.forEach(co => {
                        compSel.append(`<option value="${co.name}">${co.name}</option>`);
                    });
                }
            }
        });

        // Load Languages
        frappe.call({
            method: 'frappe.client.get_list',
            args: { doctype: 'Language', fields: ['name'], filters: { enabled: 1 }, limit_page_length: 200 },
            callback: function(r) {
                const langSel = me.wrapper.find('#supp-language');
                langSel.html(`<option value="">${__('Default (English)')}</option>`);
                if (r.message) {
                    r.message.forEach(l => {
                        langSel.append(`<option value="${l.name}">${l.name}</option>`);
                    });
                }
            }
        });
    }

    render_table(list) {
        var me = this;
        const tbody = this.wrapper.find('#smriti-suppliers-tbody');
        tbody.empty();

        if (!list.length) {
            tbody.html(`<tr><td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No suppliers found.')}</td></tr>`);
            return;
        }

        list.forEach(s => {
            const tr = $(`
                <tr>
                    <td>
                        <div style="font-weight:600; color:var(--text-color);">${s.supplier_name}</div>
                        <div style="font-size:0.75rem; color:var(--accent-color); font-weight:500; margin-top:2px;">Vendor Code: ${s.custom_vendor_code || 'DV'}</div>
                    </td>
                    <td style="font-weight:600; color:var(--primary-lt-color);">${s.mobile_no || 'N/A'}</td>
                    <td style="color:var(--text-muted-color);">${s.supplier_group}</td>
                    <td><span class="credit-badge">${s.custom_credit_days || 0} Days</span></td>
                    <td><span class="supplier-id-badge">${s.name}</span></td>
                    <td style="text-align:right;">
                        <button class="topbtn btn-edit-supplier" data-id="${s.name}" title="${__('Edit Supplier Details')}" style="padding:4px 8px;">
                            <span class="material-symbols-outlined" style="font-size:16px;">edit</span>
                        </button>
                    </td>
                </tr>
            `);
            tr.find(".btn-edit-supplier").on("click", function() {
                me.open_edit_supplier_modal($(this).data("id"));
            });
            tbody.append(tr);
        });
    }

    apply_filters() {
        const q = this.wrapper.find('#smriti-supp-search').val().toLowerCase();
        const grp = this.wrapper.find('#smriti-supp-filter-group').val();

        let filtered = this.masterSuppliersList;

        if (q) {
            filtered = filtered.filter(s => 
                s.supplier_name.toLowerCase().includes(q) ||
                s.name.toLowerCase().includes(q) ||
                (s.custom_vendor_code || '').toLowerCase().includes(q) ||
                (s.mobile_no || '').includes(q)
            );
        }
        if (grp) {
            filtered = filtered.filter(s => s.supplier_group === grp);
        }

        this.render_table(filtered);
    }

    toggle_advanced_details() {
        const section = this.wrapper.find('#advanced-section');
        const chevron = this.wrapper.find('#advanced-chevron');
        if (section.css('display') === 'none') {
            section.css('display', 'flex');
            chevron.text('expand_less');
        } else {
            section.css('display', 'none');
            chevron.text('expand_more');
        }
    }

    toggle_internal_supplier(checked) {
        const group = this.wrapper.find('#represents-company-group');
        if (checked) {
            group.css('display', 'flex');
        } else {
            group.css('display', 'none');
            this.wrapper.find('#supp-represents-company').val("");
        }
    }

    handle_status_change(status) {
        const holdGroup = this.wrapper.find('#hold-settings-group');
        if (status === 'On Hold') {
            holdGroup.css('display', 'grid');
        } else {
            holdGroup.css('display', 'none');
            this.wrapper.find('#supp-hold-type').val("All");
            this.wrapper.find('#supp-release-date').val("");
        }
    }

    open_add_supplier_modal() {
        this.wrapper.find('#smriti-modal-action-title').text(__('Quick Add Supplier'));
        this.wrapper.find('#supp-name-id').val("");
        this.wrapper.find('#supp-name').val("");
        this.wrapper.find('#supp-type').val("Company");
        this.wrapper.find('#supp-contact-person').val("");
        this.wrapper.find('#supp-status').val("Active");
        this.handle_status_change("Active");
        this.wrapper.find('#supp-mobile').val("");
        this.wrapper.find('#supp-email').val("");
        this.wrapper.find('#supp-gstin').val("");
        this.wrapper.find('#supp-gst-category').val("Registered Regular");
        this.wrapper.find('#supp-pan').val("");
        this.wrapper.find('#supp-vendor-code').val("");

        // Clear Address
        this.wrapper.find('#bill-line1').val("");
        this.wrapper.find('#bill-line2').val("");
        this.wrapper.find('#bill-city').val("");
        this.wrapper.find('#bill-state').val("");
        this.wrapper.find('#bill-pincode').val("");
        
        this.wrapper.find('#same-as-billing').prop('checked', false);
        this.toggle_same_as_billing(false);
        
        this.wrapper.find('#ship-line1').val("");
        this.wrapper.find('#ship-line2').val("");
        this.wrapper.find('#ship-city').val("");
        this.wrapper.find('#ship-state').val("");
        this.wrapper.find('#ship-pincode').val("");

        // Clear Advanced
        this.wrapper.find('#supp-group').val("Local");
        this.wrapper.find('#supp-credit-days').val("0");
        this.wrapper.find('#supp-payment-terms').val("");
        this.wrapper.find('#supp-currency').val("");
        this.wrapper.find('#supp-price-list').val("");
        this.wrapper.find('#supp-bank-account').val("");
        this.wrapper.find('#supp-is-internal-supplier').prop('checked', false);
        this.toggle_internal_supplier(false);
        this.wrapper.find('#supp-is-transporter').prop('checked', false);
        this.wrapper.find('#supp-allow-invoice-no-po').prop('checked', false);
        this.wrapper.find('#supp-allow-invoice-no-receipt').prop('checked', false);
        this.wrapper.find('#supp-is-frozen').prop('checked', false);
        this.wrapper.find('#supp-warn-rfqs').prop('checked', false);
        this.wrapper.find('#supp-prevent-rfqs').prop('checked', false);
        this.wrapper.find('#supp-warn-pos').prop('checked', false);
        this.wrapper.find('#supp-prevent-pos').prop('checked', false);
        this.wrapper.find('#supp-website').val("");
        this.wrapper.find('#supp-language').val("");
        this.wrapper.find('#supp-details').val("");

        this.wrapper.find('#smriti-supplier-modal').addClass('open');
        this.wrapper.find('#supp-name').focus();
    }

    open_edit_supplier_modal(name) {
        var me = this;
        frappe.show_alert({message: __('Fetching supplier details...'), indicator: 'blue'});
        
        frappe.call({
            method: 'smriti_retail_os.master_api.get_supplier_detail',
            args: { name: name },
            callback: function(r) {
                if (r.message) {
                    const s = r.message;
                    me.wrapper.find('#smriti-modal-action-title').text(__('Edit Supplier: ') + s.supplier_name);
                    me.wrapper.find('#supp-name-id').val(s.name);
                    me.wrapper.find('#supp-naming-series').val(s.naming_series);
                    me.wrapper.find('#supp-name').val(s.supplier_name);
                    me.wrapper.find('#supp-type').val(s.supplier_type || "Company");
                    me.wrapper.find('#supp-contact-person').val(s.contact_person || "");
                    me.wrapper.find('#supp-status').val(s.status || "Active");
                    me.handle_status_change(s.status || "Active");
                    me.wrapper.find('#supp-mobile').val(s.mobile_no || "");
                    me.wrapper.find('#supp-email').val(s.email_id || "");
                    me.wrapper.find('#supp-gstin').val(s.gstin || "");
                    me.wrapper.find('#supp-gst-category').val(s.gst_category || "Registered Regular");
                    me.wrapper.find('#supp-pan').val(s.pan || "");
                    me.wrapper.find('#supp-vendor-code').val(s.custom_vendor_code || "");

                    // Parse Billing Address Text
                    const billLines = (s.custom_address_text || "").split('\n');
                    me.wrapper.find('#bill-line1').val(billLines[0] || "");
                    me.wrapper.find('#bill-line2').val(billLines[1] || "");
                    me.wrapper.find('#bill-city').val(billLines[2] || "");
                    me.wrapper.find('#bill-state').val(billLines[3] || "");
                    me.wrapper.find('#bill-pincode').val(billLines[4] || "");

                    // Parse Shipping Address Text
                    const shipLines = (s.custom_shipping_address_text || "").split('\n');
                    me.wrapper.find('#ship-line1').val(shipLines[0] || "");
                    me.wrapper.find('#ship-line2').val(shipLines[1] || "");
                    me.wrapper.find('#ship-city').val(shipLines[2] || "");
                    me.wrapper.find('#ship-state').val(shipLines[3] || "");
                    me.wrapper.find('#ship-pincode').val(shipLines[4] || "");

                    const isSame = s.custom_address_text && s.custom_address_text === s.custom_shipping_address_text;
                    me.wrapper.find('#same-as-billing').prop('checked', isSame);
                    me.toggle_same_as_billing(isSame);

                    // Set Advanced
                    me.wrapper.find('#supp-group').val(s.supplier_group || "Local");
                    me.wrapper.find('#supp-credit-days').val(s.custom_credit_days || 0);
                    me.wrapper.find('#supp-payment-terms').val(s.payment_terms || "");
                    me.wrapper.find('#supp-currency').val(s.default_currency || "");
                    me.wrapper.find('#supp-price-list').val(s.default_price_list || "");
                    me.wrapper.find('#supp-bank-account').val(s.default_bank_account || "");
                    me.wrapper.find('#supp-is-internal-supplier').prop('checked', !!s.is_internal_supplier);
                    me.toggle_internal_supplier(!!s.is_internal_supplier);
                    me.wrapper.find('#supp-represents-company').val(s.represents_company || "");
                    me.wrapper.find('#supp-is-transporter').prop('checked', !!s.is_transporter);
                    me.wrapper.find('#supp-allow-invoice-no-po').prop('checked', !!s.allow_purchase_invoice_creation_without_purchase_order);
                    me.wrapper.find('#supp-allow-invoice-no-receipt').prop('checked', !!s.allow_purchase_invoice_creation_without_purchase_receipt);
                    me.wrapper.find('#supp-is-frozen').prop('checked', !!s.is_frozen);
                    me.wrapper.find('#supp-hold-type').val(s.hold_type || "All");
                    me.wrapper.find('#supp-release-date').val(s.release_date || "");
                    me.wrapper.find('#supp-warn-rfqs').prop('checked', !!s.warn_rfqs);
                    me.wrapper.find('#supp-prevent-rfqs').prop('checked', !!s.prevent_rfqs);
                    me.wrapper.find('#supp-warn-pos').prop('checked', !!s.warn_pos);
                    me.wrapper.find('#supp-prevent-pos').prop('checked', !!s.prevent_pos);
                    me.wrapper.find('#supp-website').val(s.website || "");
                    me.wrapper.find('#supp-language').val(s.language || "");
                    me.wrapper.find('#supp-details').val(s.supplier_details || "");

                    me.wrapper.find('#smriti-supplier-modal').addClass('open');
                }
            }
        });
    }

    close_supplier_modal() {
        this.wrapper.find('#smriti-supplier-modal').removeClass('open');
    }

    toggle_same_as_billing(isSame) {
        const shipSection = this.wrapper.find('#shipping-address-section');
        if (isSame) {
            shipSection.css({
                'opacity': '0.5',
                'pointer-events': 'none'
            });
            // Sync values
            this.wrapper.find('#ship-line1').val(this.wrapper.find('#bill-line1').val());
            this.wrapper.find('#ship-line2').val(this.wrapper.find('#bill-line2').val());
            this.wrapper.find('#ship-city').val(this.wrapper.find('#bill-city').val());
            this.wrapper.find('#ship-state').val(this.wrapper.find('#bill-state').val());
            this.wrapper.find('#ship-pincode').val(this.wrapper.find('#bill-pincode').val());
        } else {
            shipSection.css({
                'opacity': '1',
                'pointer-events': 'all'
            });
        }
    }

    auto_resolve_state(gstin, prefix) {
        if (!gstin || gstin.trim().length < 2) return;
        const code = gstin.trim().substring(0, 2);
        const state = this.GST_STATE_CODES[code];
        if (state) {
            const el = this.wrapper.find(`#${prefix}-state`);
            if (el.length) {
                el.val(state);
                el.addClass('retrieval-glowing');
                setTimeout(() => { el.removeClass('retrieval-glowing'); }, 2000);
            }
        }
    }

    save_supplier_detail() {
        var me = this;
        const name = this.wrapper.find('#supp-name').val().trim();
        const suppId = this.wrapper.find('#supp-name-id').val();

        if (!name) {
            frappe.show_alert({message: __('Please enter the Supplier Name.'), indicator: 'red'});
            return;
        }

        const btn = this.wrapper.find('#btn-save');
        btn.prop('disabled', true);

        // Construct addresses texts
        const billText = [
            this.wrapper.find('#bill-line1').val().trim(),
            this.wrapper.find('#bill-line2').val().trim(),
            this.wrapper.find('#bill-city').val().trim(),
            this.wrapper.find('#bill-state').val().trim(),
            this.wrapper.find('#bill-pincode').val().trim()
        ].join('\n');

        let shipText = billText;
        if (!this.wrapper.find('#same-as-billing').is(':checked')) {
            shipText = [
                this.wrapper.find('#ship-line1').val().trim(),
                this.wrapper.find('#ship-line2').val().trim(),
                this.wrapper.find('#ship-city').val().trim(),
                this.wrapper.find('#ship-state').val().trim(),
                this.wrapper.find('#ship-pincode').val().trim()
            ].join('\n');
        }

        const args = {
            naming_series: this.wrapper.find('#supp-naming-series').val(),
            supplier_name: name,
            supplier_type: this.wrapper.find('#supp-type').val(),
            supplier_group: this.wrapper.find('#supp-group').val(),
            contact_person: this.wrapper.find('#supp-contact-person').val().trim(),
            status: this.wrapper.find('#supp-status').val(),
            mobile_no: this.wrapper.find('#supp-mobile').val().trim(),
            email_id: this.wrapper.find('#supp-email').val().trim(),
            gstin: this.wrapper.find('#supp-gstin').val().trim(),
            gst_category: this.wrapper.find('#supp-gst-category').val(),
            pan: this.wrapper.find('#supp-pan').val().trim().toUpperCase(),
            custom_credit_days: this.wrapper.find('#supp-credit-days').val(),
            custom_address_text: billText,
            custom_shipping_address_text: shipText,
            custom_vendor_code: this.wrapper.find('#supp-vendor-code').val().trim(),
            
            // Advanced fields
            default_currency: this.wrapper.find('#supp-currency').val(),
            default_bank_account: this.wrapper.find('#supp-bank-account').val(),
            default_price_list: this.wrapper.find('#supp-price-list').val(),
            payment_terms: this.wrapper.find('#supp-payment-terms').val(),
            is_internal_supplier: this.wrapper.find('#supp-is-internal-supplier').is(':checked') ? 1 : 0,
            represents_company: this.wrapper.find('#supp-represents-company').val(),
            is_transporter: this.wrapper.find('#supp-is-transporter').is(':checked') ? 1 : 0,
            allow_purchase_invoice_creation_without_purchase_order: this.wrapper.find('#supp-allow-invoice-no-po').is(':checked') ? 1 : 0,
            allow_purchase_invoice_creation_without_purchase_receipt: this.wrapper.find('#supp-allow-invoice-no-receipt').is(':checked') ? 1 : 0,
            is_frozen: this.wrapper.find('#supp-is-frozen').is(':checked') ? 1 : 0,
            hold_type: this.wrapper.find('#supp-hold-type').val(),
            release_date: this.wrapper.find('#supp-release-date').val(),
            warn_rfqs: this.wrapper.find('#supp-warn-rfqs').is(':checked') ? 1 : 0,
            prevent_rfqs: this.wrapper.find('#supp-prevent-rfqs').is(':checked') ? 1 : 0,
            warn_pos: this.wrapper.find('#supp-warn-pos').is(':checked') ? 1 : 0,
            prevent_pos: this.wrapper.find('#supp-prevent-pos').is(':checked') ? 1 : 0,
            website: this.wrapper.find('#supp-website').val().trim(),
            language: this.wrapper.find('#supp-language').val(),
            supplier_details: this.wrapper.find('#supp-details').val().trim(),
            name: suppId || null
        };

        frappe.call({
            method: 'smriti_retail_os.master_api.save_supplier_detail',
            args: args,
            freeze: true,
            freeze_message: __('Saving Supplier Record...'),
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({message: __('Supplier record saved successfully!'), indicator: 'green'});
                    me.close_supplier_modal();
                    me.load_suppliers();
                }
                btn.prop('disabled', false);
            },
            error: function() {
                btn.prop('disabled', false);
            }
        });
    }
}
