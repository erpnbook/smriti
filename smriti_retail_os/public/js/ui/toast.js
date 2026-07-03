/**
 * @file:    public/js/ui/toast.js
 * @desc:    SMRITI toast component for programmatic non-blocking alerts.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.toast = (function() {
    function ensureContainer() {
        let container = document.getElementById("toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "toast-container";
            document.body.appendChild(container);
        }
        return container;
    }

    function show(msg, type = "success") {
        const container = ensureContainer();
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        
        const icons = {
            success: "check_circle",
            error: "error",
            warn: "warning",
            info: "info"
        };
        const icon = icons[type] || "info";

        toast.innerHTML = `
            <span class="material-symbols-outlined">${icon}</span>
            <span>${msg}</span>
        `;
        
        container.appendChild(toast);
        
        // Auto-dismiss transition
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-10px)";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    return {
        success: (msg) => show(msg, "success"),
        error: (msg) => show(msg, "error"),
        warn: (msg) => show(msg, "warn"),
        info: (msg) => show(msg, "info")
    };
})();

// Assign helper shortcut to window
window.toast = SMRITI.toast.success;
