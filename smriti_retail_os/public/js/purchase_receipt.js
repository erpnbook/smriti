/**
 * @file: smriti_retail_os/public/js/purchase_receipt.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ─────────────────────────────────────────────
   SMRITI — Purchase Receipt Form Simplification
   GRN receipt entry for retail store.
   System Manager sees normal standard form.
   ───────────────────────────────────────────── */

frappe.ui.form.on("Purchase Receipt", {

    setup: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_pr_setup(frm);
    },

    refresh: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_pr_refresh(frm);
    },

    onload: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_pr_simplify_layout(frm);

        // Auto-set posting date to today
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today());
        }
        // Auto-set company
        if (!frm.doc.company) {
            frappe.db.get_single_value("Global Defaults", "default_company")
                .then(c => { if (c) frm.set_value("company", c); });
        }
    },

    supplier: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        if (frm.doc.supplier) {
            frappe.db.get_value("Supplier", frm.doc.supplier,
                "custom_address_text",
                function (r) {
                    if (r && r.custom_address_text) {
                        frm.dashboard.set_headline(
                            `<span style="color:var(--smriti-text-muted,#8892a4);font-size:12px">
                                🏭 ${r.custom_address_text}
                            </span>`
                        );
                    }
                }
            );
        }
    },

    purchase_order: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        if (frm.doc.purchase_order) {
            frappe.show_alert({
                message: "Items will be auto-fetched from Purchase Order.",
                indicator: "blue"
            }, 4);
        }
    }
});

/* ── Item-level: show received qty vs ordered ── */
frappe.ui.form.on("Purchase Receipt Item", {
    qty: function (frm, cdt, cdn) {
        if (frappe.user.has_role("System Manager")) return;
        const row = locals[cdt][cdn];
        if (row.purchase_order_item) {
            frappe.db.get_value(
                "Purchase Order Item",
                row.purchase_order_item,
                "qty",
                function (r) {
                    if (r && row.qty > r.qty) {
                        frappe.show_alert({
                            message: `⚠️ Qty (${row.qty}) exceeds PO qty (${r.qty}) for ${row.item_code}`,
                            indicator: "orange"
                        }, 5);
                    }
                }
            );
        }
    }
});

function _smriti_pr_setup(frm) {
    frm.set_query("supplier", function () {
        return { filters: { disabled: 0 } };
    });
    frm.set_query("item_code", "items", function () {
        return { filters: { disabled: 0, is_purchase_item: 1 } };
    });
    frm.set_query("purchase_order", function () {
        return {
            filters: {
                supplier: frm.doc.supplier || undefined,
                docstatus: 1,
                status: ["in", ["To Receive and Bill", "To Receive"]]
            }
        };
    });
}

function _smriti_pr_simplify_layout(frm) {
    const hide_fields = [
        "amended_from", "select_print_heading",
        "letter_head", "language",
        "tc_name", "apply_discount_on",
        "additional_discount_percentage",
        "ignore_pricing_rule",
        "plc_conversion_rate", "price_list_currency",
        "tax_category", "shipping_address",
        "billing_address", "supplier_warehouse",
        "auto_repeat", "scan_barcode",
        "lr_no", "lr_date", "vehicle_no"
    ];
    hide_fields.forEach(f => frm.toggle_display(f, false));
}

function _smriti_pr_refresh(frm) {
    _smriti_pr_simplify_layout(frm);

    // Quick navigation
    frm.add_custom_button(__("← SMRITI Desk"), function () {
        frappe.set_route("smriti-desk");
    }, __("SMRITI"));

    frm.add_custom_button(__("📋 Purchase Orders"), function () {
        frappe.set_route("List", "Purchase Order");
    }, __("SMRITI"));

    // GRN summary headline
    if (frm.doc.docstatus === 1) {
        const item_count = (frm.doc.items || []).length;
        const total_qty  = (frm.doc.items || []).reduce(
            (sum, r) => sum + (r.qty || 0), 0
        );
        frm.dashboard.set_headline(
            `<span style="color:#10b981;font-weight:600">
                ✅ GRN Received — ${item_count} SKUs |
                ${total_qty} units |
                ₹${frappe.format(frm.doc.grand_total, {fieldtype:"Currency"})}
            </span>`
        );
    } else if (frm.doc.docstatus === 0) {
        frm.dashboard.set_headline(
            `<span style="color:#f59e0b;font-weight:600">
                📝 Draft GRN — Verify quantities before submitting
            </span>`
        );
    }

    // Barcode scan shortcut for items
    if (frm.doc.docstatus === 0 && frappe.user.has_role("SMRITI Store Manager")) {
        frm.add_custom_button(__("🔍 Scan & Add Item"), function () {
            frappe.prompt(
                [{ label: "Barcode", fieldname: "barcode", fieldtype: "Data",
                   reqd: 1, description: "Scan or type barcode" }],
                function (vals) {
                    frappe.call({
                        method: "smriti_retail_os.billing_api.add_item_by_barcode",
                        args: { barcode: vals.barcode },
                        callback: function (r) {
                            if (r.message) {
                                const item = r.message;
                                const row  = frm.add_child("items");
                                row.item_code = item.item_code;
                                row.item_name = item.item_name;
                                row.qty       = 1;
                                row.rate      = item.rate || 0;
                                row.warehouse = frm.doc.set_warehouse || "";
                                frm.refresh_field("items");
                                frappe.show_alert({
                                    message: `✅ Added: ${item.item_name}`,
                                    indicator: "green"
                                }, 3);
                            }
                        }
                    });
                },
                __("Scan Item"),
                __("Add")
            );
        }, __("SMRITI"));
    }
}
