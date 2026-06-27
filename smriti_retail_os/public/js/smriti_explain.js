/**
 * @file: smriti_retail_os/public/js/smriti_explain.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
(function () {
    const templates = {
        "INV-001": "{total_sales_qty} ÷ {lookback_days} × 7 = {result} pieces/week",
        "INV-002": "{current_stock} ÷ {weekly_velocity} = {result} weeks",
        "INV-003": "max(0, 100 - ({active_days_since_last_sale} × (100 ÷ {max_inactive_days_allowed}))) = {result} score",
        "FRC-001": "max(0, 100 - ({coefficient_of_variation} × 100)) = {result}% confidence",
        "OHS-001": "100 - ({sync_delay_hours} × 0.5) - ({variance_percentage} × 5) = {result} score",
        "TRF-001": "Rs {sales_retaining_value} - Rs {freight_cost} - Rs {origin_stockout_risk_penalty} = Rs {result} benefit",
        "SAL-001": "({total_sales_qty} ÷ ({opening_stock} + {received_stock})) × 100 = {result}%",
        "AUD-001": "(1 - (abs({physical_qty} - {ledger_qty}) ÷ {ledger_qty})) × 100 = {result}% accuracy",
        "INV-004": "Rs {annual_sales_cost} ÷ Rs {average_inventory_value} = {result} times",
        "VAR-001": "({active_available_sizes} ÷ {total_sizes_in_curve}) × 100 = {result}% curve health",
        "KGF-001": "({registered_kpis} ÷ {total_kpis}) × 100 = {result}% compliance"
    };

    window.smritiExplain = function (formulaId, liveInputs = null) {
        if (!formulaId) return;

        // Fetch payload from API
        frappe.call({
            method: "smriti_retail_os.api.explain_api.get_explain_payload",
            args: { formula_id: formulaId },
            callback: function (r) {
                if (r.message) {
                    renderExplainModal(r.message, liveInputs);
                }
            }
        });
    };

    function renderExplainModal(data, liveInputs) {
        // Ensure Modal container exists
        let overlay = document.getElementById("smriti-explain-overlay");
        let modal = document.getElementById("smriti-explain-modal");

        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "smriti-explain-overlay";
            overlay.className = "smriti-explain-overlay";
            overlay.onclick = closeExplainModal;
            document.body.appendChild(overlay);
        }

        if (!modal) {
            modal = document.createElement("div");
            modal.id = "smriti-explain-modal";
            modal.className = "smriti-explain-modal";
            document.body.appendChild(modal);
        }

        // Generate Live worked example if provided
        let liveExampleHtml = "";
        if (liveInputs && templates[data.formula_id]) {
            let templateStr = templates[data.formula_id];
            for (let key in liveInputs) {
                templateStr = templateStr.replace(`{${key}}`, liveInputs[key]);
            }
            if (liveInputs.result !== undefined) {
                templateStr = templateStr.replace("{result}", liveInputs.result);
            }

            let varList = [];
            for (let key in liveInputs) {
                if (key !== "result") {
                    varList.push(`
                        <div style="display:flex; justify-content:space-between; font-size:12px; color:#475569; border-bottom:1px dashed #E2E8F0; padding:4px 0;">
                            <span style="font-family:monospace; font-weight:700;">${key}</span>
                            <span>${liveInputs[key]}</span>
                        </div>
                    `);
                }
            }
            let variablesBreakdown = "";
            if (varList.length > 0) {
                variablesBreakdown = `
                    <div style="margin-top: 10px; background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #E2E8F0;">
                        <p style="font-size:11px; font-weight:800; color:#475569; text-transform:uppercase; margin-bottom:6px; letter-spacing:0.5px;">Input Variables Mapping</p>
                        ${varList.join("")}
                    </div>
                `;
            }

            liveExampleHtml = `
                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Live Worked Calculation</span>
                    <div class="smriti-explain-live-box">
                        <div style="font-size:14px; font-weight:700;">${templateStr}</div>
                        ${variablesBreakdown}
                    </div>
                </div>
            `;
        }

        // Build Related Formulas
        let relatedHtml = "";
        if (data.related_formula_ids && data.related_formula_ids.length > 0) {
            relatedHtml = `
                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Related KGF Metrics</span>
                    <div class="smriti-explain-tags">
                        ${data.related_formula_ids.map(fid => `
                            <span class="smriti-explain-tag" onclick="closeExplainModal(); setTimeout(() => window.smritiExplain('${fid}', ${liveInputs ? JSON.stringify(liveInputs) : null}), 200)">
                                ${fid}
                            </span>
                        `).join("")}
                    </div>
                </div>
            `;
        }

        // Build Dependent list
        let deps = data.dependent_features || [];
        let depsText = Array.isArray(deps) ? deps.join(", ") : deps;

        // Build JSON extra fields
        let trainingLesson = data.explainability_json?.related_training_lesson || "TRN-" + data.formula_id;
        let manualSection = data.explainability_json?.related_manual_section || "Volume 3 > SMRITI Governance";
        let dictTerm = data.explainability_json?.related_dictionary_term || data.formula_name;

        modal.innerHTML = `
            <div class="smriti-explain-header">
                <div>
                    <span class="smriti-explain-id">${data.formula_id}</span>
                    <h3 class="smriti-explain-title">${data.formula_name}</h3>
                </div>
                <button class="smriti-explain-close" onclick="closeExplainModal()">✕</button>
            </div>
            <div class="smriti-explain-body">
                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Business Meaning (Hinglish/English)</span>
                    <div class="smriti-explain-text-box">
                        ${data.business_meaning}
                    </div>
                </div>

                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Documentation Formula</span>
                    <div class="smriti-explain-code-box">
                        <code id="smriti-explain-copy-target">${data.formula_expression}</code>
                        <button class="smriti-explain-btn-copy" onclick="copyFormulaToClipboard()">📋 Copy</button>
                    </div>
                </div>

                ${liveExampleHtml}

                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Standard Registry Worked Example</span>
                    <div class="smriti-explain-example-box">
                        ${data.worked_example}
                    </div>
                </div>

                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Interpretation & Next Steps</span>
                    <div class="smriti-explain-action-box">
                        <p style="font-weight:700; color:#1A2B5C; margin-bottom:6px;">Evaluation Bands:</p>
                        <p style="margin-bottom:10px; color:#475569;">${data.interpretation_guide}</p>
                        <p style="font-weight:700; color:#2563EB; margin-bottom:6px;">Recommended Action:</p>
                        <p style="color:#475569;">${data.recommended_action}</p>
                    </div>
                </div>

                ${relatedHtml}

                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Learn More & Documentation</span>
                    <div class="smriti-explain-learn-buttons">
                        <button class="smriti-explain-btn-learn" onclick="smritiExplainGoTo('manual', ${JSON.stringify(manualSection).replace(/"/g, '&quot;')})">📘 Read Manual</button>
                        <button class="smriti-explain-btn-learn" onclick="smritiExplainGoTo('training', ${JSON.stringify(trainingLesson).replace(/"/g, '&quot;')})">🎓 Training Lesson</button>
                        <button class="smriti-explain-btn-learn" onclick="smritiExplainGoTo('dictionary', ${JSON.stringify(dictTerm).replace(/"/g, '&quot;')})">📖 Dictionary Entry</button>
                    </div>
                </div>

                <div class="smriti-explain-section">
                    <span class="smriti-explain-section-title">Audit Governance Metadata</span>
                    <div class="smriti-explain-grid">
                        <div>
                            <span class="smriti-explain-label">Code Reference</span>
                            <span class="smriti-explain-val" style="font-family: monospace; font-size:11px; word-break:break-all;">${data.implementation_reference || "N/A"}</span>
                        </div>
                        <div>
                            <span class="smriti-explain-label">Version</span>
                            <span class="smriti-explain-val">v${data.formula_version}</span>
                        </div>
                        <div>
                            <span class="smriti-explain-label">Business Owner</span>
                            <span class="smriti-explain-val">${data.business_owner || "Jawahar R. Mallah"}</span>
                        </div>
                        <div>
                            <span class="smriti-explain-label">Dependent Features</span>
                            <span class="smriti-explain-val">${depsText}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        overlay.classList.add("open");
        modal.classList.add("open");
    }

    window.closeExplainModal = function () {
        const overlay = document.getElementById("smriti-explain-overlay");
        const modal = document.getElementById("smriti-explain-modal");
        if (overlay) overlay.classList.remove("open");
        if (modal) modal.classList.remove("open");
    };

    window.smritiExplainGoTo = function (type, val) {
        closeExplainModal();
        if (type === "dictionary") {
            window.location.href = `/smriti-dictionary?term=${encodeURIComponent(val)}`;
        } else {
            let prefix = type === "manual" ? "Manual Reference" : "Training Lesson";
            window.location.href = `/smriti-coming-soon?feature=${encodeURIComponent(prefix + ": " + val)}&back=/app/smriti-formula-registry`;
        }
    };

    window.copyFormulaToClipboard = function () {
        const codeElement = document.getElementById("smriti-explain-copy-target");
        if (codeElement) {
            navigator.clipboard.writeText(codeElement.innerText).then(() => {
                alert("Formula expression copied to clipboard!");
            });
        }
    };

    window.smritiExplainCurrent = function () {
        const pathname = window.location.pathname;
        frappe.call({
            method: "smriti_retail_os.api.knowledge_studio_api.explain_screen_by_route",
            args: { route_path: pathname },
            callback: function (r) {
                if (r.message && r.message.found) {
                    renderScreenExplainModal(r.message);
                } else {
                    alert(r.message ? r.message.message : "No verified screen guide found for this page.");
                }
            }
        });
    };

    function renderScreenExplainModal(data) {
        let overlay = document.getElementById("smriti-explain-overlay");
        let modal = document.getElementById("smriti-explain-modal");

        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "smriti-explain-overlay";
            overlay.className = "smriti-explain-overlay";
            overlay.onclick = closeExplainModal;
            document.body.appendChild(overlay);
        }

        if (!modal) {
            modal = document.createElement("div");
            modal.id = "smriti-explain-modal";
            modal.className = "smriti-explain-modal";
            document.body.appendChild(modal);
        }

        const beg = data.beginner || {};
        const power = data.power_user || {};
        const dev = data.developer || {};
        
        const beginnerHtml = `
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Business Purpose</span>
                <div class="smriti-explain-text-box">${beg.purpose || 'N/A'}</div>
            </div>
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">How to Use</span>
                <div class="smriti-explain-text-box">${beg.how_to_use || 'N/A'}</div>
            </div>
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Practical Example</span>
                <div class="smriti-explain-example-box">${beg.example || 'N/A'}</div>
            </div>
        `;

        const powerHtml = `
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Validation Checks</span>
                <div class="smriti-explain-text-box" style="border-left-color: #8B5CF6; background: #FAF5FF;">${power.validation || 'N/A'}</div>
            </div>
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Workflow Pipeline</span>
                <div class="smriti-explain-text-box">${power.workflow || 'N/A'}</div>
            </div>
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Core Schema Fields</span>
                <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:6px;">
                    ${data.fields.map(f => `<span class="smriti-explain-tag" style="cursor:default;">${f}</span>`).join('')}
                </div>
            </div>
        `;

        const devHtml = `
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">DocType Schema</span>
                <div class="smriti-explain-text-box" style="font-family:monospace; font-size:12px;">${data.doctype || 'N/A'}</div>
            </div>
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Bound whitelisted APIs</span>
                <div style="display:flex; flex-direction:column; gap:4px;">
                    ${data.apis.map(api => `<div class="smriti-explain-live-box" style="font-size:11px; padding:8px 12px; margin:0;">${api}</div>`).join('')}
                </div>
            </div>
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Consuming Reports</span>
                <div class="smriti-explain-text-box">${data.reports.join(', ') || 'None'}</div>
            </div>
            <div class="smriti-explain-section">
                <span class="smriti-explain-section-title">Reference Manual</span>
                <div class="smriti-explain-text-box" style="border-left-color: #10b981; background: #F0FDF4;">${dev.manual_reference || 'N/A'}</div>
            </div>
        `;

        modal.innerHTML = `
            <div class="smriti-explain-header">
                <div>
                    <span class="smriti-explain-id">SCREEN GUIDE</span>
                    <h3 class="smriti-explain-title">${data.title}</h3>
                </div>
                <button class="smriti-explain-close" onclick="closeExplainModal()">✕</button>
            </div>
            
            <div style="display:flex; background:#F1F5F9; border-bottom:1px solid #E2E8F0; padding:4px 8px; gap:8px;">
                <button class="smriti-screen-tab active" data-level="beginner" style="flex:1; border:none; background:transparent; padding:8px 12px; font-weight:700; color:#475569; border-radius:6px; cursor:pointer;">Beginner</button>
                <button class="smriti-screen-tab" data-level="power" style="flex:1; border:none; background:transparent; padding:8px 12px; font-weight:700; color:#475569; border-radius:6px; cursor:pointer;">Power User</button>
                <button class="smriti-screen-tab" data-level="developer" style="flex:1; border:none; background:transparent; padding:8px 12px; font-weight:700; color:#475569; border-radius:6px; cursor:pointer;">Developer</button>
            </div>

            <div class="smriti-explain-body" style="padding:20px 28px;">
                <div class="smriti-screen-panel active" id="scr-panel-beginner">${beginnerHtml}</div>
                <div class="smriti-screen-panel" id="scr-panel-power" style="display:none;">${powerHtml}</div>
                <div class="smriti-screen-panel" id="scr-panel-developer" style="display:none;">${devHtml}</div>
            </div>
        `;

        const styleSheet = document.createElement("style");
        styleSheet.id = "smriti-screen-tabs-style";
        styleSheet.innerText = `
            .smriti-screen-tab.active {
                background: #fff !important;
                color: #2563EB !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
        `;
        if (!document.getElementById("smriti-screen-tabs-style")) {
            document.head.appendChild(styleSheet);
        }

        $(modal).find(".smriti-screen-tab").on("click", function() {
            $(modal).find(".smriti-screen-tab").removeClass("active");
            $(this).addClass("active");
            const level = $(this).attr("data-level");
            $(modal).find(".smriti-screen-panel").hide();
            $(modal).find("#scr-panel-" + level).show();
        });

        overlay.classList.add("open");
        modal.classList.add("open");
    }

    window.smritiExplainDoc = function (doctype, docname) {
        if (!docname) return;

        frappe.call({
            method: "smriti_retail_os.api.udne_api.explain_doc",
            args: { doc_name: docname },
            callback: function (r) {
                if (r.message && r.message.success) {
                    renderDocExplainModal(r.message);
                } else {
                    frappe.show_alert({message: __("No explainability audit log trace found for this document."), indicator: 'orange'});
                }
            }
        });
    };

    function renderDocExplainModal(res) {
        let overlay = document.getElementById("smriti-explain-overlay");
        let modal = document.getElementById("smriti-explain-modal");

        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "smriti-explain-overlay";
            overlay.className = "smriti-explain-overlay";
            overlay.onclick = closeExplainModal;
            document.body.appendChild(overlay);
        }

        if (!modal) {
            modal = document.createElement("div");
            modal.id = "smriti-explain-modal";
            modal.className = "smriti-explain-modal";
            document.body.appendChild(modal);
        }

        modal.innerHTML = `
            <div class="smriti-explain-header">
                <div>
                    <span class="smriti-explain-id">${__('DOCUMENT TRACER')}</span>
                    <h3 class="smriti-explain-title">${res.evidence.generated_number}</h3>
                </div>
                <button class="smriti-explain-close" onclick="closeExplainModal()">✕</button>
            </div>
            
            <div class="smriti-explain-body" style="display: flex; flex-direction: column; gap: 16px; padding: 20px 28px;">
                <!-- 1. Summary Card -->
                <div class="smriti-explain-section" style="margin:0;">
                    <span class="smriti-explain-section-title">${__('Summary')}</span>
                    <div class="smriti-explain-text-box" style="border-left-color: #027a48; background: #f0fdf4; color: #166534; font-weight: 500;">
                        ${res.summary}
                    </div>
                </div>

                <!-- 2. Timeline Card -->
                <div class="smriti-explain-section" style="margin:0;">
                    <span class="smriti-explain-section-title">${__('Decision Timeline')}</span>
                    <div class="smriti-explain-live-box" style="margin:0; padding:16px; background:#f8fafc; border:1px solid #e2e8f0;">
                        <div style="position: relative; padding-left: 20px; border-left: 2px solid #cbd5e1;">
                            ${res.timeline.map((step, idx) => `
                                <div style="position: relative; margin-bottom: 10px; font-size: 13px; color: #475569;">
                                    <span style="position: absolute; left: -26px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: #2563eb; border: 2px solid #fff;"></span>
                                    ${step}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- 3. Evidence Card -->
                <div class="smriti-explain-section" style="margin:0;">
                    <span class="smriti-explain-section-title">${__('Audit Evidence Details')}</span>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                        <div class="smriti-explain-live-box" style="margin:0; padding:10px 12px; background:#f8fafc; border:1px solid #e2e8f0;">
                            <span style="font-size:10px; font-weight:700; color:#64748b; text-transform:uppercase;">Applied Rule</span>
                            <div style="font-size:12px; font-weight:600; color:#1e293b; margin-top:2px;">${res.evidence.applied_rule}</div>
                        </div>
                        <div class="smriti-explain-live-box" style="margin:0; padding:10px 12px; background:#f8fafc; border:1px solid #e2e8f0;">
                            <span style="font-size:10px; font-weight:700; color:#64748b; text-transform:uppercase;">Rule Template</span>
                            <div style="font-size:12px; font-weight:600; color:#1e293b; margin-top:2px; font-family:monospace;">${res.evidence.rule_template}</div>
                        </div>
                    </div>
                    <div class="smriti-explain-code-box" style="margin:0;">
                        <pre style="margin:0; font-family:monospace; font-size:11px; white-space:pre-wrap; word-break:break-all; background:none; border:none; padding:0; color:#334155;">${JSON.stringify(res.evidence, null, 2)}</pre>
                    </div>
                </div>

                <!-- 4. Performance Card -->
                <div class="smriti-explain-section" style="margin:0;">
                    <span class="smriti-explain-section-title">${__('Performance Metadata')}</span>
                    <div class="smriti-explain-grid" style="margin-top:0;">
                        <div>
                            <span class="smriti-explain-label">Latency</span>
                            <span class="smriti-explain-val">${res.metrics.latency_ms} ms</span>
                        </div>
                        <div>
                            <span class="smriti-explain-label">Rule Version</span>
                            <span class="smriti-explain-val">v${res.metrics.rule_version}</span>
                        </div>
                        <div>
                            <span class="smriti-explain-label">Explainability</span>
                            <span class="smriti-explain-val" style="color:#027a48; font-weight:700;">${res.confidence}%</span>
                        </div>
                        <div>
                            <span class="smriti-explain-label">Authorized User</span>
                            <span class="smriti-explain-val" style="font-size:11px; word-break:break-all;">${res.evidence.user}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        overlay.classList.add("open");
        modal.classList.add("open");
    }
})();
