/**
 * @file:    public/js/ui/toolbar.js
 * @desc:    SMRITI Toolbar Component - Manages search text input, dropdown filters, and action trigger buttons.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.Toolbar = class {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`SMRITI Toolbar: Container #${containerId} not found.`);
            return;
        }
        this.searchPlaceholder = options.searchPlaceholder || "Search...";
        this.filters = options.filters || [];
        this.actions = options.actions || [];
        this.onChange = options.onChange || null;
        this.init();
    }

    init() {
        let filtersHtml = this.filters.map(f => {
            let optionsHtml = `<option value="">All ${f.label}</option>`;
            if (f.options) {
                optionsHtml += f.options.map(o => `<option value="${o.value}">${o.label}</option>`).join('');
            }
            return `
                <select class="filter-select" id="toolbar-filter-${f.id}">
                    ${optionsHtml}
                </select>
            `;
        }).join('');

        let actionsHtml = this.actions.map(a => `
            <button class="topbtn" id="toolbar-action-${a.id}">
                <span class="material-symbols-outlined">${a.icon}</span> ${a.label}
            </button>
        `).join('');

        this.container.innerHTML = `
            <div class="toolbar-content" style="display:flex; align-items:center; gap:12px; width:100%;">
                <div class="search-wrapper" style="position:relative; flex:1; max-width:320px;">
                    <span class="material-symbols-outlined" style="position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:18px;">search</span>
                    <input type="text" class="search-input" id="toolbar-search" placeholder="${this.searchPlaceholder}" style="padding-left:36px; width:100%;">
                </div>
                <div class="filters-wrapper" style="display:flex; gap:8px; align-items:center;">
                    ${filtersHtml}
                </div>
                <div class="actions-wrapper" style="margin-left:auto; display:flex; gap:8px;">
                    ${actionsHtml}
                </div>
            </div>
        `;

        // Bind events
        const searchInput = this.container.querySelector("#toolbar-search");
        let searchTimeout = null;
        searchInput.addEventListener("input", () => {
            if (searchTimeout) clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => this.triggerChange(), 300);
        });

        this.filters.forEach(f => {
            const select = this.container.querySelector(`#toolbar-filter-${f.id}`);
            if (select) {
                select.addEventListener("change", () => this.triggerChange());
            }
        });

        this.actions.forEach(a => {
            const btn = this.container.querySelector(`#toolbar-action-${a.id}`);
            if (btn && typeof a.callback === "function") {
                btn.addEventListener("click", () => a.callback());
            }
        });
    }

    getValues() {
        const values = {
            search: this.container.querySelector("#toolbar-search").value.trim().toLowerCase()
        };
        this.filters.forEach(f => {
            const select = this.container.querySelector(`#toolbar-filter-${f.id}`);
            if (select) {
                values[f.id] = select.value;
            }
        });
        return values;
    }

    triggerChange() {
        if (this.onChange) {
            this.onChange(this.getValues());
        }
    }
};
