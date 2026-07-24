/**
 * @file: smriti_retail_os/public/js/ui/command_palette.js
 * @description: SMRITI Global Command Palette (Ctrl+K / Cmd+K) Controller
 * @author: SMRITI UI System Team
 */

window.SMRITI = window.SMRITI || {};

(function(SMRITI) {
    "use strict";

    let paletteEl = null;
    let inputEl = null;
    let resultsEl = null;

    const navCommands = [
        { label: "Product Studio Catalog", route: "/products", icon: "inventory_2", category: "Navigation" },
        { label: "Barcode Label Studio", route: "/barcode", icon: "barcode", category: "Navigation" },
        { label: "POS Billing Studio", route: "/billing", icon: "point_of_sale", category: "Navigation" },
        { label: "Inventory & Stock Reconciliation", route: "/inventory", icon: "inventory", category: "Navigation" },
        { label: "Purchase Orders & GRN", route: "/purchase_receipt", icon: "shopping_cart", category: "Navigation" },
        { label: "Sales Invoices & Returns", route: "/sales_invoices", icon: "receipt_long", category: "Navigation" },
        { label: "Analytics & Executive Reports", route: "/analytics", icon: "analytics", category: "Navigation" },
        { label: "Platform Security & Users", route: "/security", icon: "admin_panel_settings", category: "Admin" }
    ];

    function createPaletteDOM() {
        if (paletteEl) return;

        paletteEl = document.createElement("div");
        paletteEl.className = "smriti-cmd-backdrop";
        paletteEl.id = "smriti-command-palette";
        paletteEl.innerHTML = `
            <div class="smriti-cmd-modal" onclick="event.stopPropagation()">
                <div class="smriti-cmd-input-wrap">
                    <span class="material-symbols-outlined smriti-cmd-icon">search</span>
                    <input type="text" class="smriti-cmd-input" id="smriti-cmd-search-input" placeholder="Type a command or search workspace..." autocomplete="off">
                    <span class="smriti-cmd-shortcut-badge">ESC</span>
                </div>
                <div class="smriti-cmd-results" id="smriti-cmd-results-list"></div>
            </div>
        `;
        document.body.appendChild(paletteEl);

        paletteEl.addEventListener("click", closePalette);
        inputEl = document.getElementById("smriti-cmd-search-input");
        resultsEl = document.getElementById("smriti-cmd-results-list");

        inputEl.addEventListener("input", function() {
            renderResults(inputEl.value.trim().toLowerCase());
        });

        inputEl.addEventListener("keydown", function(e) {
            if (e.key === "Escape") closePalette();
        });
    }

    function renderResults(query) {
        if (!resultsEl) return;
        let items = navCommands;
        if (query) {
            items = items.filter(c => c.label.toLowerCase().includes(query) || c.category.toLowerCase().includes(query));
        }

        if (items.length === 0) {
            resultsEl.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--smriti-color-text-muted);">No matching commands found.</div>`;
            return;
        }

        let html = `<div class="smriti-cmd-group-title">Quick Actions & Workspaces</div>`;
        items.forEach(item => {
            html += `
                <a class="smriti-cmd-item" href="${item.route}">
                    <span class="material-symbols-outlined smriti-cmd-item-icon">${item.icon}</span>
                    <span class="smriti-cmd-item-label">${item.label}</span>
                    <span class="smriti-cmd-item-badge">${item.category}</span>
                </a>
            `;
        });
        resultsEl.innerHTML = html;
    }

    function openPalette() {
        createPaletteDOM();
        paletteEl.classList.add("open");
        renderResults("");
        setTimeout(() => inputEl.focus(), 50);
    }

    function closePalette() {
        if (paletteEl) paletteEl.classList.remove("open");
    }

    // Global shortcut listener (Ctrl+K or Cmd+K)
    window.addEventListener("keydown", function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            if (paletteEl && paletteEl.classList.contains("open")) {
                closePalette();
            } else {
                openPalette();
            }
        }
    });

    SMRITI.CommandPalette = {
        open: openPalette,
        close: closePalette
    };
})(window.SMRITI);
