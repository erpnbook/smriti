/**
 * @file: smriti_matrix_renderer.js
 * @description: Reusable, dynamic Matrix Grid Renderer component for SMRITI Retail OS.
 *               Handles N-dimensional grid layout (2D viewport + filters), keyboard navigation,
 *               Excel paste import, and semantic theme highlights.
 */

class SmritiMatrixRenderer {
  constructor(options) {
    this.container = document.getElementById(options.containerId);
    this.article = options.article;
    this.session = options.session; // MatrixSessionDTO
    this.onChange = options.onChange || (() => {});
    this.onNewVariant = options.onNewVariant || (() => {});
    this.onStateChange = options.onStateChange || (() => {});
    
    this.init();
  }

  init() {
    if (!this.container) return;
    this.render();
    this.setupListeners();
  }

  render() {
    const s = this.session;
    const def = s.definition || { axis_x: "Size", axis_y: "Color" };
    
    // Column header labels (Axis X values)
    const cols = s.sizes;
    // Row header labels (Axis Y values)
    const rows = s.colors;

    let html = `
      <div class="smriti-matrix-wrapper">
        <div class="smriti-matrix-header">
          <div class="matrix-title">📊 Style Matrix: ${s.article}</div>
          <button class="po-btn-add" style="margin-left:auto;padding:4px 8px;font-size:11px;" onclick="document.getElementById('paste-area-${this.article}').style.display='block';">
            📋 Paste from Excel
          </button>
        </div>
        
        <!-- Excel Paste Box -->
        <div id="paste-area-${this.article}" class="paste-box" style="display:none;margin-bottom:12px;padding:12px;background:var(--card);border:1px dashed var(--border);border-radius:8px;">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:6px;">Copy a grid from Excel (including header row & columns) and paste it here:</div>
          <textarea class="fi" id="paste-input-${this.article}" placeholder="Paste cells here..." style="height:60px;font-family:monospace;font-size:11px;"></textarea>
          <div style="display:flex;gap:8px;margin-top:8px;">
            <button class="btn btn-xs btn-primary" onclick="window.matrixInstances['${this.article}'].importFromPaste()">Apply Paste</button>
            <button class="btn btn-xs btn-default" onclick="document.getElementById('paste-area-${this.article}').style.display='none';">Cancel</button>
          </div>
        </div>

        <div class="matrix-table-container">
          <table class="matrix-table" id="matrix-table-${this.article}">
            <thead>
              <tr>
                <th class="sticky-col first-col">${def.axis_y} \\ ${def.axis_x}</th>
                ${cols.map(c => `<th>${c}</th>`).join("")}
                <th class="total-col">Row Total</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map(r => {
                let rowSum = 0;
                return `
                  <tr>
                    <td class="sticky-col first-col" style="font-weight:600;">${r}</td>
                    ${cols.map(c => {
                      const cell = this.getCell(c, r);
                      const qty = cell ? cell.qty || 0 : 0;
                      rowSum += qty;
                      const isNew = cell && cell.variant && !cell.variant.item_code.startsWith(this.article); // newly auto-created variant indicator
                      const highlightClass = isNew ? "smriti-state-new" : "";
                      return `
                        <td>
                          <input type="number" 
                            class="matrix-cell-input ${highlightClass}" 
                            data-x="${c}" 
                            data-y="${r}" 
                            value="${qty > 0 ? qty : ""}" 
                            placeholder="0"
                            min="0"
                            step="1"
                            onchange="window.matrixInstances['${this.article}'].handleCellChange('${c}', '${r}', this.value)"
                          />
                        </td>
                      `;
                    }).join("")}
                    <td class="total-cell row-total" id="row-total-${this.article}-${r.replace(/\s+/g, '_')}">${rowSum}</td>
                  </tr>
                `;
              }).join("")}
              <!-- Bottom Columns Sum Row -->
              <tr class="summary-row">
                <td class="sticky-col first-col" style="font-weight:700;">Column Total</td>
                ${cols.map(c => {
                  const colSum = this.getColTotal(c);
                  return `<td class="total-cell col-total" id="col-total-${this.article}-${c.replace(/\s+/g, '_')}">${colSum}</td>`;
                }).join("")}
                <td class="total-cell grand-total" id="grand-total-${this.article}" style="font-weight:700;color:var(--primary);">${this.getGrandTotal()}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    this.container.innerHTML = html;
    
    // Register global instance for event handlers
    window.matrixInstances = window.matrixInstances || {};
    window.matrixInstances[this.article] = this;
  }

  getCell(x, y) {
    return this.session.cells.find(c => c.x_val === x && c.y_val === y);
  }

  getColTotal(x) {
    return this.session.cells
      .filter(c => c.x_val === x)
      .reduce((sum, c) => sum + (parseFloat(c.qty) || 0), 0);
  }

  getGrandTotal() {
    return this.session.cells.reduce((sum, c) => sum + (parseFloat(c.qty) || 0), 0);
  }

  handleCellChange(x, y, value) {
    const qty = parseFloat(value) || 0;
    let cell = this.getCell(x, y);
    if (!cell) {
      cell = { x_val: x, y_val: y, qty: qty, variant: null };
      this.session.cells.push(cell);
    } else {
      cell.qty = qty;
    }

    // Call onChange
    this.onChange(x, y, qty, cell);
    
    // Recalculate and update UI totals directly in DOM for instant response
    this.updateDomTotals();
  }

  updateDomTotals() {
    const s = this.session;
    // Update row totals
    s.colors.forEach(r => {
      const rowSum = s.cells.filter(c => c.y_val === r).reduce((sum, c) => sum + (parseFloat(c.qty) || 0), 0);
      const el = document.getElementById(`row-total-${this.article}-${r.replace(/\s+/g, '_')}`);
      if (el) el.textContent = rowSum;
    });

    // Update column totals
    s.sizes.forEach(c => {
      const colSum = this.getColTotal(c);
      const el = document.getElementById(`col-total-${this.article}-${c.replace(/\s+/g, '_')}`);
      if (el) el.textContent = colSum;
    });

    // Grand total
    const gt = document.getElementById(`grand-total-${this.article}`);
    if (gt) gt.textContent = this.getGrandTotal();

    this.onStateChange();
  }

  importFromPaste() {
    const ta = document.getElementById(`paste-input-${this.article}`);
    if (!ta) return;
    const text = ta.value;
    if (!text.trim()) return;

    // Parser client-side
    const sep = text.includes('\t') ? '\t' : (text.includes(',') ? ',' : ' ');
    const lines = text.trim().split('\n').map(l => l.split(sep).map(c => c.trim()));
    if (!lines.length) return;
    
    const headers = lines[0].slice(1).filter(h => h);
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      if (!line || !line.length) continue;
      const rowHeader = line[0];
      for (let j = 1; j < line.length; j++) {
        if (j - 1 < headers.length) {
          const qty = parseFloat(line[j]);
          if (qty >= 0) {
            const x = headers[j - 1];
            const y = rowHeader;
            const cell = this.getCell(x, y);
            if (cell) {
              cell.qty = qty;
              // Update input in UI
              const input = this.container.querySelector(`input[data-x="${x}"][data-y="${y}"]`);
              if (input) input.value = qty > 0 ? qty : "";
            }
          }
        }
      }
    }
    
    // Hide pastebox and refresh totals
    document.getElementById(`paste-area-${this.article}`).style.display = 'none';
    ta.value = "";
    this.updateDomTotals();
    toast("success", "Imported", "Excel paste grid applied successfully!");
  }

  setupListeners() {
    // Arrow Key Navigation
    const inputs = this.container.querySelectorAll(".matrix-cell-input");
    inputs.forEach(input => {
      input.addEventListener("keydown", (e) => {
        const x = input.getAttribute("data-x");
        const y = input.getAttribute("data-y");
        const sizes = this.session.sizes;
        const colors = this.session.colors;
        let targetX = x;
        let targetY = y;
        
        let move = false;
        
        if (e.key === "ArrowRight" || e.key === "Tab" && !e.shiftKey) {
          const idx = sizes.indexOf(x);
          if (idx < sizes.length - 1) {
            targetX = sizes[idx + 1];
            move = true;
          } else {
            const cIdx = colors.indexOf(y);
            if (cIdx < colors.length - 1) {
              targetY = colors[cIdx + 1];
              targetX = sizes[0];
              move = true;
            }
          }
        } else if (e.key === "ArrowLeft" || e.key === "Tab" && e.shiftKey) {
          const idx = sizes.indexOf(x);
          if (idx > 0) {
            targetX = sizes[idx - 1];
            move = true;
          } else {
            const cIdx = colors.indexOf(y);
            if (cIdx > 0) {
              targetY = colors[cIdx - 1];
              targetX = sizes[sizes.length - 1];
              move = true;
            }
          }
        } else if (e.key === "ArrowUp") {
          const cIdx = colors.indexOf(y);
          if (cIdx > 0) {
            targetY = colors[cIdx - 1];
            move = true;
          }
        } else if (e.key === "ArrowDown") {
          const cIdx = colors.indexOf(y);
          if (cIdx < colors.length - 1) {
            targetY = colors[cIdx + 1];
            move = true;
          }
        }
        
        if (move) {
          e.preventDefault();
          const nextInput = this.container.querySelector(`input[data-x="${targetX}"][data-y="${targetY}"]`);
          if (nextInput) nextInput.focus();
        }
      });
    });
  }
}
