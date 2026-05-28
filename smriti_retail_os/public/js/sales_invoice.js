/**
 * @file: smriti_retail_os/public/js/sales_invoice.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ─────────────────────────────────────────────
   SMRITI — Shoper9 Pure Mode
   Beautifully simple, sleek, and compact.
   ───────────────────────────────────────────── */

frappe.ui.form.on("Sales Invoice", {
    setup: function(frm) {
        if (frappe.user.has_role("System Manager")) return;
        frm.set_query("selling_price_list", () => ({ filters: { selling: 1 } }));
    },

    onload: function(frm) {
        if (frappe.user.has_role("System Manager")) return;
        _pure_apply_clutter_removal(frm);
    },

    refresh: function(frm) {
        if (frappe.user.has_role("System Manager")) return;
        _pure_apply_clutter_removal(frm);
        _pure_render_sleek_ui(frm);
        
        // Clean Action Buttons
        frm.page.clear_inner_toolbar();
        if (frappe.user.has_role("SMRITI Cashier")) {
            frm.add_custom_button(__("← New Bill"), () => frappe.set_route("smriti-billing"), __("SMRITI"));
        }
    }
});

function _pure_apply_clutter_removal(frm) {
    // 1. Hide ALL Secondary Tabs
    const hide_tabs = [
        "payments_tab", "contact_and_address_tab", "terms_tab", 
        "more_info_tab", "connections_tab", "gst_section",
        "subscription_section", "automation_section", "utm_analytics_section"
    ];
    
    // 2. Hide EVERY Field Mentioned by User as Clutter
    const hide_fields = [
        "naming_series", "posting_time", "set_posting_time", "due_date",
        "is_pos", "is_return", "is_debit_note", "apply_tds", "title",
        "scan_barcode", "update_stock", "tax_category", "shipping_rule", 
        "incoterm", "use_company_roundoff_cost_center", "total_advance",
        "outstanding_amount", "amended_from", "taxes_and_charges",
        "total_qty", "total", "base_total_taxes_and_charges", "total_taxes_and_charges",
        "rounding_adjustment", "grand_total"
    ];

    // 3. Hide ALL Section Breaks to remove horizontal lines and labels
    const hide_sections = [
        "customer_section", "currency_and_price_list", "taxes_section",
        "commission_section", "sales_team_section", "packing_list",
        "loyalty_section", "write_off_section", "advances_section",
        "items_section", "totals_section", "section_break_30", "time_sheet_list",
        "pricing_rule_details", "sec_tax_breakup", "other_charges_calculation"
    ];

    hide_tabs.forEach(t => frm.set_df_property(t, "hidden", 1));
    hide_fields.forEach(f => frm.toggle_display(f, false));
    hide_sections.forEach(s => frm.set_df_property(s, "hidden", 1));

    // Ensure items and customer are still functional but the noise is gone
    frm.toggle_display("customer", true);
    frm.toggle_display("posting_date", true);
    frm.toggle_display("items", true);
    frm.toggle_display("rounded_total", true);

    // 4. Simplify the Items Grid Columns
    if (frm.fields_dict.items && frm.fields_dict.items.grid) {
        const grid = frm.fields_dict.items.grid;
        
        // Define kept fields and their column spans (should sum to 12)
        const kept_fields = {
            "item_code": 2,
            "item_name": 4,
            "qty": 2,
            "rate": 2,
            "amount": 2
        };

        grid.docfields.forEach(df => {
            if (kept_fields[df.fieldname] !== undefined) {
                df.hidden = 0;
                df.in_list_view = 1;
                df.columns = kept_fields[df.fieldname];
            } else {
                df.hidden = 1;
                df.in_list_view = 0;
            }
        });
        
        grid.refresh();
    }
}

function _pure_render_sleek_ui(frm) {
    frm.dashboard.clear_headline();
    
    const amount = frappe.format(frm.doc.rounded_total || frm.doc.grand_total, {fieldtype:"Currency"});
    const tax = frappe.format(frm.doc.total_taxes_and_charges, {fieldtype:"Currency"});
    const items_count = (frm.doc.items || []).length;
    
    // Inject custom "Rearranged" Sleek Header styled by smriti_sales_invoice.css
    frm.dashboard.set_headline(`
        <div class="dashboard-headline-card" style="padding: 20px; display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <div style="display: flex; gap: 40px;">
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #667085; font-weight: 700; margin-bottom: 4px; letter-spacing: 0.5px;">Customer</div>
                    <div style="font-size: 16px; font-weight: 600; color: #101828;">${frm.doc.customer_name || 'Walk-In Customer'}</div>
                </div>
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #667085; font-weight: 700; margin-bottom: 4px; letter-spacing: 0.5px;">Date</div>
                    <div style="font-size: 16px; font-weight: 600; color: #101828;">${frappe.datetime.str_to_user(frm.doc.posting_date)}</div>
                </div>
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #667085; font-weight: 700; margin-bottom: 4px; letter-spacing: 0.5px;">Items</div>
                    <div style="font-size: 16px; font-weight: 600; color: #101828;">${items_count} SKU(s)</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; text-transform: uppercase; color: #667085; font-weight: 700; margin-bottom: 2px; letter-spacing: 0.5px;">Total Payable</div>
                <div style="font-size: 38px; font-weight: 900; color: #6941c6; line-height: 1;">${amount}</div>
                <div style="font-size: 11px; color: #027a48; font-weight: 600; margin-top: 4px;">Incl. GST: ${tax}</div>
            </div>
        </div>
    `);
}
