frappe.pages['smriti-udne'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Universal Numbering Engine Settings',
        single_column: true
    });
    
    var currentTimespan = "Today";
    
    wrapper.page_render = function() {
        wrapper.innerHTML = `
            <div class="smriti-udne-container">
                <div class="smriti-udne-header">
                    <h2>👤 SMRITI Universal Document Numbering Engine (UDNE)</h2>
                    <span style="font-size: 14px; color: #64748b;">Version: 1.0.0 GA</span>
                </div>
                
                <!-- Metrics Section -->
                <div class="smriti-card" style="margin-bottom: 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3 style="margin: 0;">📊 Operational Performance & Auditing</h3>
                        <div style="display: flex; gap: 8px;">
                            <select class="smriti-form-control" id="metrics-timespan-select" style="width: auto; padding: 6px 12px;">
                                <option value="Today">Today</option>
                                <option value="Last 7 Days">Last 7 Days</option>
                                <option value="Lifetime">Lifetime</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="smriti-metrics-grid">
                        <div class="smriti-metric-card">
                            <div class="smriti-metric-val" id="metric-total-gen">-</div>
                            <div class="smriti-metric-label">Allocations</div>
                        </div>
                        <div class="smriti-metric-card">
                            <div class="smriti-metric-val" id="metric-latency">-</div>
                            <div class="smriti-metric-label">Avg Latency</div>
                        </div>
                        <div class="smriti-metric-card">
                            <div class="smriti-metric-val" id="metric-p95">-</div>
                            <div class="smriti-metric-label">P95 Latency</div>
                        </div>
                        <div class="smriti-metric-card">
                            <div class="smriti-metric-val" id="metric-health-score">-</div>
                            <div class="smriti-metric-label">Explain Score</div>
                        </div>
                        <div class="smriti-metric-card">
                            <div class="smriti-metric-val" id="metric-gaps-count" style="color: #ef4444;">-</div>
                            <div class="smriti-metric-label">Unexplained Gaps</div>
                        </div>
                    </div>
                    
                    <!-- Explain Tracer search bar -->
                    <div style="border-top: 1px solid #e2e8f0; padding-top: 16px; display: flex; gap: 12px; align-items: center;">
                        <span style="font-weight: 600; color: #1A2B5C; font-size: 14px;">🔍 Explain Number Tracer:</span>
                        <input type="text" class="smriti-form-control" id="explain-tracer-input" placeholder="Enter display number or document PK (e.g. MUM/FY26/INV/000001)" style="flex: 1;">
                        <button class="smriti-btn smriti-btn-primary" id="explain-tracer-btn">Trace Decision</button>
                    </div>
                </div>
                
                <div class="smriti-grid">
                    <!-- Column 1: Config & Live Preview -->
                    <div class="smriti-card">
                        <h3>🔧 Configure Numbering Rule</h3>
                        
                        <form id="smriti-rule-form">
                            <input type="hidden" id="rule-name" value="">
                            
                            <div class="smriti-form-group">
                                <label for="document-type">Target DocType</label>
                                <select class="smriti-form-control" id="document-type" required>
                                    <option value="POS Invoice">POS Invoice</option>
                                    <option value="Sales Invoice">Sales Invoice</option>
                                    <option value="Stock Entry">Stock Entry</option>
                                    <option value="Purchase Receipt">Purchase Receipt</option>
                                </select>
                            </div>
                            
                            <div class="smriti-form-group">
                                <label for="rule-priority">Priority Scope</label>
                                <select class="smriti-form-control" id="rule-priority">
                                    <option value="Global">Global Default</option>
                                    <option value="Company">Company Override</option>
                                    <option value="Branch">Branch Override</option>
                                    <option value="Store">Store Override</option>
                                </select>
                            </div>
                            
                            <div class="smriti-form-group">
                                <label for="priority-value">Priority Value (Store/Branch/Company ID)</label>
                                <input type="text" class="smriti-form-control" id="priority-value" placeholder="e.g. MUMBAI">
                            </div>
                            
                            <div class="smriti-form-group">
                                <label for="rule-template">Numbering Template</label>
                                <input type="text" class="smriti-form-control" id="rule-template" value="{branch}/FY{fy}/INV/{counter:6}" required>
                                <small style="color: #64748b;">Supported tokens: {company}, {branch}, {store}, {state}, {fy}, {month}, {year}, {terminal}, {user}, {counter:padding}</small>
                            </div>
                            
                            <div class="smriti-form-group">
                                <label for="reset-rule">Reset Counter Scope</label>
                                <select class="smriti-form-control" id="reset-rule">
                                    <option value="Never">Never Reset</option>
                                    <option value="Financial Year">Financial Year Reset</option>
                                    <option value="Yearly">Calendar Year Reset</option>
                                    <option value="Monthly">Monthly Reset</option>
                                    <option value="Daily">Daily Reset</option>
                                    <option value="Store">Store Reset</option>
                                    <option value="Terminal">Terminal Reset</option>
                                </select>
                            </div>
                            
                            <div class="smriti-form-group">
                                <label><input type="checkbox" id="manual-override" value="1"> Allow Cashier Manual Override (PIN Auth Required)</label>
                            </div>
                            
                            <button type="submit" class="smriti-btn smriti-btn-primary">Save Numbering Rule</button>
                            <button type="button" class="smriti-btn smriti-btn-secondary" id="reset-form-btn">Clear Form</button>
                        </form>
                        
                        <h4 style="margin-top: 24px; color: #1A2B5C;">ⓘ Live Preview (Backend Resolved)</h4>
                        <div class="smriti-preview-box">
                            <span id="rendered-preview-output">MUM/FY26/INV/000001</span>
                            <span style="font-size: 11px; color: #a5f3fc; border: 1px solid #0891b2; padding: 2px 6px; border-radius: 4px;">GA PREVIEW</span>
                        </div>
                    </div>
                    
                    <!-- Column 2: Audit Logs, Gap Scanner & Reservations -->
                    <div>
                        <div class="smriti-card">
                            <h3>🔍 Sequence Gap Scanner</h3>
                            <div class="smriti-form-group">
                                <label for="scan-doctype">Select DocType to Audit</label>
                                <select class="smriti-form-control" id="scan-doctype">
                                    <option value="POS Invoice">POS Invoice</option>
                                    <option value="Sales Invoice">Sales Invoice</option>
                                </select>
                            </div>
                            <button class="smriti-btn smriti-btn-primary" id="run-scanner-btn">Run Sequence Audit</button>
                            
                            <div style="margin-top: 16px; max-height: 200px; overflow-y: auto;">
                                <table class="smriti-table">
                                    <thead>
                                        <tr>
                                            <th>Hole Sequence</th>
                                            <th>Classification</th>
                                            <th>Details</th>
                                        </tr>
                                    </thead>
                                    <tbody id="gap-scanner-tbody">
                                        <tr>
                                            <td colspan="3" style="text-align: center; color: #64748b;">No audit run yet.</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div class="smriti-card">
                            <h3>📱 Active Terminal Range Reservations</h3>
                            <div style="max-height: 200px; overflow-y: auto;">
                                <table class="smriti-table">
                                    <thead>
                                        <tr>
                                            <th>Terminal</th>
                                            <th>Range Allocated</th>
                                            <th>Utilization</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody id="reservations-tbody">
                                        <tr>
                                            <td colspan="4" style="text-align: center; color: #64748b;">No active reservations found.</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Active Rules List -->
                <div class="smriti-card" style="margin-top: 24px;">
                    <h3>📋 Registered Numbering Rules</h3>
                    <div style="overflow-x: auto;">
                        <table class="smriti-table">
                            <thead>
                                <tr>
                                    <th>DocType</th>
                                    <th>Priority</th>
                                    <th>Priority Value</th>
                                    <th>Template</th>
                                    <th>Version</th>
                                    <th>Reset</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="rules-list-tbody">
                                <tr>
                                    <td colspan="7" style="text-align: center; color: #64748b;">Loading rules...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        setupEvents();
        refreshDashboardData();
    };
    
    function setupEvents() {
        wrapper.querySelector('#smriti-rule-form').addEventListener('submit', function(e) {
            e.preventDefault();
            saveRule();
        });
        
        wrapper.querySelector('#reset-form-btn').addEventListener('click', function() {
            clearForm();
        });
        
        ['#rule-template', '#document-type', '#rule-priority', '#priority-value', '#reset-rule'].forEach(function(selector) {
            wrapper.querySelector(selector).addEventListener('input', triggerPreview);
            wrapper.querySelector(selector).addEventListener('change', triggerPreview);
        });
        
        wrapper.querySelector('#run-scanner-btn').addEventListener('click', runScanner);
        
        wrapper.querySelector('#metrics-timespan-select').addEventListener('change', function() {
            currentTimespan = this.value;
            loadMetrics();
        });
        
        wrapper.querySelector('#explain-tracer-btn').addEventListener('click', triggerTracer);
    }
    
    function refreshDashboardData() {
        loadMetrics();
        loadRules();
        loadReservations();
        triggerPreview();
    }
    
    function loadMetrics() {
        frappe.call({
            method: "smriti_retail_os.api.udne_api.get_dashboard_metrics",
            args: { timespan: currentTimespan },
            callback: function(r) {
                if (r.message && r.message.success) {
                    const m = r.message.metrics;
                    const h = r.message.health;
                    
                    wrapper.querySelector('#metric-total-gen').textContent = m.total_generations;
                    wrapper.querySelector('#metric-latency').textContent = m.average_latency_ms + " ms";
                    wrapper.querySelector('#metric-p95').textContent = m.p95_latency_ms + " ms";
                    wrapper.querySelector('#metric-health-score').textContent = h.explainability_score + "%";
                    wrapper.querySelector('#metric-gaps-count').textContent = m.unexplained_gaps;
                    
                    if (m.unexplained_gaps === 0) {
                        wrapper.querySelector('#metric-gaps-count').style.color = "#166534";
                    } else {
                        wrapper.querySelector('#metric-gaps-count').style.color = "#ef4444";
                    }
                }
            }
        });
    }
    
    function triggerTracer() {
        const inputVal = wrapper.querySelector('#explain-tracer-input').value.trim();
        if (!inputVal) {
            frappe.show_alert({message: __("Please enter a sequence number or identifier to trace."), indicator: "orange"});
            return;
        }
        
        frappe.call({
            method: "smriti_retail_os.api.udne_api.explain_doc",
            args: { doc_name: inputVal },
            callback: function(r) {
                if (r.message && r.message.success) {
                    const res = r.message;
                    const d = new frappe.ui.Dialog({
                        title: `Explain Number: ${res.evidence.generated_number}`,
                        size: 'large',
                        fields: [
                            {
                                fieldtype: 'HTML',
                                fieldname: 'explain_html',
                                html: `
                                    <div class="smriti-explain-container">
                                        <div class="smriti-explain-header">
                                            <span class="smriti-confidence-badge">Confidence: ${res.confidence}%</span>
                                            <h4 style="margin: 0 0 8px 0; color: #1A2B5C;">Decision Summary</h4>
                                            <p style="margin: 0; font-size: 14px; color: #334155;">${res.summary}</p>
                                        </div>
                                        
                                        <h4 style="color: #1A2B5C; margin-bottom: 8px;">Execution Timeline</h4>
                                        <div class="smriti-timeline">
                                            ${res.timeline.map(step => `
                                                <div class="smriti-timeline-item">${step}</div>
                                            `).join('')}
                                        </div>
                                        
                                        <h4 style="color: #1A2B5C; margin-top: 24px; margin-bottom: 8px;">Audit Evidence Payload</h4>
                                        <pre class="smriti-explain-evidence">${JSON.stringify(res.evidence, null, 2)}</pre>
                                    </div>
                                `
                            }
                        ]
                    });
                    d.show();
                } else {
                    frappe.msgprint({
                        title: __('Trace Failed'),
                        indicator: 'orange',
                        message: r.message ? r.message.error : __('Trace search returned no records.')
                    });
                }
            }
        });
    }
    
    function triggerPreview() {
        const template = wrapper.querySelector('#rule-template').value;
        const priorityVal = wrapper.querySelector('#priority-value').value || "MUMBAI";
        
        const mockContext = {
            company: "SMRITI Retail Ltd",
            branch: priorityVal,
            store: priorityVal,
            terminal: "POS-01",
            user: "Jawahar",
            fy: "26-27",
            month: "06",
            year: "2026",
            state: "MH",
            channel: "POS"
        };
        
        frappe.call({
            method: "smriti_retail_os.api.udne_api.preview_number",
            args: {
                template: template,
                context_json: JSON.stringify(mockContext),
                counter_val: 1
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    wrapper.querySelector('#rendered-preview-output').textContent = r.message.preview;
                    wrapper.querySelector('#rendered-preview-output').style.color = "#38bdf8";
                } else {
                    wrapper.querySelector('#rendered-preview-output').textContent = r.message ? r.message.error : "Validation error";
                    wrapper.querySelector('#rendered-preview-output').style.color = "#ef4444";
                }
            }
        });
    }
    
    function saveRule() {
        const ruleData = {
            name: wrapper.querySelector('#rule-name').value || undefined,
            document_type: wrapper.querySelector('#document-type').value,
            priority: wrapper.querySelector('#rule-priority').value,
            priority_value: wrapper.querySelector('#priority-value').value || undefined,
            template: wrapper.querySelector('#rule-template').value,
            reset_rule: wrapper.querySelector('#reset-rule').value,
            allow_manual_override: wrapper.querySelector('#manual-override').checked ? 1 : 0,
            is_active: 1
        };
        
        frappe.call({
            method: "smriti_retail_os.api.udne_api.save_rule",
            args: {
                doc_data: JSON.stringify(ruleData)
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({message: __("Numbering rule saved successfully!"), indicator: "green"});
                    clearForm();
                    refreshDashboardData();
                } else {
                    frappe.msgprint({
                        title: __('Error Saving'),
                        indicator: 'red',
                        message: r.message ? r.message.error : __('Unknown validation error')
                    });
                }
            }
        });
    }
    
    function clearForm() {
        wrapper.querySelector('#rule-name').value = "";
        wrapper.querySelector('#document-type').value = "POS Invoice";
        wrapper.querySelector('#rule-priority').value = "Global";
        wrapper.querySelector('#priority-value').value = "";
        wrapper.querySelector('#rule-template').value = "{branch}/FY{fy}/INV/{counter:6}";
        wrapper.querySelector('#reset-rule').value = "Never";
        wrapper.querySelector('#manual-override').checked = false;
        triggerPreview();
    }
    
    function loadRules() {
        frappe.call({
            method: "smriti_retail_os.api.udne_api.get_rules",
            callback: function(r) {
                const tbody = wrapper.querySelector('#rules-list-tbody');
                if (r.message && r.message.length) {
                    tbody.innerHTML = r.message.map(function(row) {
                        return `
                            <tr>
                                <td><strong>${row.document_type}</strong></td>
                                <td>${row.priority}</td>
                                <td>${row.priority_value || '-'}</td>
                                <td><code>${row.template}</code></td>
                                <td><span class="smriti-badge smriti-badge-active">v${row.version}</span></td>
                                <td>${row.reset_rule}</td>
                                <td>
                                    <button class="btn btn-xs btn-default edit-rule-btn" data-rule='${JSON.stringify(row)}'>Edit</button>
                                </td>
                            </tr>
                        `;
                    }).join('');
                    
                    tbody.querySelectorAll('.edit-rule-btn').forEach(function(btn) {
                        btn.addEventListener('click', function() {
                            const data = JSON.parse(this.getAttribute('data-rule'));
                            wrapper.querySelector('#rule-name').value = data.name;
                            wrapper.querySelector('#document-type').value = data.document_type;
                            wrapper.querySelector('#rule-priority').value = data.priority;
                            wrapper.querySelector('#priority-value').value = data.priority_value || "";
                            wrapper.querySelector('#rule-template').value = data.template;
                            wrapper.querySelector('#reset-rule').value = data.reset_rule;
                            wrapper.querySelector('#manual-override').checked = data.allow_manual_override === 1;
                            triggerPreview();
                        });
                    });
                } else {
                    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #64748b;">No rules configured yet.</td></tr>`;
                }
            }
        });
    }
    
    function loadReservations() {
        frappe.call({
            method: "smriti_retail_os.api.udne_api.get_dashboard_metrics",
            args: { timespan: currentTimespan },
            callback: function(r) {
                const tbody = wrapper.querySelector('#reservations-tbody');
                if (r.message && r.message.success && r.message.reservations && r.message.reservations.length) {
                    tbody.innerHTML = r.message.reservations.map(function(row) {
                        const statusClass = row.status.toLowerCase();
                        return `
                            <tr>
                                <td><code>${row.terminal_id}</code></td>
                                <td>
                                    ${row.start} - ${row.end}
                                    <div class="smriti-progress-bar">
                                        <div class="smriti-progress-fill" style="width: ${row.utilization}%"></div>
                                    </div>
                                </td>
                                <td><strong>${row.utilization}%</strong> (${row.current - row.start}/${row.end - row.start + 1})</td>
                                <td><span class="smriti-badge smriti-badge-${statusClass}">${row.status}</span></td>
                            </tr>
                        `;
                    }).join('');
                } else {
                    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #64748b;">No reservations found.</td></tr>`;
                }
            }
        });
    }
    
    function runScanner() {
        const doctype = wrapper.querySelector('#scan-doctype').value;
        frappe.call({
            method: "smriti_retail_os.api.udne_api.get_rules",
            callback: function(rulesRes) {
                const rules = rulesRes.message || [];
                const rule = rules.find(r => r.document_type === doctype && r.is_active === 1);
                if (!rule) {
                    frappe.msgprint({
                        title: __('Audit Error'),
                        indicator: 'orange',
                        message: __('No active numbering rule exists for this DocType to perform sequence verification.')
                    });
                    return;
                }
                
                frappe.call({
                    method: "smriti_retail_os.api.udne_api.scan_sequence_gaps",
                    args: {
                        doctype: doctype,
                        rule_name: rule.name
                    },
                    callback: function(r) {
                        const tbody = wrapper.querySelector('#gap-scanner-tbody');
                        if (r.message && r.message.success) {
                            const gaps = r.message.gaps || [];
                            if (gaps.length) {
                                tbody.innerHTML = gaps.map(function(gap) {
                                    const badgeClass = gap.status.toLowerCase();
                                    return `
                                        <tr>
                                            <td><code>#${gap.number}</code></td>
                                            <td><span class="smriti-badge smriti-badge-${badgeClass}">${gap.status}</span></td>
                                            <td>${gap.explanation}</td>
                                        </tr>
                                    `;
                                }).join('');
                            } else {
                                tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: #166534; background-color: #dcfce7; font-weight: 600;">✅ Audit Clean: No sequence gaps detected!</td></tr>`;
                            }
                        } else {
                            tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: #ef4444;">Error running audit.</td></tr>`;
                        }
                    }
                });
            }
        });
    }
    
    wrapper.page_render();
};

