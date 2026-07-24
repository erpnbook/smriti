/**
 * @file    smriti_retail_os/public/js/smriti_core.js
 * @desc    SMRITI Core Framework — JavaScript Adapter Layer.
 *
 *          This file isolates ALL Frappe/ERPNext JavaScript APIs behind the
 *          smriti.* namespace. No www/ page, no component, no studio JS file
 *          may call frappe.* directly. All calls must go through this adapter.
 *
 *          Architecture: Architecture Constitution Rule 2 (Service-First Design)
 *          Guard:        Guard 6 — UI Persistence Boundary (warning mode)
 *
 * @author  Jawahar R. Mallah <jawahar.mallah@gmail.com>
 * @version 1.0.0
 * @license GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function () {
    "use strict";

    // ── Namespace Bootstrap ────────────────────────────────────────────────────
    window.smriti = window.smriti || window.SMRITI || {};
    window.SMRITI = window.smriti;

    // ── API Adapter ────────────────────────────────────────────────────────────
    /**
     * smriti.api — all SMRITI-to-backend communication.
     *
     * Usage (correct):
     *   smriti.api.call("smriti_retail_os.billing_api.get_summary", { company })
     *     .then(data => render(data))
     *     .catch(err => smriti.notify.error("Load Failed", err.message));
     *
     * Usage (forbidden — NEVER do this in www/ pages):
     *   frappe.call({ method: "...", ... })   ← VIOLATION (Guard 6)
     */
    smriti.api = {

        /**
         * Make a whitelisted server-side call.
         * @param {string} method   - Dotted Python method path
         * @param {object} args     - Arguments to pass to the method
         * @param {object} [opts]   - Optional overrides for frappe.call
         * @returns {Promise<any>}  - Resolves with response.message
         */
        call(method, args = {}, opts = {}) {
            return new Promise((resolve, reject) => {
                frappe.call({
                    method,
                    args,
                    callback: r => resolve(r.message),
                    error: e => {
                        let msg = "";
                        try {
                            if (e?.responseJSON?._server_messages) {
                                const msgs = JSON.parse(e.responseJSON._server_messages);
                                msg = msgs.map(m => {
                                    try { return JSON.parse(m).message; } catch(err) { return m; }
                                }).join("\n");
                            } else if (e?.responseJSON?.exception) {
                                const lines = String(e.responseJSON.exception).trim().split("\n");
                                msg = lines[lines.length - 1] || e.responseJSON.exception;
                            } else if (e?.responseText) {
                                const parsed = JSON.parse(e.responseText);
                                msg = parsed.exception || parsed.message || "";
                            }
                        } catch (err) {
                            msg = "";
                        }
                        if (!msg) {
                            msg = (e && e.statusText && e.statusText !== "error") ? e.statusText : "Request failed. Please check backend server status.";
                        }
                        reject(new Error(msg));
                    },
                    ...opts
                });
            });
        },

        /**
         * Fetch a single SMRITI document by model and name.
         * @param {string} model    - SMRITI model name (e.g. "Customer")
         * @param {string} name     - Document ID (e.g. "CUST-001")
         * @param {Array}  [fields] - Fields to return
         * @returns {Promise<object>}
         */
        /**
         * Fetch a single SMRITI document by model and name.
         * @param {string} model - SMRITI model name (e.g. "Customer")
         * @param {string} name  - Document ID (e.g. "CUST-001")
         * @returns {Promise<object>}
         */
        get(model, name) {
            return smriti.api.call(
                "smriti_retail_os.core.api.get",
                { model, name }
            );
        },

        /**
         * Fetch a single field value from a SMRITI document.
         * @param {string} model     - SMRITI model name
         * @param {string} name      - Document ID
         * @param {string} fieldname - Field to fetch
         * @returns {Promise<*>}
         */
        getField(model, name, fieldname) {
            return smriti.api.call(
                "smriti_retail_os.core.api.get_field",
                { model, name, fieldname }
            );
        },

        /**
         * Fetch a filtered list of SMRITI documents.
         * @param {string} model           - SMRITI model name
         * @param {object} [opts]          - Options: filters, fields, order_by, limit, start
         * @param {object} [opts.filters]  - Filter conditions {fieldname: value}
         * @param {Array}  [opts.fields]   - Fields to return (default: ["name"])
         * @param {string} [opts.order_by] - Sort expression (e.g. "modified desc")
         * @param {number} [opts.limit]    - Max records (default: 20)
         * @param {number} [opts.start]    - Pagination offset
         * @returns {Promise<Array>}
         */
        getList(model, opts = {}) {
            return smriti.api.call(
                "smriti_retail_os.core.api.get_list",
                { model, filters: opts.filters || {}, fields: opts.fields || ["name"],
                  order_by: opts.order_by || null, limit: opts.limit || 20, start: opts.start || 0 }
            );
        },

        /**
         * Check if a SMRITI document exists.
         * @param {string} model - SMRITI model name
         * @param {string} name  - Document ID
         * @returns {Promise<boolean>}
         */
        exists(model, name) {
            return smriti.api.call(
                "smriti_retail_os.core.api.exists",
                { model, name }
            );
        },

        /**
         * Save (create or update) a SMRITI document.
         * @param {string} model - SMRITI model name
         * @param {object} data  - Document data (include 'name' to update, omit to create)
         * @returns {Promise<object>}
         */
        save(model, data) {
            return smriti.api.call(
                "smriti_retail_os.core.api.save",
                { model, data }
            );
        },

        /**
         * Submit (post) a SMRITI document.
         * @param {string} model - SMRITI model name
         * @param {string} name  - Document ID to submit
         * @returns {Promise<object>}
         */
        submit(model, name) {
            return smriti.api.call(
                "smriti_retail_os.core.api.submit",
                { model, name }
            );
        },

        /**
         * Delete a SMRITI document.
         * @param {string} model - SMRITI model name
         * @param {string} name  - Document ID
         * @returns {Promise<{ok: true, deleted: string}>}
         */
        delete(model, name) {
            return smriti.api.call(
                "smriti_retail_os.core.api.delete",
                { model, name }
            );
        },

        /**
         * Fetch the Form Engine schema for a model.
         * Used by smriti.forms.render() to build the form UI.
         * @param {string} model - SMRITI model name (e.g. "Purchase")
         * @returns {Promise<{model, title, fields}>}
         */
        schema(model) {
            return smriti.api.call(
                "smriti_retail_os.core.api.schema",
                { model }
            );
        },

        /**
         * Typeahead / lookup search for a LookupField.
         * @param {string} model           - SMRITI model name
         * @param {object} [opts]
         * @param {string} [opts.query]         - Search string
         * @param {object} [opts.filters]        - Additional static filters
         * @param {string} [opts.display_field]  - Field to use as label
         * @param {number} [opts.limit]          - Max results
         * @returns {Promise<Array<{value, label}>>}
         */
        lookup(model, opts = {}) {
            return smriti.api.call(
                "smriti_retail_os.core.api.lookup",
                { model, query: opts.query || "", filters: opts.filters || {},
                  display_field: opts.display_field || "name", limit: opts.limit || 20 }
            );
        }
    };

    // ── Notification Adapter ───────────────────────────────────────────────────
    /**
     * smriti.notify — HREP-compliant user notifications.
     *
     * Usage (correct):
     *   smriti.notify.success("Saved", "Purchase order saved successfully.");
     *   smriti.notify.error("Save Failed", "The supplier field is required.", "SMRITI-VAL-001");
     *
     * Usage (forbidden):
     *   frappe.show_alert(...)   ← VIOLATION
     *   frappe.msgprint(...)     ← VIOLATION
     */
    smriti.notify = {

        /** @param {string} title @param {string} message */
        success(title, message = "") {
            frappe.show_alert(
                { message: `<b>${title}</b>${message ? `<br><span>${message}</span>` : ""}`, indicator: "green" },
                5
            );
        },

        /**
         * @param {string} title
         * @param {string} message  - Business-language, no technical details
         * @param {string} [refId]  - SMRITI error reference ID
         */
        error(title, message = "", refId = null) {
            const ref = refId ? `<br><small style="opacity:0.7">Ref: ${refId}</small>` : "";
            frappe.show_alert(
                { message: `<b>${title}</b><br><span>${message}</span>${ref}`, indicator: "red" },
                8
            );
        },

        /** @param {string} title @param {string} message */
        warning(title, message = "") {
            frappe.show_alert(
                { message: `<b>${title}</b>${message ? `<br><span>${message}</span>` : ""}`, indicator: "orange" },
                6
            );
        },

        /** @param {string} title @param {string} message */
        info(title, message = "") {
            frappe.show_alert(
                { message: `<b>${title}</b>${message ? `<br><span>${message}</span>` : ""}`, indicator: "blue" },
                5
            );
        }
    };

    // ── Dialog Adapter ─────────────────────────────────────────────────────────
    /**
     * smriti.dialog — SMRITI dialog utilities.
     *
     * Usage (correct):
     *   smriti.dialog.confirm("Delete Customer?", "This cannot be undone.",
     *       () => smriti.api.delete("Customer", name));
     *
     * Usage (forbidden):
     *   frappe.confirm(...)   ← VIOLATION
     *   frappe.prompt(...)    ← VIOLATION
     *   frappe.msgprint(...)  ← VIOLATION
     */
    smriti.dialog = {

        /**
         * Show an informational alert dialog.
         * @param {string}   title
         * @param {string}   message
         * @param {Function} [onOk]
         */
        alert(title, message, onOk = null) {
            frappe.msgprint({ title, message, indicator: "blue" });
            if (typeof onOk === "function") onOk();
        },

        /**
         * Show a confirmation dialog.
         * @param {string}   title
         * @param {string}   message
         * @param {Function} onConfirm - Called when user confirms
         * @param {Function} [onCancel]
         */
        confirm(title, message, onConfirm, onCancel = null) {
            frappe.confirm(
                `<b>${title}</b><br>${message}`,
                onConfirm,
                onCancel || (() => {})
            );
        },

        /**
         * Show a prompt dialog with one or more fields.
         * @param {string}   title
         * @param {Array}    fields  - Frappe field definitions
         * @param {Function} onSubmit - Called with {fieldname: value} on submit
         * @param {string}   [primaryLabel]
         */
        prompt(title, fields, onSubmit, primaryLabel = "Confirm") {
            const d = new frappe.ui.Dialog({
                title,
                fields,
                primary_action_label: primaryLabel,
                primary_action(values) {
                    d.hide();
                    if (typeof onSubmit === "function") onSubmit(values);
                }
            });
            d.show();
            return d;
        }
    };

    // ── Navigation Adapter ─────────────────────────────────────────────────────
    /**
     * smriti.navigation — all SMRITI page routing.
     *
     * RULE: Never use frappe.set_route() or window.location for /app/* or /desk/* URLs.
     *       SMRITI URLs are always clean, business-vocabulary paths (/customers, /billing, etc.)
     *
     * Usage (correct):
     *   smriti.navigation.go(smriti.navigation.routes.customers);
     *   smriti.navigation.go("/customers?search=John");
     *
     * Usage (forbidden):
     *   frappe.set_route("Form", "Customer", "CUST-001")   ← VIOLATION
     *   window.location.href = "/app/customer"              ← VIOLATION
     */
    smriti.navigation = {

        /** Canonical SMRITI page routes. Never use /app/* or /desk/* URLs. */
        routes: {
            home:        "/smriti-home",
            products:    "/products",
            customers:   "/customers",
            suppliers:   "/suppliers",
            billing:     "/billing",
            purchase:    "/smriti-purchase",
            grn:         "/smriti-grn",
            inventory:   "/inventory",
            reports:     "/reports",
            analytics:   "/analytics",
            security:    "/security",
            payments:    "/payments",
            shift:       "/shift",
            barcode:     "/barcode",
            settings:    "/smriti-pos-profiles",
        },

        /**
         * Navigate to a SMRITI page path.
         * @param {string} path - Must be a SMRITI path, never /app/* or /desk/*
         */
        go(path) {
            if (path.includes("/app/") || path.includes("/desk/")) {
                console.error(
                    "[SMRITI Guard 6] Navigation violation: attempted to route to platform URL:",
                    path,
                    "\nUse a SMRITI route instead."
                );
                return;
            }
            window.location.href = path;
        },

        /** Navigate back in browser history. */
        back() { window.history.back(); },

        /** Reload the current page. */
        reload() { window.location.reload(); },

        /** Replace current history entry (no back button). */
        replace(path) { window.location.replace(path); }
    };

    // ── Realtime Events Adapter ────────────────────────────────────────────────
    /**
     * smriti.events — client-side realtime event bus.
     *
     * Usage (correct):
     *   smriti.events.on("smriti:stock_update", data => updateStockDisplay(data));
     *
     * Usage (forbidden):
     *   frappe.realtime.on(...)   ← VIOLATION
     */
    smriti.events = {

        /**
         * Subscribe to a realtime event.
         * @param {string}   event   - Event name (use "smriti:" prefix)
         * @param {Function} handler - Called with event data
         */
        on(event, handler) {
            frappe.realtime.on(event, handler);
        },

        /**
         * Unsubscribe from a realtime event.
         * @param {string}   event
         * @param {Function} handler
         */
        off(event, handler) {
            frappe.realtime.off(event, handler);
        }
    };

    // ── Context Adapter ────────────────────────────────────────────────────────
    /**
     * smriti.context — access to session and site context.
     * Never access frappe.session or frappe.boot directly from www/ pages.
     */
    smriti.context = {

        /** Current logged-in user email. */
        get user() {
            return frappe.session && frappe.session.user;
        },

        /** Current site name. */
        get site() {
            return frappe.boot && frappe.boot.sitename;
        },

        /** User's full name. */
        get fullName() {
            return frappe.boot && frappe.boot.user_info &&
                   frappe.boot.user_info[this.user] &&
                   frappe.boot.user_info[this.user].fullname;
        },

        /** True if user is logged in (not Guest). */
        get isLoggedIn() {
            return this.user && this.user !== "Guest";
        }
    };

    // ── Framework Ready Log ────────────────────────────────────────────────────
    if (window.location.hostname !== "production") {
        console.debug("[SMRITI Core] Framework adapter loaded. smriti.api / smriti.notify / smriti.dialog / smriti.navigation ready.");
    }

})();
