// -*- coding: utf-8 -*-
// SMRITI Universal Smart Lookup Component
// Proactively handles debounced searches, recents, validation, and dynamic Quick Create.

(function() {
  const API = "smriti_retail_os.api.lookup_api";

  const fieldsConfig = {
    Customer: [
        { name: "customer_name", label: "Customer Name", type: "text", required: true },
        { name: "mobile_no", label: "Mobile No", type: "text" }
    ],
    Supplier: [
        { name: "supplier_name", label: "Supplier Name", type: "text", required: true },
        { name: "mobile_no", label: "Mobile No", type: "text" },
        { name: "email_id", label: "Email ID", type: "email" }
    ],
    Product: [
        { name: "item_code", label: "Product / Barcode", type: "text", required: true },
        { name: "item_name", label: "Product Name", type: "text", required: true },
        { name: "standard_rate", label: "Standard Rate", type: "number", required: true }
    ],
    Warehouse: [
        { name: "warehouse_name", label: "Warehouse Name", type: "text", required: true }
    ],
    Employee: [
        { name: "employee_name", label: "Employee Name", type: "text", required: true },
        { name: "cell_number", label: "Cell Number", type: "text" }
    ],
    Salesperson: [
        { name: "sales_person_name", label: "Sales Person Name", type: "text", required: true }
    ],
    Brand: [
        { name: "brand_name", label: "Brand Name", type: "text", required: true }
    ],
    Category: [
        { name: "item_group_name", label: "Item Group Name", type: "text", required: true }
    ],
    UOM: [
        { name: "uom_name", label: "UOM Name", type: "text", required: true }
    ],
    "Tax Template": [
        { name: "title", label: "Tax Template Title", type: "text", required: true }
    ],
    "Payment Terms": [
        { name: "template_name", label: "Template Name", type: "text", required: true }
    ],
    Currency: [
        { name: "currency_name", label: "Currency Name", type: "text", required: true }
    ],
    Company: [
        { name: "company_name", label: "Company Name", type: "text", required: true }
    ]
  };

  class SmritiSmartLookup {
    constructor(opts) {
      this.input = opts.input;
      this.entity = opts.entity;
      this.filters = opts.filters || {};
      this.onSelect = opts.onSelect;
      this.onCreate = opts.onCreate;
      this.recentList = [];
      this.searchResults = [];
      this.highlightedIdx = -1;
      this.debounceTimer = null;

      this.initDOM();
      this.initEvents();
    }

    initDOM() {
      // Wrap the input in a container for relative positioning of the dropdown
      if (!this.input.parentNode.classList.contains("smriti-lookup-container")) {
        const wrapper = document.createElement("div");
        wrapper.className = "smriti-lookup-container";
        this.input.parentNode.insertBefore(wrapper, this.input);
        wrapper.appendChild(this.input);
      }

      this.container = this.input.parentNode;

      // Dropdown DOM
      this.dropdown = document.createElement("div");
      this.dropdown.className = "smriti-lookup-dropdown";
      this.container.appendChild(this.dropdown);
    }

    initEvents() {
      // Focus or click
      this.input.addEventListener("focus", () => this.showRecents());
      this.input.addEventListener("click", () => this.showRecents());

      // Key typing
      this.input.addEventListener("keyup", (e) => {
        if (["ArrowUp", "ArrowDown", "Enter", "Escape"].includes(e.key)) {
          this.handleKeyNavigation(e);
          return;
        }
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
          this.performSearch(this.input.value);
        }, 200);
      });

      // Click outside to close
      document.addEventListener("click", (e) => {
        if (!this.container.contains(e.target)) {
          this.closeDropdown();
        }
      });
    }

    async showRecents() {
      if (this.input.value.trim().length > 0) return;
      this.highlightedIdx = -1;
      this.dropdown.innerHTML = `<div class="smriti-lookup-header">Loading Recents…</div>`;
      this.dropdown.classList.add("active");

      try {
        const res = await this.apiCall("recent", { entity: this.entity });
        this.recentList = res || [];
        this.renderItems(this.recentList, "Recently Used");
      } catch(e) {
        this.dropdown.innerHTML = `<div class="smriti-lookup-empty">Failed to load recents.</div>`;
      }
    }

    async performSearch(text) {
      if (text.trim().length === 0) {
        this.showRecents();
        return;
      }
      this.highlightedIdx = -1;
      this.dropdown.innerHTML = `<div class="smriti-lookup-header">Searching…</div>`;
      this.dropdown.classList.add("active");

      try {
        const res = await this.apiCall("search", {
          entity: this.entity,
          text: text,
          filters: JSON.stringify(this.filters)
        });
        this.searchResults = res || [];
        this.renderItems(this.searchResults, "Search Results");
      } catch(e) {
        this.dropdown.innerHTML = `<div class="smriti-lookup-empty">Search error.</div>`;
      }
    }

    renderItems(items, title) {
      if (items.length === 0) {
        this.dropdown.innerHTML = `
          <div class="smriti-lookup-empty">
            No matching ${this.entity} found.
            <button class="smriti-lookup-create-btn" type="button">➕ Create New ${this.entity}</button>
          </div>
        `;
        const btn = this.dropdown.querySelector(".smriti-lookup-create-btn");
        if (btn) btn.addEventListener("click", () => this.openQuickCreate());
        return;
      }

      this.dropdown.innerHTML = `
        <div class="smriti-lookup-header">${title}</div>
        ${items.map((it, idx) => `
          <div class="smriti-lookup-item" data-idx="${idx}">
            <span class="lookup-title">${it.label}</span>
            <span class="lookup-subtitle">${it.value}</span>
          </div>
        `).join("")}
      `;

      // Attach click events
      const els = this.dropdown.querySelectorAll(".smriti-lookup-item");
      els.forEach(el => {
        el.addEventListener("click", () => {
          const idx = parseInt(el.getAttribute("data-idx"));
          const list = title === "Recently Used" ? this.recentList : this.searchResults;
          this.select(list[idx]);
        });
      });
    }

    select(item) {
      this.input.value = item.label;
      this.closeDropdown();
      if (this.onSelect) {
        this.onSelect(item.value, item.label, item.detail);
      }
    }

    closeDropdown() {
      this.dropdown.classList.remove("active");
    }

    handleKeyNavigation(e) {
      const items = this.dropdown.querySelectorAll(".smriti-lookup-item");
      if (items.length === 0) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        this.highlightedIdx = (this.highlightedIdx + 1) % items.length;
        this.highlight(items);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        this.highlightedIdx = (this.highlightedIdx - 1 + items.length) % items.length;
        this.highlight(items);
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (this.highlightedIdx >= 0 && this.highlightedIdx < items.length) {
          items[this.highlightedIdx].click();
        }
      } else if (e.key === "Escape") {
        this.closeDropdown();
      }
    }

    highlight(items) {
      items.forEach((el, idx) => {
        if (idx === this.highlightedIdx) {
          el.classList.add("highlighted");
          el.scrollIntoView({ block: "nearest" });
        } else {
          el.classList.remove("highlighted");
        }
      });
    }

    openQuickCreate() {
      this.closeDropdown();
      const fields = fieldsConfig[this.entity] || [{ name: "name", label: "Name", type: "text", required: true }];

      // Render Backdrop and modal dynamically
      const backdrop = document.createElement("div");
      backdrop.className = "smriti-lookup-modal-backdrop";
      
      backdrop.innerHTML = `
        <div class="smriti-lookup-modal">
          <div class="smriti-lookup-modal-header">
            <span class="smriti-lookup-modal-title">Create New ${this.entity}</span>
            <button class="smriti-lookup-modal-close" type="button">&times;</button>
          </div>
          <form class="smriti-lookup-modal-form">
            <div class="smriti-lookup-modal-body">
              ${fields.map(f => `
                <div class="smriti-lookup-form-group">
                  <label class="smriti-lookup-label">${f.label} ${f.required ? '<span style="color:red">*</span>':''}</label>
                  <input class="smriti-lookup-input" type="${f.type}" name="${f.name}" ${f.required ? 'required':''} />
                </div>
              `).join("")}
            </div>
            <div class="smriti-lookup-modal-footer">
              <button class="smriti-lookup-btn cancel" type="button">Cancel</button>
              <button class="smriti-lookup-btn submit" type="submit">Save</button>
            </div>
          </form>
        </div>
      `;

      document.body.appendChild(backdrop);
      setTimeout(() => backdrop.classList.add("active"), 10);

      const closeBtn = backdrop.querySelector(".smriti-lookup-modal-close");
      const cancelBtn = backdrop.querySelector(".smriti-lookup-btn.cancel");
      const form = backdrop.querySelector(".smriti-lookup-modal-form");

      const close = () => {
        backdrop.classList.remove("active");
        setTimeout(() => backdrop.remove(), 200);
      };

      closeBtn.addEventListener("click", close);
      cancelBtn.addEventListener("click", close);

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const data = {};
        fields.forEach(f => {
          const inp = form.querySelector(`[name="${f.name}"]`);
          data[f.name] = inp ? inp.value : "";
        });

        const submitBtn = form.querySelector(".smriti-lookup-btn.submit");
        submitBtn.disabled = true;
        submitBtn.textContent = "Saving…";

        try {
          const res = await this.apiCall("create", {
            entity: this.entity,
            data: JSON.stringify(data)
          });
          close();
          this.select(res);
          if (this.onCreate) this.onCreate(res.value, res.label, res.detail);
        } catch(err) {
          alert("Creation failed: " + (err.exc || err.message || "Unknown error"));
          submitBtn.disabled = false;
          submitBtn.textContent = "Save";
        }
      });
    }

    async apiCall(method, args) {
      if (!frappe.csrf_token) {
        frappe.csrf_token = window.csrf_token || window.CSRF_TOKEN || (window.frappe && window.frappe.csrf_token) || "";
      }
      return new Promise((resolve, reject) => {
        const callArgs = {
          method: `${API}.${method}`,
          args: args,
          callback: (r) => {
            if (r.exc) reject(r);
            else resolve(r.message);
          },
          error: (err) => {
            reject(err);
          }
        };
        const token = frappe.csrf_token;
        if (token) {
          callArgs.headers = { "X-Frappe-CSRF-Token": token };
        }
        frappe.call(callArgs);
      });
    }
  }

  window.SmritiSmartLookup = SmritiSmartLookup;
})();
