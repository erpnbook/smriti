// SMRITI Negative Stock Dashboard controller & views
// Author: Jawahar R Mallah <jawahar.mallah@gmail.com>
// Date: 2026-06-29
// Version: 1.9.0


frappe.pages['smriti-negative-stock'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Negative Stock Management',
        single_column: true
    });

    wrapper.page_render = function() {
        wrapper.innerHTML = `
            <div class="smriti-ns-container">
                <div class="smriti-ns-header">
                    <h2>🚫 SMRITI Negative Stock Control Center</h2>
                    <span style="font-size: 14px; color: #64748b; font-weight:500;">Always decision-ready</span>
                </div>

                <!-- Metrics Panel -->
                <div class="smriti-metrics-grid">
                    <div class="smriti-metric-card">
                        <div class="smriti-metric-val" id="metric-today-cases">0</div>
                        <div class="smriti-metric-label">Cases Today</div>
                    </div>
                    <div class="smriti-metric-card">
                        <div class="smriti-metric-val" id="metric-recovered-today">0</div>
                        <div class="smriti-metric-label">Recovered Today</div>
                    </div>
                    <div class="smriti-metric-card">
                        <div class="smriti-metric-val" id="metric-open-cases">0</div>
                        <div class="smriti-metric-label">Open Cases</div>
                    </div>
                    <div class="smriti-metric-card">
                        <div class="smriti-metric-val" id="metric-exposure">₹0.00</div>
                        <div class="smriti-metric-label">Financial Exposure</div>
                    </div>
                    <div class="smriti-metric-card">
                        <div class="smriti-metric-val" id="metric-sla">98.2%</div>
                        <div class="smriti-metric-label">Recovery SLA</div>
                    </div>
                </div>

                <!-- Cases List -->
                <div class="smriti-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3 style="margin: 0;">📋 Active Negative Stock Exceptions</h3>
                        <button class="smriti-btn smriti-btn-secondary" id="refresh-dashboard-btn">
                            <span class="material-symbols-outlined" style="font-size:16px; margin-right:4px;">refresh</span> Refresh
                        </button>
                    </div>

                    <div style="overflow-x: auto;">
                        <table class="smriti-table">
                            <thead>
                                <tr>
                                    <th>Case ID</th>
                                    <th>Item Code</th>
                                    <th>Warehouse</th>
                                    <th>Negative Qty</th>
                                    <th>Decision</th>
                                    <th>Status</th>
                                    <th>Requested By</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="ns-cases-tbody">
                                <tr>
                                    <td colspan="8" style="text-align: center; color: #64748b;">Loading exceptions...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Details Slider Drawer -->
                <div class="smriti-drawer-backdrop" id="ns-drawer-backdrop"></div>
                <div class="smriti-drawer" id="ns-drawer">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;">
                        <h3 style="margin: 0; color: #1A2B5C;" id="drawer-title">Exception Detail</h3>
                        <button class="smriti-btn smriti-btn-secondary" id="close-drawer-btn" style="padding: 4px 8px;">✕</button>
                    </div>
                    <div id="drawer-content">
                        <!-- Filled dynamically -->
                    </div>
                </div>
            </div>
        `;

        // Bind events
        $("#refresh-dashboard-btn").on("click", function() {
            wrapper.load_dashboard_data();
        });

        $("#close-drawer-btn, #ns-drawer-backdrop").on("click", function() {
            wrapper.close_drawer();
        });

        wrapper.load_dashboard_data();
    };

    wrapper.load_dashboard_data = function() {
        // Fetch stats
        frappe.call({
            method: "smriti_retail_os.negative_stock.api.negative_stock_api.get_dashboard_metrics",
            callback: function(r) {
                if (r.message) {
                    const m = r.message;
                    $("#metric-today-cases").text(m.cases_today);
                    $("#metric-recovered-today").text(m.recovered_today);
                    $("#metric-open-cases").text(m.open_cases);
                    $("#metric-exposure").text("₹" + m.exposure.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
                    $("#metric-sla").text(m.sla_compliance);
                }
            }
        });

        // Fetch cases
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "SMRITI Negative Stock Case",
                fields: ["name", "item_code", "warehouse", "negative_qty", "decision", "status", "requested_by", "explanation"],
                order_by: "creation desc",
                limit_page_length: 50
            },
            callback: function(r) {
                const tbody = $("#ns-cases-tbody");
                tbody.empty();

                if (r.message && r.message.length > 0) {
                    r.message.forEach(case_doc => {
                        const row = $(`
                            <tr style="cursor: pointer;">
                                <td><b>${case_doc.name}</b></td>
                                <td>${case_doc.item_code}</td>
                                <td>${case_doc.warehouse}</td>
                                <td style="color: #ef4444; font-weight: 600;">${case_doc.negative_qty}</td>
                                <td><span class="smriti-badge smriti-badge-open">${case_doc.decision}</span></td>
                                <td><span class="smriti-badge smriti-badge-${case_doc.status.toLowerCase().replace(' ', '-')}">${case_doc.status}</span></td>
                                <td>${case_doc.requested_by || 'System'}</td>
                                <td class="action-cell"></td>
                            </tr>
                        `);

                        // Prevent row click when clicking action buttons
                        row.find("td").not(".action-cell").on("click", function() {
                            wrapper.open_drawer(case_doc);
                        });

                        const actionCell = row.find(".action-cell");
                        if (case_doc.status === "Pending Approval") {
                            const approveBtn = $(`<button class="smriti-btn smriti-btn-success" style="padding: 4px 8px; font-size:11px; margin-right:6px;">Approve</button>`);
                            const rejectBtn = $(`<button class="smriti-btn smriti-btn-danger" style="padding: 4px 8px; font-size:11px;">Reject</button>`);

                            approveBtn.on("click", function(e) {
                                e.stopPropagation();
                                wrapper.handle_approval_action(case_doc.name, "approve");
                            });

                            rejectBtn.on("click", function(e) {
                                e.stopPropagation();
                                wrapper.handle_approval_action(case_doc.name, "reject");
                            });

                            actionCell.append(approveBtn).append(rejectBtn);
                        } else {
                            actionCell.html(`<span class="text-muted" style="font-size:11px;">No Action</span>`);
                        }

                        tbody.append(row);
                    });
                } else {
                    tbody.html(`<tr><td colspan="8" style="text-align: center; color: #64748b;">No active negative stock exceptions found.</td></tr>`);
                }
            }
        });
    };

    wrapper.handle_approval_action = function(case_id, action) {
        // Show comment dialog
        const d = new frappe.ui.Dialog({
            title: action === "approve" ? "Approve Negative Stock Case" : "Reject Negative Stock Case",
            fields: [
                {
                    label: "Comment",
                    fieldname: "comment",
                    fieldtype: "Small Text",
                    reqd: true
                },
                {
                    label: "Approval Reference / PO ID",
                    fieldname: "reference",
                    fieldtype: "Data",
                    depends_on: `eval:${action === 'approve'}`
                }
            ],
            primary_action_label: action === "approve" ? "Approve" : "Reject",
            primary_action: function(values) {
                frappe.call({
                    method: action === "approve" ? 
                        "smriti_retail_os.negative_stock.api.negative_stock_api.approve_case" : 
                        "smriti_retail_os.negative_stock.api.negative_stock_api.reject_case",
                    args: {
                        case_id: case_id,
                        comment: values.comment,
                        reference: values.reference || ""
                    },
                    callback: function(r) {
                        d.hide();
                        frappe.show_alert({
                            message: `Case ${case_id} ${action}d successfully.`,
                            indicator: action === "approve" ? "green" : "red"
                        });
                        wrapper.load_dashboard_data();
                    }
                });
            }
        });
        d.show();
    };

    wrapper.open_drawer = function(case_doc) {
        $("#drawer-title").text(`Exception: ${case_doc.name}`);
        $("#drawer-content").html(`
            <div style="margin-bottom: 20px;">
                <span style="font-size: 12px; text-transform: uppercase; color: #64748b; font-weight:600; display:block; margin-bottom:4px;">Item Details</span>
                <b style="font-size: 15px; color:#1A2B5C;">${case_doc.item_code}</b>
                <span style="display:block; font-size:13px; margin-top:2px;">Warehouse: <b>${case_doc.warehouse}</b></span>
                <span style="display:block; font-size:13px; margin-top:2px;">Deficit: <b style="color:#ef4444;">${case_doc.negative_qty} Units</b></span>
            </div>

            <div style="margin-bottom: 20px;">
                <span style="font-size: 12px; text-transform: uppercase; color: #64748b; font-weight:600; display:block; margin-bottom:4px;">Explainability & Trace Log</span>
                <div class="smriti-explain-markdown">${case_doc.explanation || 'No trace log generated.'}</div>
            </div>
        `);

        $("#ns-drawer").addClass("open");
        $("#ns-drawer-backdrop").addClass("open");
    };

    wrapper.close_drawer = function() {
        $("#ns-drawer").removeClass("open");
        $("#ns-drawer-backdrop").removeClass("open");
    };

    wrapper.page_render();
};
