/**
 * @file: smriti_retail_os/public/error_pages/error_page.js
 * @description: Reusable javascript controller for SMRITI Branded Error Experience (Static Asset).
 * @author: Jawahar Ramkripal Mallah
 * @owner: AITDL
 * @license: GPL-3.0-only
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        hydrateDiagnostics();
        hydrateSuggestions();
        setupDiagnosticsToggle();
    });

    /**
     * Populate diagnostic variables on the client side
     */
    function hydrateDiagnostics() {
        // 1. Requested URL
        const urlEl = document.getElementById('diag-url');
        if (urlEl) {
            urlEl.textContent = window.location.href;
        }

        // 2. Timestamp
        const timeEl = document.getElementById('diag-time');
        if (timeEl) {
            timeEl.textContent = new Date().toISOString();
        }

        // 3. Reference ID (HREP standard: SMRITI-ERR-YYYYMMDD-XXXXXX)
        const refEl = document.getElementById('diag-ref');
        if (refEl) {
            const now = new Date();
            const yyyy = now.getFullYear();
            const mm = String(now.getMonth() + 1).padStart(2, '0');
            const dd = String(now.getDate()).padStart(2, '0');
            const randStr = Math.random().toString(36).substring(2, 8).toUpperCase();
            refEl.textContent = `SMRITI-ERR-${yyyy}${mm}${dd}-${randStr}`;
        }

        // 4. Developer Mode Check
        const isDevMode = !!window.SMRITI_DEVELOPER_MODE || 
                         ['localhost', '127.0.0.1'].includes(window.location.hostname) ||
                         new URLSearchParams(window.location.search).has('debug');
        
        const envEl = document.getElementById('diag-env');
        if (envEl) {
            envEl.textContent = isDevMode ? 'SMRITI Development Mode' : 'SMRITI Production';
        }

        const stackBox = document.getElementById('dev-stack-box');
        if (stackBox) {
            stackBox.style.display = isDevMode ? 'block' : 'none';
        }
    }

    /**
     * Map current URL matching patterns to suggest relevant pages
     */
    function hydrateSuggestions() {
        const path = window.location.pathname.toLowerCase();
        const suggestionsBox = document.getElementById('suggestions-box');
        const listEl = document.getElementById('suggestion-list');
        
        if (!listEl || !suggestionsBox) return;

        // Define route mappings with business vocabulary
        const mappings = [
            { key: 'product', label: '📦 Products Catalog', route: '/products' },
            { key: 'purchase', label: '🤝 Purchase Studio', route: '/purchase' },
            { key: 'sale', label: '🛒 Sales Studio (Billing)', route: '/billing' },
            { key: 'bill', label: '🛒 Sales Studio (Billing)', route: '/billing' },
            { key: 'invoice', label: '🛒 Sales Studio (Billing)', route: '/billing' },
            { key: 'report', label: '📊 Business Reports', route: '/reports' },
            { key: 'analytic', label: '📊 Business Reports', route: '/reports' },
            { key: 'setting', label: '⚙️ Configuration Portal', route: '/config-portal' },
            { key: 'config', label: '⚙️ Configuration Portal', route: '/config-portal' },
            { key: 'customer', label: '👤 Customers Directory', route: '/customers' },
            { key: 'supplier', label: '🏢 Suppliers Registry', route: '/suppliers' },
            { key: 'barcode', label: '🏷️ Barcode Center', route: '/barcode' },
            { key: 'opening', label: '📦 Inventory Operations', route: '/inventory' },
            { key: 'stock', label: '📦 Inventory Operations', route: '/inventory' }
        ];

        const matched = [];
        mappings.forEach(item => {
            if (path.includes(item.key)) {
                matched.push(item);
            }
        });

        // If no matching suggestions, add standard fallback modules
        if (matched.length === 0) {
            matched.push({ label: '🛒 Sales Studio (Billing)', route: '/billing' });
            matched.push({ label: '📦 Products Catalog', route: '/products' });
            matched.push({ label: '📊 Business Reports', route: '/reports' });
        }

        // Render matched links
        listEl.innerHTML = '';
        matched.forEach(item => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = item.route;
            a.textContent = item.label;
            li.appendChild(a);
            listEl.appendChild(li);
        });

        suggestionsBox.style.display = 'block';
    }

    /**
     * Set up accessibility and toggling for diagnostics panel
     */
    function setupDiagnosticsToggle() {
        const toggleBtn = document.getElementById('diag-toggle');
        const detailsPanel = document.getElementById('diag-details');

        if (!toggleBtn || !detailsPanel) return;

        toggleBtn.addEventListener('click', function() {
            const isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';
            toggleBtn.setAttribute('aria-expanded', !isExpanded);
            detailsPanel.hidden = isExpanded;
        });

        // Accessibility keyboard shortcut support (Escape closes diagnostics panel if focused)
        detailsPanel.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                toggleBtn.setAttribute('aria-expanded', 'false');
                detailsPanel.hidden = true;
                toggleBtn.focus();
            }
        });
    }

})();
