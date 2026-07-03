/**
 * @file:    public/js/ui/drawer.js
 * @desc:    SMRITI Drawer Component - Handles slide-out details viewer overlay.
 * @author:  Jawahar R. Mallah
 */

window.SMRITI = window.SMRITI || {};

SMRITI.Drawer = (function() {
    let drawerEl = null;
    let backdropEl = null;

    function ensureElements() {
        if (!drawerEl) {
            backdropEl = document.createElement("div");
            backdropEl.className = "drawer-backdrop";
            
            drawerEl = document.createElement("div");
            drawerEl.className = "drawer";
            
            document.body.appendChild(backdropEl);
            document.body.appendChild(drawerEl);

            backdropEl.addEventListener("click", () => SMRITI.Drawer.close());
        }
    }

    return {
        open: function(options = {}) {
            ensureElements();
            
            const title = options.title || "Detail View";
            const content = options.content || "";

            drawerEl.innerHTML = `
                <div class="drawer-header">
                    <h2>${title}</h2>
                    <button class="drawer-close-btn" onclick="SMRITI.Drawer.close()">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
                <div class="drawer-body">
                    ${content}
                </div>
            `;

            backdropEl.classList.add("show");
            drawerEl.classList.add("open");
        },

        close: function() {
            if (drawerEl) {
                backdropEl.classList.remove("show");
                drawerEl.classList.remove("open");
            }
        }
    };
})();
