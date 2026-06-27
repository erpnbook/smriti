/**
 * @file: smriti_retail_os/public/js/item.js
 * @description: Item form customizations for SMRITI Retail OS — hides advanced tabs, shows retail fields.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.8.6
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

frappe.ui.form.on('Item', {
    onload: function(frm) {
        if (frm.is_new()) {
            frm.set_value('custom_is_retail_item', 1);
        }
    },
    refresh: function(frm) {
        // HSN-first: custom_gst_percentage is always read-only, auto-derived from HSN master
        frm.set_df_property('custom_gst_percentage', 'read_only', 1);
        frm.set_df_property('custom_gst_percentage', 'description',
            __('Auto-derived from HSN Code. Set HSN Code to update.'));

        const is_smriti = frappe.user.has_role("SMRITI Store Manager") || frappe.user.has_role("SMRITI Cashier");
        if (is_smriti) {
            // 1. Hide Advanced Tabs
            const tabs_to_hide = [
                'accounting', 'uom_tab', 'item_tax_section_break', 
                'inventory_section', 'variants_section', 'purchasing_tab', 
                'sales_details', 'manufacturing', 'quality_tab', 'dashboard_tab'
            ];
            tabs_to_hide.forEach(tab => frm.toggle_display(tab, false));

            // 2. Hide Advanced Sections in Details Tab
            const sections_to_hide = [
                'section_break_zlmj', 'section_break_gjns', 'section_break_znra', 'section_break_11'
            ];
            sections_to_hide.forEach(sec => frm.toggle_display(sec, false));

            // 3. Make sure our SMRITI fields are visible and prominent
            frm.toggle_display('custom_is_retail_item', true);
            frm.toggle_display('custom_department', true);
            frm.toggle_display('custom_gst_percentage', true);
            frm.toggle_display('custom_mrp', true);
            frm.toggle_display('gst_hsn_code', true);
            frm.toggle_display('custom_current_stock_html', true);
            
            // 4. Fetch current retail stock dynamically
            if (!frm.is_new()) {
                frappe.call({
                    method: 'smriti_retail_os.api.get_item_stock',
                    args: { item_code: frm.doc.item_code },
                    callback: function(r) {
                        if (r.message) {
                            frm.set_df_property('custom_current_stock_html', 'options', 
                                `<div class="p-3 my-2" style="background: rgba(13, 148, 136, 0.1); border: 1px solid rgba(13, 148, 136, 0.3); border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                                    <div style="background: #0d9488; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1em;">🛒</div>
                                    <div>
                                        <span style="font-weight: 600; color: #0f766e; font-size: 1.05em; display: block;">Retail Stock Status</span>
                                        <span style="font-weight: 700; color: #0d9488; font-size: 1.25em;">${r.message.actual_qty || 0} Units Available</span>
                                    </div>
                                 </div>`
                            );
                        }
                    }
                });
            }
        }
    },
    gst_hsn_code: function(frm) {
        // HSN-first: when HSN code changes, auto-derive GST % from HSN master
        if (frm.doc.gst_hsn_code) {
            frappe.call({
                method: 'smriti_retail_os.item_master_api.get_hsn_gst_rate',
                args: { hsn_code: frm.doc.gst_hsn_code },
                callback: function(r) {
                    if (r.message !== undefined) {
                        frm.set_value('custom_gst_percentage', String(r.message));
                    }
                }
            });
        } else {
            frm.set_value('custom_gst_percentage', '0');
        }
    }
});
