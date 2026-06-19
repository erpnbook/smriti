/**
 * @file: smriti_retail_os/public/js/smriti_explain.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
// SMRITI Universal Explain Engine JS Client
// Copyright (c) 2026, SMRITI Retail OS and contributors

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
})();
