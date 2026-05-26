/* ─────────────────────────────────────────────
   SMRITI — Sales Invoice Form Simplification
   Hides irrelevant fields for retail workflow.
   System Manager sees normal ERPNext form.
   ───────────────────────────────────────────── */

frappe.ui.form.on("Sales Invoice", {

    setup: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_si_setup(frm);
    },

    refresh: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_si_refresh(frm);
    },

    onload: function (frm) {
        if (frappe.user.has_role("System Manager")) return;
        _smriti_si_simplify_layout(frm);
    }
});

/* ── Setup — filters & link defaults ── */
function _smriti_si_setup(frm) {
    // Default selling price list
    frm.set_query("selling_price_list", function () {
        return { filters: { selling: 1 } };
    });

    // Customer filter — show only individuals and companies
    frm.set_query("customer", function () {
        return { filters: { disabled: 0 } };
    });
}

/* ── Simplify layout — hide non-retail fields ── */
function _smriti_si_simplify_layout(frm) {
    // Tabs/sections to hide for cashier
    const hide_fields = [
        "amended_from", "return_against",
        "select_print_heading", "letter_head",
        "language", "tc_name",
        "commission_rate", "total_commission",
        "write_off_account", "write_off_cost_center",
        "write_off_amount", "write_off_outstanding_amount_automatically",
        "loyalty_program", "loyalty_points",
        "redeem_loyalty_points",
        "pos_profile",        // hide raw POS profile link
        "set_posting_time"
    ];

    // Cashier can't change these
    if (frappe.user.has_role("SMRITI Cashier")) {
        hide_fields.push(
            "selling_price_list", "price_list_currency",
            "plc_conversion_rate", "ignore_pricing_rule",
            "apply_discount_on", "additional_discount_percentage"
        );
        frm.set_df_property("customer", "read_only", frm.doc.docstatus === 1 ? 1 : 0);
    }

    hide_fields.forEach(function (f) {
        frm.toggle_display(f, false);
    });
}

/* ── Refresh — quick action buttons ── */
function _smriti_si_refresh(frm) {
    _smriti_si_simplify_layout(frm);

    // Add "Back to Billing" button for Cashier
    if (frappe.user.has_role("SMRITI Cashier")) {
        frm.add_custom_button(__("← Back to Billing"), function () {
            frappe.set_route("smriti-billing");
        }, __("SMRITI"));
    }

    // Store Manager — add quick links
    if (frappe.user.has_role("SMRITI Store Manager")) {
        frm.add_custom_button(__("← SMRITI Desk"), function () {
            frappe.set_route("smriti-desk");
        }, __("SMRITI"));

        if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
            frm.add_custom_button(__("💰 Record Payment"), function () {
                frappe.set_route("payment-entry", "new-payment-entry-1");
            }, __("SMRITI"));
        }
    }

    // Status badge — color coding
    if (frm.doc.docstatus === 1) {
        frm.dashboard.set_headline(
            `<span style="color:#10b981;font-weight:600">
                ✅ Submitted — Outstanding: ₹${frappe.format(frm.doc.outstanding_amount, {fieldtype:"Currency"})}
            </span>`
        );
    }
}
