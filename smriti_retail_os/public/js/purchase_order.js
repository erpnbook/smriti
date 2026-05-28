/**
 * @file: smriti_retail_os/public/js/purchase_order.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ─────────────────────────────────────────────
   SMRITI — Purchase Order Form Simplification
   Retail-focused PO creation for Store Manager.
   System Manager sees normal ERPNext form.
   ───────────────────────────────────────────── */

frappe.ui.form.on("Purchase Order", {

    setup: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_po_setup(frm);
    },

    refresh: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_po_refresh(frm);
    },

    onload: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_po_simplify_layout(frm);

        // Auto-set company if only one
        if (!frm.doc.company) {
            frappe.db.get_single_value("Global Defaults", "default_company")
                .then(company => {
                    if (company) frm.set_value("company", company);
                });
        }
        // Auto-set schedule date to today + 7 days
        if (!frm.doc.schedule_date) {
            frm.set_value("schedule_date",
                frappe.datetime.add_days(frappe.datetime.get_today(), 7));
        }
    },

    supplier: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        if (frm.doc.supplier) {
            // Auto-fill credit days from custom field
            frappe.db.get_value("Supplier", frm.doc.supplier,
                ["custom_credit_days", "custom_address_text"],
                function (r) {
                    if (r && r.custom_credit_days) {
                        frm.dashboard.set_headline(
                            `<span style="color:var(--smriti-text-muted,#8892a4);font-size:12px">
                                📋 Credit Days: <b>${r.custom_credit_days}</b> |
                                ${r.custom_address_text || ""}
                            </span>`
                        );
                    }
                }
            );
        }
    }
});

function _smriti_po_setup(frm) {
    // Filter suppliers — active only
    frm.set_query("supplier", function () {
        return { filters: { disabled: 0, supplier_type: "Company" } };
    });
    // Filter items — retail items only
    frm.set_query("item_code", "items", function () {
        return { filters: { disabled: 0, is_purchase_item: 1 } };
    });
}

function _smriti_po_simplify_layout(frm) {
    const hide_fields = [
        "amended_from", "select_print_heading",
        "letter_head", "language",
        "tc_name", "commission_rate",
        "total_commission", "apply_discount_on",
        "additional_discount_percentage",
        "ignore_pricing_rule", "set_from_warehouse",
        "plc_conversion_rate", "price_list_currency",
        "tax_category", "shipping_address",
        "billing_address", "supplier_warehouse"
    ];

    // Cashier — more restrictions
    if (frappe.user.has_role("SMRITI Cashier")) {
        hide_fields.push("buying_price_list", "taxes_and_charges");
    }

    hide_fields.forEach(f => frm.toggle_display(f, false));
}

function _smriti_po_refresh(frm) {
    _smriti_po_simplify_layout(frm);

    // Quick navigation
    frm.add_custom_button(__("← SMRITI Desk"), function () {
        frappe.set_route("smriti-desk");
    }, __("SMRITI"));

    frm.add_custom_button(__("📦 Purchase Receipt"), function () {
        frappe.set_route("List", "Purchase Receipt");
    }, __("SMRITI"));

    // Status indicator
    const status_colors = {
        "Draft":      { color: "#8892a4", icon: "📝" },
        "To Receive and Bill": { color: "#f59e0b", icon: "📦" },
        "To Bill":    { color: "#e94560", icon: "🧾" },
        "Completed":  { color: "#10b981", icon: "✅" },
        "Cancelled":  { color: "#ef4444", icon: "❌" }
    };
    const st = status_colors[frm.doc.status] || { color: "#8892a4", icon: "❓" };
    if (frm.doc.docstatus >= 0) {
        frm.dashboard.set_headline(
            `<span style="color:${st.color};font-weight:600">
                ${st.icon} ${frm.doc.status || "Draft"} —
                Total: ₹${frappe.format(frm.doc.grand_total, {fieldtype:"Currency"})}
            </span>`
        );
    }

    // Quick "Make Purchase Receipt" visible button for Store Manager
    if (frm.doc.docstatus === 1 &&
        frm.doc.status !== "Completed" &&
        frappe.user.has_role("SMRITI Store Manager")) {
        frm.add_custom_button(__("📦 Make Receipt"), function () {
            frappe.model.open_mapped_doc({
                method: "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt",
                frm: frm
            });
        }, __("SMRITI"));
    }
}
