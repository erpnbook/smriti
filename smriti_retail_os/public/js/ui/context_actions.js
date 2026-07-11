/**
 * @file:    public/js/ui/context_actions.js
 * @desc:    Adaptive Context Action System (ACAS) JavaScript Core.
 *           Manages action registration, context resolution, and responsive rendering.
 * @author:  SMRITI Platform
 */

window.SMRITI = window.SMRITI || {};

(function () {
    "use strict";

    // ── 1. Registry ──────────────────────────────────────────────────────────
    SMRITI.ContextRegistry = {
        actions: [],

        /**
         * Register a context action
         * @param {Object} actionConfig - Configuration object
         */
        register(actionConfig) {
            if (!actionConfig.id || !actionConfig.label) {
                console.warn("SMRITI ACAS: Invalid action config skipped", actionConfig);
                return;
            }
            // Check for duplicates
            if (this.actions.some(a => a.id === actionConfig.id)) {
                return;
            }
            this.actions.push({
                id: actionConfig.id,
                label: actionConfig.label,
                icon: actionConfig.icon || "bolt",
                shortcut: actionConfig.shortcut || null,
                roles: actionConfig.roles || [],
                permissions: actionConfig.permissions || [],
                isDanger: !!actionConfig.isDanger,
                condition: actionConfig.condition || null,
                callback: actionConfig.callback || null,
                category: actionConfig.category || "General",
                scope: actionConfig.scope || "*" // DocType or context keyword, e.g. "Item", "POS Invoice", "Report"
            });
        },

        getActionsFor(scope, context = {}) {
            return this.actions.filter(action => {
                if (action.scope !== "*" && action.scope !== scope) {
                    return false;
                }
                // Role filter
                if (action.roles.length > 0) {
                    const userRoles = frappe.user_roles || [];
                    const hasRole = action.roles.some(r => userRoles.includes(r) || userRoles.includes("System Manager"));
                    if (!hasRole) return false;
                }
                // Custom condition callback
                if (typeof action.condition === "function") {
                    try {
                        if (!action.condition(context)) return false;
                    } catch (e) {
                        return false;
                    }
                }
                return true;
            });
        }
    };

    // ── 2. Provider & AI Rules Engine ───────────────────────────────────────
    SMRITI.ContextProvider = {
        resolveContext(element) {
            const contextElem = element.closest("[data-smriti-context-object]");
            if (!contextElem) return null;

            const scope = contextElem.getAttribute("data-smriti-context-object");
            const id = contextElem.getAttribute("data-smriti-context-id");
            const state = contextElem.getAttribute("data-smriti-context-state");
            const module = contextElem.getAttribute("data-smriti-context-module");

            // Extract additional custom attributes if any
            const dataAttributes = {};
            Array.from(contextElem.attributes).forEach(attr => {
                if (attr.name.startsWith("data-smriti-context-val-")) {
                    const key = attr.name.replace("data-smriti-context-val-", "");
                    dataAttributes[key] = attr.value;
                }
            });

            return {
                scope,
                id,
                state,
                module,
                element: contextElem,
                ...dataAttributes
            };
        },

        getActions(context) {
            if (!context || !context.scope) return [];
            let actions = SMRITI.ContextRegistry.getActionsFor(context.scope, context);

            // AI Features / Recommendation rules engine
            actions = this.injectAiRecommendations(actions, context);

            // Audit recent usage tracking
            actions = this.injectRecentsAndFavorites(actions, context);

            return actions;
        },

        injectAiRecommendations(actions, context) {
            const state = (context.state || "").toLowerCase();
            const scope = context.scope;

            // Simple rules for smart AI next action promotion
            let recommendedId = null;

            if (scope === "POS Invoice" && (state === "pending" || state === "draft")) {
                recommendedId = "pos_receive_payment";
            } else if (scope === "Item" && (context.stock_qty <= context.reorder_level || state === "low stock")) {
                recommendedId = "item_create_po";
            } else if (scope === "Customer" && (context.outstanding_amount > 0 || state === "outstanding")) {
                recommendedId = "customer_send_reminder";
            } else if (scope === "Purchase Order" && (state === "draft" || state === "0")) {
                recommendedId = "po_submit";
            } else if (scope === "POS Invoice" && (state === "completed" || state === "submitted" || state === "paid" || state === "1")) {
                recommendedId = "pos_print";
            }

            if (recommendedId) {
                return actions.map(act => {
                    if (act.id === recommendedId) {
                        return { ...act, recommended: true, label: `✨ ${act.label}` };
                    }
                    return act;
                });
            }
            return actions;
        },

        injectRecentsAndFavorites(actions, context) {
            // Retrieve pin status and favorites from localStorage
            const favorites = JSON.parse(localStorage.getItem(`smriti_fav_actions_${context.scope}`) || "[]");
            const recents = JSON.parse(localStorage.getItem(`smriti_recent_actions_${context.scope}`) || "[]");

            return actions.map(act => {
                const isFavorite = favorites.includes(act.id);
                const isRecent = recents.includes(act.id);
                return { ...act, isFavorite, isRecent };
            });
        },

        recordActionExecution(actionId, scope) {
            let recents = JSON.parse(localStorage.getItem(`smriti_recent_actions_${scope}`) || "[]");
            recents = [actionId, ...recents.filter(id => id !== actionId)].slice(0, 3);
            localStorage.setItem(`smriti_recent_actions_${scope}`, JSON.stringify(recents));

            // Log action execution for audit trail
            console.log(`[SMRITI ACAS Audit] Executed action "${actionId}" on scope "${scope}"`);
        }
    };

    // ── 3. Renderer ──────────────────────────────────────────────────────────
    SMRITI.ContextRenderer = {
        activeMenu: null,
        activeBackdrop: null,
        focusIndex: -1,

        open(context, x, y) {
            this.close();

            const actions = SMRITI.ContextProvider.getActions(context);
            if (actions.length === 0) return;

            // Render overlay backdrop
            this.renderBackdrop();

            // Determine layout
            const width = window.innerWidth;
            let menuElem;

            if (width < 480) {
                // Small Mobile -> Full Screen Action Sheet style
                menuElem = this.renderBottomSheet(context, actions, true);
            } else if (width < 768) {
                // Mobile -> Bottom Sheet
                menuElem = this.renderBottomSheet(context, actions, false);
            } else if (width < 1200) {
                // Tablet -> Floating Card
                menuElem = this.renderPopover(context, actions, x, y, true);
            } else {
                // Desktop -> Floating Context Menu
                menuElem = this.renderPopover(context, actions, x, y, false);
            }

            this.activeMenu = menuElem;
            this.focusIndex = -1;
            this.setupKeyboardNavigation(menuElem);
        },

        close() {
            if (this.activeMenu) {
                this.activeMenu.classList.remove("show");
                const elem = this.activeMenu;
                setTimeout(() => elem.remove(), 200);
                this.activeMenu = null;
            }
            if (this.activeBackdrop) {
                this.activeBackdrop.classList.remove("show");
                const bg = this.activeBackdrop;
                setTimeout(() => bg.remove(), 200);
                this.activeBackdrop = null;
            }
            this.focusIndex = -1;
        },

        renderBackdrop() {
            const backdrop = document.createElement("div");
            backdrop.className = "smriti-context-backdrop";
            document.body.appendChild(backdrop);
            backdrop.addEventListener("click", () => this.close());
            setTimeout(() => backdrop.classList.add("show"), 10);
            this.activeBackdrop = backdrop;
        },

        renderPopover(context, actions, x, y, isTabletCard = false) {
            const popover = document.createElement("div");
            popover.className = "smriti-context-popover" + (isTabletCard ? " tablet-card" : "");
            
            // Build items HTML
            popover.innerHTML = this.buildMenuHtml(context, actions);
            document.body.appendChild(popover);

            // Position calculation (ensure it doesn't go off screen)
            const menuWidth = popover.offsetWidth || 240;
            const menuHeight = popover.offsetHeight || 300;
            const winWidth = window.innerWidth;
            const winHeight = window.innerHeight;

            let posX = x;
            let posY = y;

            if (x + menuWidth > winWidth) {
                posX = winWidth - menuWidth - 12;
            }
            if (y + menuHeight > winHeight) {
                posY = winHeight - menuHeight - 12;
            }
            if (posX < 0) posX = 12;
            if (posY < 0) posY = 12;

            popover.style.left = `${posX}px`;
            popover.style.top = `${posY}px`;

            this.attachItemListeners(popover, actions, context);
            setTimeout(() => popover.classList.add("show"), 10);
            return popover;
        },

        renderBottomSheet(context, actions, isFullScreen = false) {
            const sheet = document.createElement("div");
            sheet.className = "smriti-context-bottom-sheet" + (isFullScreen ? " full-screen" : "");
            
            sheet.innerHTML = `
                <div class="smriti-context-sheet-handle"></div>
                ${this.buildMenuHtml(context, actions)}
            `;
            document.body.appendChild(sheet);

            this.attachItemListeners(sheet, actions, context);
            setTimeout(() => sheet.classList.add("show"), 10);
            return sheet;
        },

        buildMenuHtml(context, actions) {
            // Sort actions: favorites first, then recommended, then the rest
            const sortedActions = [...actions].sort((a, b) => {
                if (a.isFavorite && !b.isFavorite) return -1;
                if (!a.isFavorite && b.isFavorite) return 1;
                if (a.recommended && !b.recommended) return -1;
                if (!a.recommended && b.recommended) return 1;
                return 0;
            });

            // Group by category
            const categories = {};
            sortedActions.forEach(act => {
                const cat = act.category || "General";
                categories[cat] = categories[cat] || [];
                categories[cat].push(act);
            });

            let html = `
                <div class="smriti-context-header">
                    <div>
                        <div class="smriti-context-title">${context.scope} Actions</div>
                        <div class="smriti-context-subtitle">${context.id || "Selection options"}</div>
                    </div>
                </div>
            `;

            // If more than 6 actions, add a search bar
            if (sortedActions.length > 6) {
                html += `
                    <div class="smriti-context-search-wrapper">
                        <input type="text" class="smriti-context-search-input" placeholder="Search actions..." aria-label="Search actions">
                    </div>
                `;
            }

            html += `<div class="smriti-context-list">`;
            
            Object.keys(categories).forEach((cat, catIdx) => {
                if (catIdx > 0) {
                    html += `<div class="smriti-context-divider"></div>`;
                }
                categories[cat].forEach(act => {
                    const itemClass = (act.recommended ? " recommended" : "") + (act.isDanger ? " danger" : "");
                    const shortcutHtml = act.shortcut ? `<span class="smriti-context-shortcut">${act.shortcut}</span>` : "";
                    const favIcon = act.isFavorite ? "⭐" : "";
                    
                    html += `
                        <button class="smriti-context-item${itemClass}" data-action-id="${act.id}" role="menuitem">
                            <span class="material-symbols-outlined smriti-context-icon">${act.icon}</span>
                            <span class="smriti-context-label">${act.label} ${favIcon}</span>
                            ${shortcutHtml}
                        </button>
                    `;
                });
            });

            html += `</div>`;
            return html;
        },

        attachItemListeners(menuElem, actions, context) {
            // Action item click handlers
            menuElem.querySelectorAll(".smriti-context-item").forEach(item => {
                item.addEventListener("click", () => {
                    const actionId = item.getAttribute("data-action-id");
                    const action = actions.find(a => a.id === actionId);
                    if (action) {
                        SMRITI.ContextProvider.recordActionExecution(actionId, context.scope);
                        if (typeof action.callback === "function") {
                            action.callback(context);
                        }
                    }
                    this.close();
                });
            });

            // Action search bar filter listener
            const searchInput = menuElem.querySelector(".smriti-context-search-input");
            if (searchInput) {
                searchInput.addEventListener("input", (e) => {
                    const term = e.target.value.toLowerCase().trim();
                    menuElem.querySelectorAll(".smriti-context-item").forEach(item => {
                        const label = item.querySelector(".smriti-context-label").textContent.toLowerCase();
                        if (label.includes(term)) {
                            item.style.display = "flex";
                        } else {
                            item.style.display = "none";
                        }
                    });
                });
                // Focus on search input automatically
                setTimeout(() => searchInput.focus(), 150);
            }
        },

        setupKeyboardNavigation(menuElem) {
            const handleKeyDown = (e) => {
                const items = Array.from(menuElem.querySelectorAll(".smriti-context-item:not([style*='display: none'])"));
                if (items.length === 0) return;

                if (e.key === "ArrowDown" || e.key === "Tab") {
                    e.preventDefault();
                    this.focusIndex = (this.focusIndex + 1) % items.length;
                    items[this.focusIndex].focus();
                } else if (e.key === "ArrowUp") {
                    e.preventDefault();
                    this.focusIndex = (this.focusIndex - 1 + items.length) % items.length;
                    items[this.focusIndex].focus();
                } else if (e.key === "Escape") {
                    e.preventDefault();
                    this.close();
                    document.removeEventListener("keydown", handleKeyDown);
                } else if (e.key === "Enter" && this.focusIndex !== -1) {
                    e.preventDefault();
                    items[this.focusIndex].click();
                    document.removeEventListener("keydown", handleKeyDown);
                }
            };
            document.addEventListener("keydown", handleKeyDown);
        }
    };

    // ── 4. Main Controller & Touch Gesture Listeners ──────────────────────────
    SMRITI.ContextActions = {
        init() {
            this.bindGlobalListeners();
        },

        open(element, event) {
            const context = SMRITI.ContextProvider.resolveContext(element);
            if (!context) return;

            event.preventDefault();
            event.stopPropagation();

            const x = event.clientX || (event.touches && event.touches[0].clientX) || 0;
            const y = event.clientY || (event.touches && event.touches[0].clientY) || 0;

            SMRITI.ContextRenderer.open(context, x, y);
        },

        bindGlobalListeners() {
            let touchTimer = null;
            let startX = 0;
            let startY = 0;

            // 1. Right Click event delegation
            document.body.addEventListener("contextmenu", (e) => {
                const target = e.target.closest("[data-smriti-context-object]");
                if (target) {
                    this.open(target, e);
                }
            });

            // 2. Long Press gesture for Touch screens
            document.body.addEventListener("touchstart", (e) => {
                const target = e.target.closest("[data-smriti-context-object]");
                if (!target) return;

                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;

                if (touchTimer) clearTimeout(touchTimer);
                touchTimer = setTimeout(() => {
                    // Create simulated context menu event
                    const simulatedEvent = {
                        preventDefault: () => e.preventDefault(),
                        stopPropagation: () => e.stopPropagation(),
                        clientX: startX,
                        clientY: startY
                    };
                    this.open(target, simulatedEvent);
                }, 500); // 500ms long press duration
            }, { passive: true });

            document.body.addEventListener("touchmove", (e) => {
                if (!touchTimer) return;
                const diffX = Math.abs(e.touches[0].clientX - startX);
                const diffY = Math.abs(e.touches[0].clientY - startY);
                if (diffX > 10 || diffY > 10) {
                    // Cancel long press if user swiped/scrolled
                    clearTimeout(touchTimer);
                    touchTimer = null;
                }
            });

            document.body.addEventListener("touchend", () => {
                if (touchTimer) {
                    clearTimeout(touchTimer);
                    touchTimer = null;
                }
            });

            // 3. Keyboard trigger Shift+F10 / ContextMenu Key
            document.addEventListener("keydown", (e) => {
                if ((e.shiftKey && e.key === "F10") || e.key === "ContextMenu") {
                    const activeElem = document.activeElement;
                    const target = activeElem ? activeElem.closest("[data-smriti-context-object]") : null;
                    if (target) {
                        const rect = target.getBoundingClientRect();
                        const simulatedEvent = {
                            preventDefault: () => e.preventDefault(),
                            stopPropagation: () => e.stopPropagation(),
                            clientX: rect.left + rect.width / 2,
                            clientY: rect.top + rect.height / 2
                        };
                        this.open(target, simulatedEvent);
                    }
                }
            });
        }
    };

    // ── 5. Default Actions Registration ──────────────────────────────────────
    const reg = SMRITI.ContextRegistry;

    // --- Item / Product Actions ---
    reg.register({
        id: "item_view_details",
        scope: "Item",
        label: "View Details",
        icon: "visibility",
        category: "View",
        callback: (ctx) => {
            if (window.location.pathname.includes("/products") && window.catalogGrid && typeof window.catalogGrid.onRowClick === "function" && ctx.element) {
                const rowIndex = ctx.element.getAttribute("data-index");
                if (rowIndex !== null && window.catalogGrid.data) {
                    const rowData = window.catalogGrid.data[rowIndex];
                    if (rowData) {
                        window.catalogGrid.onRowClick(rowData);
                        return;
                    }
                }
            }
            window.location.href = `/products?item_code=${encodeURIComponent(ctx.id)}`;
        }
    });

    reg.register({
        id: "item_create_po",
        scope: "Item",
        label: "Create Purchase Order",
        icon: "shopping_cart",
        category: "Transactions",
        callback: (ctx) => {
            window.location.href = `/smriti-po-create?item_code=${encodeURIComponent(ctx.id)}`;
        }
    });

    reg.register({
        id: "item_adjust_stock",
        scope: "Item",
        label: "Adjust Stock (Admin Only)",
        icon: "inventory_2",
        category: "Management",
        roles: ["System Manager"],
        callback: (ctx) => {
            if (window.SMRITI.toast) {
                window.SMRITI.toast.success(`Redirecting to stock entry adjustments for item: ${ctx.id}`);
            } else {
                frappe.show_alert(`Redirecting to stock entry adjustments for item: ${ctx.id}`);
            }
        }
    });

    // --- POS Invoice Actions ---
    reg.register({
        id: "pos_receive_payment",
        scope: "POS Invoice",
        label: "Receive Payment",
        icon: "payments",
        category: "Workflow",
        callback: (ctx) => {
            frappe.show_alert(`Opening payment portal for POS Invoice: ${ctx.id}`);
        }
    });

    reg.register({
        id: "pos_print",
        scope: "POS Invoice",
        label: "Print Receipt",
        icon: "print",
        category: "Output",
        callback: (ctx) => {
            window.open(`/printview?doctype=POS%20Invoice&name=${encodeURIComponent(ctx.id)}`, '_blank');
        }
    });

    reg.register({
        id: "pos_whatsapp",
        scope: "POS Invoice",
        label: "Share via WhatsApp",
        icon: "chat",
        category: "Output",
        callback: (ctx) => {
            frappe.show_alert(`Generating invoice link for WhatsApp sharing: ${ctx.id}`);
        }
    });

    reg.register({
        id: "pos_email",
        scope: "POS Invoice",
        label: "Email to Customer",
        icon: "mail",
        category: "Output",
        callback: (ctx) => {
            frappe.show_alert(`Sending PDF receipt for invoice: ${ctx.id}`);
        }
    });

    // --- Purchase Order Actions ---
    reg.register({
        id: "po_submit",
        scope: "Purchase Order",
        label: "Submit Order",
        icon: "publish",
        category: "Workflow",
        callback: (ctx) => {
            frappe.show_alert(`Submitting Purchase Order: ${ctx.id}`);
        }
    });

    reg.register({
        id: "po_create_grn",
        scope: "Purchase Order",
        label: "Create Goods Receipt (GRN)",
        icon: "receipt",
        category: "Workflow",
        callback: (ctx) => {
            window.location.href = `/smriti-grn?purchase_order=${encodeURIComponent(ctx.id)}`;
        }
    });

    // --- Customer Actions ---
    reg.register({
        id: "customer_send_reminder",
        scope: "Customer",
        label: "Send Outstanding Reminder",
        icon: "notifications_active",
        category: "Notifications",
        callback: (ctx) => {
            frappe.show_alert(`Sending payment reminder to Customer: ${ctx.id}`);
        }
    });

    reg.register({
        id: "customer_view_ledger",
        scope: "Customer",
        label: "View Customer Ledger",
        icon: "menu_book",
        category: "Reports",
        callback: (ctx) => {
            window.location.href = `/reports?report_name=customer_outstanding&customer=${encodeURIComponent(ctx.id)}`;
        }
    });

    // --- Report Actions ---
    reg.register({
        id: "report_export_excel",
        scope: "Report",
        label: "Export to Excel",
        icon: "table_view",
        category: "Export",
        callback: () => {
            const btn = document.getElementById("btn-export-excel") || document.querySelector(".btn-export-excel");
            if (btn) btn.click();
            else frappe.show_alert("Triggering Excel Export...");
        }
    });

    reg.register({
        id: "report_export_csv",
        scope: "Report",
        label: "Export to CSV",
        icon: "description",
        category: "Export",
        callback: () => {
            const btn = document.getElementById("btn-export-csv") || document.querySelector(".btn-export-csv");
            if (btn) btn.click();
            else frappe.show_alert("Triggering CSV Export...");
        }
    });

    // Auto-bootstrap ACAS on script load
    if (document.readyState !== "loading") {
        SMRITI.ContextActions.init();
    } else {
        document.addEventListener("DOMContentLoaded", () => {
            SMRITI.ContextActions.init();
        });
    }

})();
