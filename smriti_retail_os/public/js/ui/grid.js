/**
 * @file:    public/js/ui/grid.js
 * @desc:    SMRITI Grid Component - Handles list displays, formatting, and actions.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.Grid = class {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`SMRITI Grid: Container #${containerId} not found.`);
            return;
        }
        this.columns = options.columns || [];
        this.dataSource = options.dataSource || null;
        this.actions = options.actions || [];
        this.onRowClick = options.onRowClick || null;
        this.data = [];
        this.init();
    }

    init() {
        this.container.innerHTML = `
            <div class="smriti-grid-wrapper">
                <table class="smriti-table">
                    <thead>
                        <tr id="grid-header-row"></tr>
                    </thead>
                    <tbody id="grid-tbody">
                        <tr><td colspan="${this.columns.length + (this.actions.length ? 1 : 0)}" style="text-align:center; padding:40px 0;">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        `;
        this.renderHeaders();
        this.refresh();
    }

    renderHeaders() {
        const headerRow = this.container.querySelector("#grid-header-row");
        let html = this.columns.map(col => `
            <th style="width: ${col.width || 'auto'}; text-align: ${col.align || 'left'};">
                ${col.label}
            </th>
        `).join('');

        if (this.actions.length) {
            html += `<th style="width: 100px; text-align: center;">Actions</th>`;
        }
        headerRow.innerHTML = html;
    }

    async refresh() {
        const tbody = this.container.querySelector("#grid-tbody");
        if (!this.dataSource) return;

        try {
            tbody.innerHTML = `<tr><td colspan="${this.columns.length + (this.actions.length ? 1 : 0)}" style="text-align:center; padding:40px 0;"><div class="loading-spinner"></div> Loading records...</td></tr>`;
            
            this.data = await this.dataSource();
            this.renderRows();
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="${this.columns.length + (this.actions.length ? 1 : 0)}" style="text-align:center; padding:40px 0; color:var(--smriti-color-brand-light);">Error: ${e.message}</td></tr>`;
            SMRITI.toast.error("Failed to load grid: " + e.message);
        }
    }

    renderRows() {
        const tbody = this.container.querySelector("#grid-tbody");
        if (!this.data || !this.data.length) {
            tbody.innerHTML = `<tr><td colspan="${this.columns.length + (this.actions.length ? 1 : 0)}" style="text-align:center; padding:40px 0; color:var(--text-muted);">No records found.</td></tr>`;
            return;
        }

        tbody.innerHTML = this.data.map((row, rowIndex) => {
            let rowHtml = `<tr class="grid-row" data-index="${rowIndex}">`;
            
            this.columns.forEach(col => {
                let val = row[col.field] === undefined || row[col.field] === null ? "" : row[col.field];
                if (col.formatter === "currency") {
                    val = `Rs. ${parseFloat(val || 0).toFixed(2)}`;
                } else if (col.formatter === "percent") {
                    val = `${val}%`;
                }
                
                let style = `text-align: ${col.align || 'left'};`;
                if (col.bold) style += " font-weight: 600; color: var(--text);";
                rowHtml += `<td style="${style}">${val}</td>`;
            });

            if (this.actions.length) {
                rowHtml += `<td style="text-align:center; display:flex; justify-content:center; gap:8px;">`;
                this.actions.forEach(act => {
                    rowHtml += `
                        <button class="grid-action-btn" data-action="${act.id}" data-index="${rowIndex}" title="${act.label}">
                            <span class="material-symbols-outlined" style="font-size:16px;">${act.icon}</span>
                        </button>
                    `;
                });
                rowHtml += `</td>`;
            }

            rowHtml += `</tr>`;
            return rowHtml;
        }).join('');

        // Attach listeners
        tbody.querySelectorAll(".grid-row").forEach(tr => {
            tr.addEventListener("click", (e) => {
                // If clicked an action button, bypass rowClick
                if (e.target.closest(".grid-action-btn")) return;
                
                const idx = tr.getAttribute("data-index");
                if (this.onRowClick) this.onRowClick(this.data[idx]);
            });
        });

        tbody.querySelectorAll(".grid-action-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const actionId = btn.getAttribute("data-action");
                const idx = btn.getAttribute("data-index");
                const act = this.actions.find(a => a.id === actionId);
                if (act && typeof act.callback === "function") {
                    act.callback(this.data[idx]);
                }
            });
        });
    }

    setData(newData) {
        this.data = newData;
        this.renderRows();
    }
};
