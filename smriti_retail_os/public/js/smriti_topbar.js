/**
 * @file: smriti_retail_os/public/js/smriti_topbar.js
 * @description: SMRITI Global Search Topbar — injects a floating search bar
 *               at the top of every SMRITI page, replacing Frappe/ERPNext search.
 * @author: Jawahar R. Mallah <jawahar.mallah@gmail.com>
 * @version: 1.0.0
 */
(function () {
    "use strict";

    const SEARCH_API = "smriti_retail_os.search_studio.api.smriti_search_api.global_search";
    const RECENT_API = "smriti_retail_os.search_studio.api.smriti_search_api.get_recent_docs";

    // ── CSS ─────────────────────────────────────────────────────────────────
    const CSS = `
#smriti-topbar {
  position: fixed; top: 0; left: 0; right: 0; height: 48px;
  background: rgba(8,14,28,0.96); backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  display: flex; align-items: center; gap: 12px;
  padding: 0 16px; z-index: 9000;
  font-family: Arial, Helvetica, sans-serif;
}
#smriti-topbar-logo {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 700; color: #e2e8f0;
  text-decoration: none; white-space: nowrap; flex-shrink: 0;
}
#smriti-topbar-logo img { width:24px; height:24px; border-radius:6px; }
#smriti-search-wrap {
  flex: 1; max-width: 480px; margin: 0 auto; position: relative;
}
#smriti-search-input {
  width: 100%; height: 34px; background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
  color: #e2e8f0; font-size: 13px; font-family: Arial, Helvetica, sans-serif;
  padding: 0 36px 0 36px; outline: none; transition: all 0.15s;
}
#smriti-search-input::placeholder { color: #475569; }
#smriti-search-input:focus {
  border-color: rgba(37,99,235,0.5); background: rgba(37,99,235,0.06);
  box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
}
#smriti-search-ico {
  position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
  color: #475569; pointer-events: none;
}
#smriti-search-kbd {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px; color: #475569; font-size: 10px;
  padding: 2px 5px; pointer-events: none;
}
/* RESULTS DROPDOWN */
#smriti-search-results {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0;
  background: #0f1729; border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; box-shadow: 0 24px 60px rgba(0,0,0,0.6);
  max-height: 420px; overflow-y: auto; display: none; z-index: 9100;
  font-family: Arial, Helvetica, sans-serif;
}
#smriti-search-results::-webkit-scrollbar { width: 3px; }
#smriti-search-results::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
.sr-section { padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.sr-section:last-child { border-bottom: none; }
.sr-heading {
  font-size: 10px; font-weight: 700; color: #475569;
  text-transform: uppercase; letter-spacing: 0.8px;
  padding: 8px 14px 4px;
}
.sr-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 14px; cursor: pointer; transition: background 0.1s;
}
.sr-item:hover, .sr-item.focused { background: rgba(37,99,235,0.1); }
.sr-ico {
  width: 30px; height: 30px; border-radius: 7px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; background: rgba(255,255,255,0.05);
}
.sr-body { flex: 1; min-width: 0; }
.sr-label { font-size: 13px; color: #e2e8f0; font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sr-sub { font-size: 11px; color: #64748b; margin-top: 1px; }
.sr-badge {
  font-size: 10px; font-weight: 700; padding: 2px 7px;
  border-radius: 8px; white-space: nowrap; flex-shrink: 0;
}
.sr-badge-item { background: rgba(37,99,235,0.1); color: #2563EB; }
.sr-badge-cust { background: rgba(16,185,129,0.1); color: #10b981; }
.sr-badge-supp { background: rgba(124,58,237,0.1); color: #a78bfa; }
.sr-badge-po   { background: rgba(245,158,11,0.1); color: #f59e0b; }
.sr-badge-inv  { background: rgba(239,68,68,0.1); color: #ef4444; }
.sr-badge-grn  { background: rgba(16,185,129,0.1); color: #10b981; }
.sr-badge-page { background: rgba(100,116,139,0.1); color: #94a3b8; }
.sr-empty { text-align: center; padding: 28px; color: #475569; font-size: 13px; }
.sr-tip  { text-align: center; padding: 10px 14px; font-size: 11px; color: #334155; }

/* TOPBAR RIGHT */
#smriti-topbar-right {
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.tb-icon-btn {
  width: 34px; height: 34px; border-radius: 8px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
  color: #94a3b8; display: flex; align-items: center; justify-content:center;
  cursor: pointer; transition: all 0.15s; text-decoration: none; position: relative;
}
.tb-icon-btn:hover { background: rgba(37,99,235,0.12); color: #2563EB; border-color: rgba(37,99,235,0.3); }
#tb-notif-badge {
  position: absolute; top: -4px; right: -4px;
  min-width: 16px; height: 16px; background: #ef4444; color: #fff;
  border-radius: 8px; font-size: 9px; font-weight: 700; padding: 0 3px;
  display: none; align-items: center; justify-content: center;
  border: 2px solid #080e1c;
}
.tb-user-btn {
  height: 34px; padding: 0 10px 0 6px; gap: 7px;
  border-radius: 8px; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08); color: #94a3b8;
  display: flex; align-items: center; cursor: pointer;
  transition: all 0.15s; text-decoration: none; font-size: 12px;
  font-family: Arial, Helvetica, sans-serif;
}
.tb-user-btn:hover { background: rgba(37,99,235,0.08); color: #e2e8f0; border-color: rgba(37,99,235,0.25); }
.tb-avatar {
  width: 24px; height: 24px; border-radius: 50%;
  background: linear-gradient(135deg,#2563EB,#7c3aed);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #fff; flex-shrink: 0;
}
/* Body offset when topbar is injected */
body.smriti-topbar-active { padding-top: 48px; }
body.smriti-topbar-active .smriti-sidebar { top: 48px !important; height: calc(100vh - 48px) !important; }
`;

    // ── HTML Template ────────────────────────────────────────────────────────
    function buildTopbar() {
        const user = (window.frappe && frappe.session && frappe.session.user_fullname) || "User";
        const initial = user.charAt(0).toUpperCase();

        const el = document.createElement("div");
        el.id = "smriti-topbar";
        el.innerHTML = `
          <a id="smriti-topbar-logo" href="/smriti">
            <img src="/assets/smriti_retail_os/images/smriti-logo.png"
                 onerror="this.style.display='none'" alt=""/>
            <span>SMRITI</span>
          </a>

          <div id="smriti-search-wrap">
            <svg id="smriti-search-ico" width="14" height="14" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input id="smriti-search-input" type="text"
                   placeholder="Search items, customers, orders… (Ctrl+K)"
                   autocomplete="off" spellcheck="false"/>
            <span id="smriti-search-kbd">⌘K</span>
            <div id="smriti-search-results"></div>
          </div>

          <div id="smriti-topbar-right">
            <!-- Notification Bell -->
            <a class="tb-icon-btn" href="/smriti-notifications" title="Notifications" id="tb-notif-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              <span id="tb-notif-badge"></span>
            </a>

            <!-- Dashboard -->
            <a class="tb-icon-btn" href="/smriti" title="Dashboard">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
              </svg>
            </a>

            <!-- User Profile -->
            <a class="tb-user-btn" href="/smriti-profile" title="My Profile">
              <div class="tb-avatar" id="tb-avatar">${initial}</div>
              <span id="tb-username">${user.split(" ")[0]}</span>
            </a>
          </div>
        `;
        return el;
    }

    // ── Search Logic ─────────────────────────────────────────────────────────
    let _searchTimer = null;
    let _focusIdx = -1;
    let _results = [];

    function debounce(fn, ms) {
        return function (...args) {
            clearTimeout(_searchTimer);
            _searchTimer = setTimeout(() => fn(...args), ms);
        };
    }

    function apiSearch(query) {
        return new Promise((res, rej) => {
            frappe.call({
                method: SEARCH_API,
                args: { query, limit: 6 },
                callback: r => res(r.message || {}),
                error: rej
            });
        });
    }

    function highlight(text, query) {
        if (!query || !text) return text || "";
        const re = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
        return String(text).replace(re, '<mark style="background:rgba(37,99,235,0.3);color:#93c5fd;border-radius:2px;">$1</mark>');
    }

    function renderResults(data, query) {
        const box = document.getElementById("smriti-search-results");
        if (!box) return;

        const sections = [];
        _results = [];

        const add = (items, label, icon, badgeClass, routeFn) => {
            if (!items || !items.length) return;
            const rows = items.slice(0, 5).map(item => {
                _results.push({ route: routeFn(item), label: item.item_name || item.customer_name || item.supplier_name || item.name || item.label });
                return `
                <div class="sr-item" data-idx="${_results.length - 1}"
                     onclick="window.SMRITI_TOPBAR.navigate(${_results.length - 1})">
                  <div class="sr-ico">${icon}</div>
                  <div class="sr-body">
                    <div class="sr-label">${highlight(item.item_name || item.customer_name || item.supplier_name || item.name || item.label, query)}</div>
                    <div class="sr-sub">${item.item_code || item.name || item.route || ""}</div>
                  </div>
                  <span class="sr-badge ${badgeClass}">${label}</span>
                </div>`;
            });
            sections.push(`<div class="sr-section"><div class="sr-heading">${label}</div>${rows.join("")}</div>`);
        };

        add(data.items,     "Item",      "🏷️", "sr-badge-item", i => `/products?item=${i.item_code}`);
        add(data.customers, "Customer",  "👥", "sr-badge-cust", i => `/customers?id=${i.name}`);
        add(data.suppliers, "Supplier",  "🏭", "sr-badge-supp", i => `/suppliers?id=${i.name}`);
        add(data.orders,    "PO",        "📋", "sr-badge-po",   i => `/smriti-purchase#orders`);
        add(data.invoices,  "Invoice",   "💰", "sr-badge-inv",  i => `/sales-invoices?id=${i.name}`);
        add(data.grns,      "GRN",       "📦", "sr-badge-grn",  i => `/smriti-purchase#grn`);
        add(data.pages,     "Page",      "🗺️", "sr-badge-page", i => i.route);

        if (!sections.length) {
            box.innerHTML = `<div class="sr-empty">No results for "<strong>${query}</strong>"</div>
              <div class="sr-tip">Try searching by item code, customer name, or PO number</div>`;
        } else {
            box.innerHTML = sections.join("") +
              `<div class="sr-tip">↑↓ navigate · Enter open · Esc close</div>`;
        }

        box.style.display = "block";
        _focusIdx = -1;
    }

    function showRecentOrEmpty() {
        const box = document.getElementById("smriti-search-results");
        if (!box) return;
        // Quick nav shortcuts
        const shortcuts = [
            { label: "Purchase Studio", route: "/smriti-purchase", icon: "🏭" },
            { label: "POS Billing",     route: "/billing",         icon: "🧾" },
            { label: "Inventory",       route: "/inventory",       icon: "📁" },
            { label: "Notifications",   route: "/smriti-notifications", icon: "🔔" },
        ];
        _results = shortcuts;
        box.innerHTML = `
          <div class="sr-section">
            <div class="sr-heading">Quick Navigate</div>
            ${shortcuts.map((s, i) => `
              <div class="sr-item" data-idx="${i}" onclick="window.SMRITI_TOPBAR.navigate(${i})">
                <div class="sr-ico">${s.icon}</div>
                <div class="sr-body"><div class="sr-label">${s.label}</div></div>
                <span class="sr-badge sr-badge-page">Page</span>
              </div>`).join("")}
          </div>
          <div class="sr-tip">Start typing to search items, customers, POs…</div>`;
        box.style.display = "block";
    }

    function closeResults() {
        const box = document.getElementById("smriti-search-results");
        if (box) box.style.display = "none";
        _focusIdx = -1;
    }

    function moveFocus(dir) {
        const items = document.querySelectorAll("#smriti-search-results .sr-item");
        if (!items.length) return;
        items.forEach(i => i.classList.remove("focused"));
        _focusIdx = Math.max(0, Math.min(_focusIdx + dir, items.length - 1));
        items[_focusIdx].classList.add("focused");
        items[_focusIdx].scrollIntoView({ block: "nearest" });
    }

    // ── Badge ────────────────────────────────────────────────────────────────
    function hydrateBadge() {
        if (!window.frappe || !frappe.call) return;
        frappe.call({
            method: "smriti_retail_os.notification_studio.api.smriti_notifications_api.get_unread_badge",
            callback: function (r) {
                if (!r || !r.message) return;
                const cnt = r.message.count || 0;
                const badge = document.getElementById("tb-notif-badge");
                if (badge) {
                    badge.textContent = cnt > 99 ? "99+" : cnt;
                    badge.style.display = cnt > 0 ? "inline-flex" : "none";
                }
            }
        });
    }

    // ── Init ────────────────────────────────────────────────────────────────
    function init() {
        // Only inject once
        if (document.getElementById("smriti-topbar")) return;
        // Don't inject on login page
        if (window.location.pathname.includes("smriti-login")) return;

        // Inject CSS
        const style = document.createElement("style");
        style.id = "smriti-topbar-css";
        style.textContent = CSS;
        document.head.appendChild(style);

        // Inject topbar
        const topbar = buildTopbar();
        document.body.insertBefore(topbar, document.body.firstChild);
        document.body.classList.add("smriti-topbar-active");

        // ── Input events ──
        const input = document.getElementById("smriti-search-input");
        const doSearch = debounce(async function (q) {
            if (q.length < 2) { showRecentOrEmpty(); return; }
            try {
                const data = await apiSearch(q);
                renderResults(data, q);
            } catch (e) {
                console.warn("[SMRITI Search]", e);
            }
        }, 280);

        input.addEventListener("input", e => doSearch(e.target.value.trim()));
        input.addEventListener("focus", () => {
            if (!input.value.trim()) showRecentOrEmpty();
            else if (_results.length) document.getElementById("smriti-search-results").style.display = "block";
        });
        input.addEventListener("keydown", e => {
            if (e.key === "ArrowDown") { e.preventDefault(); moveFocus(1); }
            else if (e.key === "ArrowUp") { e.preventDefault(); moveFocus(-1); }
            else if (e.key === "Enter") {
                e.preventDefault();
                if (_focusIdx >= 0 && _results[_focusIdx]) {
                    window.location.href = _results[_focusIdx].route || _results[_focusIdx];
                } else if (_results.length) {
                    window.location.href = _results[0].route || _results[0];
                }
            }
            else if (e.key === "Escape") { closeResults(); input.blur(); }
        });

        // Close on outside click
        document.addEventListener("click", e => {
            if (!e.target.closest("#smriti-search-wrap")) closeResults();
        });

        // ── Ctrl+K global shortcut ──
        document.addEventListener("keydown", e => {
            if ((e.ctrlKey || e.metaKey) && e.key === "k") {
                e.preventDefault();
                input.focus();
                input.select();
                showRecentOrEmpty();
            }
        });

        // Badge
        hydrateBadge();
        if (frappe && frappe.realtime) {
            frappe.realtime.on("smriti_notification", hydrateBadge);
        }
        setInterval(hydrateBadge, 60000);
    }

    // Public API
    window.SMRITI_TOPBAR = {
        navigate: function (idx) {
            const r = _results[idx];
            if (r) window.location.href = r.route || r;
        },
        open: function () {
            const input = document.getElementById("smriti-search-input");
            if (input) { input.focus(); input.select(); showRecentOrEmpty(); }
        }
    };

    // Init after frappe is ready
    if (window.frappe && frappe.ready) {
        frappe.ready(init);
    } else {
        document.addEventListener("DOMContentLoaded", function () {
            // Wait a tick for frappe to init
            setTimeout(init, 300);
        });
    }
})();
