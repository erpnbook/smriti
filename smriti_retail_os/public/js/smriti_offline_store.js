/**
 * @file: smriti_retail_os/public/js/smriti_offline_store.js
 * @description: SMRITI Retail OS — IndexedDB Offline Data Store.
 *               Manages pending invoices, item cache, customer cache,
 *               and sync log for offline-first POS operation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-04
 * @version: 1.8.6
 * @license: MIT
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Offline Store — IndexedDB Layer
   Stores:
     pending_invoices  → Offline POS bills awaiting sync
     items_cache       → Product catalog for offline scan
     customers_cache   → Customer list for offline lookup
     sync_log          → Audit trail of sync operations
   ============================================================ */

const SmritiOfflineStore = {

    db:      null,
    DB_NAME: 'SmritiRetailOS',
    DB_VER:  1,

    // ── Init ─────────────────────────────────────────────────
    async init() {
        try {
            this.db = await this._openDB();
            console.log('[SMRITI Offline Store] IndexedDB ready ✅');
        } catch (err) {
            console.error('[SMRITI Offline Store] Failed to open IndexedDB:', err);
        }
        return this;
    },

    _openDB() {
        return new Promise((resolve, reject) => {
            const req = indexedDB.open(this.DB_NAME, this.DB_VER);

            req.onupgradeneeded = e => {
                const db = e.target.result;
                console.log('[SMRITI Offline Store] Creating/upgrading schema');

                if (!db.objectStoreNames.contains('pending_invoices')) {
                    const s = db.createObjectStore('pending_invoices', { keyPath: 'id', autoIncrement: true });
                    s.createIndex('status',    'status',    { unique: false });
                    s.createIndex('timestamp', 'timestamp', { unique: false });
                }
                if (!db.objectStoreNames.contains('items_cache')) {
                    const s = db.createObjectStore('items_cache', { keyPath: 'item_code' });
                    s.createIndex('item_group', 'item_group', { unique: false });
                    s.createIndex('item_name',  'item_name',  { unique: false });
                }
                if (!db.objectStoreNames.contains('customers_cache')) {
                    const s = db.createObjectStore('customers_cache', { keyPath: 'name' });
                    s.createIndex('customer_name', 'customer_name', { unique: false });
                    s.createIndex('mobile_no',     'mobile_no',     { unique: false });
                }
                if (!db.objectStoreNames.contains('sync_log')) {
                    const s = db.createObjectStore('sync_log', { keyPath: 'id', autoIncrement: true });
                    s.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };

            req.onsuccess = e => resolve(e.target.result);
            req.onerror   = e => reject(e.target.error);
        });
    },

    // ── Guard helper ─────────────────────────────────────────
    _requireDB() {
        if (!this.db) throw new Error('[SMRITI Offline Store] DB not initialized. Call init() first.');
    },

    _idbRequest(req) {
        return new Promise((resolve, reject) => {
            req.onsuccess = () => resolve(req.result);
            req.onerror   = () => reject(req.error);
        });
    },

    // ═══════════════════════════════════════════════════════
    // PENDING INVOICES
    // ═══════════════════════════════════════════════════════

    /**
     * Save a POS invoice to the offline queue.
     * @param {Object} payload  - The billing payload (items, customer, etc.)
     * @param {string} csrf     - CSRF token captured at time of billing
     * @returns {number} id     - The auto-assigned queue ID
     */
    async savePendingInvoice(payload, csrf = '') {
        this._requireDB();
        const tx    = this.db.transaction('pending_invoices', 'readwrite');
        const store = tx.objectStore('pending_invoices');
        const id    = await this._idbRequest(store.add({
            payload,
            csrf,
            timestamp:   Date.now(),
            status:      'pending',
            retry_count: 0
        }));
        await this.logSync('invoice_queued', `Invoice queued for ${payload?.customer || 'Walk-in'} (id: ${id})`);
        console.log(`[SMRITI Offline Store] Invoice queued — id: ${id}`);
        return id;
    },

    /** Get all pending invoices from the queue */
    async getPendingInvoices() {
        this._requireDB();
        const tx = this.db.transaction('pending_invoices', 'readonly');
        return this._idbRequest(tx.objectStore('pending_invoices').getAll());
    },

    /** Count pending invoices (for offline badge display) */
    async countPendingInvoices() {
        this._requireDB();
        const tx = this.db.transaction('pending_invoices', 'readonly');
        return this._idbRequest(tx.objectStore('pending_invoices').count());
    },

    /** Remove a synced invoice from the queue */
    async deletePendingInvoice(id) {
        this._requireDB();
        const tx = this.db.transaction('pending_invoices', 'readwrite');
        await this._idbRequest(tx.objectStore('pending_invoices').delete(id));
        console.log(`[SMRITI Offline Store] Invoice removed from queue — id: ${id}`);
    },

    /** Mark an invoice's retry count on transient failure */
    async incrementRetry(id) {
        this._requireDB();
        const tx       = this.db.transaction('pending_invoices', 'readwrite');
        const store    = tx.objectStore('pending_invoices');
        const invoice  = await this._idbRequest(store.get(id));
        if (invoice) {
            invoice.retry_count = (invoice.retry_count || 0) + 1;
            invoice.status      = invoice.retry_count >= 5 ? 'failed' : 'pending';
            await this._idbRequest(store.put(invoice));
        }
    },

    // ═══════════════════════════════════════════════════════
    // ITEMS CACHE
    // ═══════════════════════════════════════════════════════

    /**
     * Bulk cache a list of items for offline lookup.
     * @param {Array} items - Array of item objects (must have item_code)
     */
    async cacheItems(items) {
        this._requireDB();
        const tx    = this.db.transaction('items_cache', 'readwrite');
        const store = tx.objectStore('items_cache');
        let count   = 0;
        for (const item of items) {
            await this._idbRequest(store.put({ ...item, _cached_at: Date.now() }));
            count++;
        }
        console.log(`[SMRITI Offline Store] Cached ${count} items`);
        await this.logSync('items_cached', `${count} items cached at ${new Date().toLocaleTimeString()}`);
    },

    /** Fetch a single item by item_code */
    async getCachedItem(item_code) {
        this._requireDB();
        const tx = this.db.transaction('items_cache', 'readonly');
        return this._idbRequest(tx.objectStore('items_cache').get(item_code));
    },

    /**
     * Search cached items by item_code or item_name (substring match).
     * @param {string} query
     * @returns {Array} matching items (max 20)
     */
    async searchCachedItems(query) {
        this._requireDB();
        const q   = (query || '').toLowerCase().trim();
        if (!q) return [];
        const tx  = this.db.transaction('items_cache', 'readonly');
        const all = await this._idbRequest(tx.objectStore('items_cache').getAll());
        return all
            .filter(item =>
                (item.item_code  || '').toLowerCase().includes(q) ||
                (item.item_name  || '').toLowerCase().includes(q) ||
                (item.custom_mrp || '').toString().includes(q)
            )
            .slice(0, 20);
    },

    /** Count total items in cache */
    async countCachedItems() {
        this._requireDB();
        const tx = this.db.transaction('items_cache', 'readonly');
        return this._idbRequest(tx.objectStore('items_cache').count());
    },

    // ═══════════════════════════════════════════════════════
    // CUSTOMERS CACHE
    // ═══════════════════════════════════════════════════════

    /**
     * Bulk cache customers for offline lookup.
     * @param {Array} customers - Array of customer objects (must have name)
     */
    async cacheCustomers(customers) {
        this._requireDB();
        const tx    = this.db.transaction('customers_cache', 'readwrite');
        const store = tx.objectStore('customers_cache');
        let count   = 0;
        for (const c of customers) {
            await this._idbRequest(store.put({ ...c, _cached_at: Date.now() }));
            count++;
        }
        console.log(`[SMRITI Offline Store] Cached ${count} customers`);
    },

    /**
     * Search cached customers by name or mobile.
     * @param {string} query
     * @returns {Array} matching customers (max 10)
     */
    async searchCachedCustomers(query) {
        this._requireDB();
        const q   = (query || '').toLowerCase().trim();
        if (!q) return [];
        const tx  = this.db.transaction('customers_cache', 'readonly');
        const all = await this._idbRequest(tx.objectStore('customers_cache').getAll());
        return all
            .filter(c =>
                (c.name          || '').toLowerCase().includes(q) ||
                (c.customer_name || '').toLowerCase().includes(q) ||
                (c.mobile_no     || '').includes(q)
            )
            .slice(0, 10);
    },

    // ═══════════════════════════════════════════════════════
    // SYNC LOG
    // ═══════════════════════════════════════════════════════

    /**
     * Write an entry to the sync audit log.
     * @param {string} action  - Action name e.g. 'invoice_synced'
     * @param {string} detail  - Human-readable description
     */
    async logSync(action, detail) {
        if (!this.db) return; // silently skip if DB not ready
        try {
            const tx = this.db.transaction('sync_log', 'readwrite');
            await this._idbRequest(tx.objectStore('sync_log').add({
                action,
                detail,
                timestamp: Date.now()
            }));
        } catch (err) {
            console.warn('[SMRITI Offline Store] logSync failed:', err);
        }
    },

    /** Get recent sync log entries */
    async getSyncLog(limit = 50) {
        this._requireDB();
        const tx  = this.db.transaction('sync_log', 'readonly');
        const all = await this._idbRequest(tx.objectStore('sync_log').getAll());
        return all
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, limit);
    },

    // ═══════════════════════════════════════════════════════
    // UTILITY
    // ═══════════════════════════════════════════════════════

    /** Get a summary of all store counts (for status display) */
    async getStoreSummary() {
        const [pending, items, customers] = await Promise.all([
            this.countPendingInvoices().catch(() => 0),
            this.countCachedItems().catch(() => 0),
            this.db ? this._idbRequest(
                this.db.transaction('customers_cache', 'readonly')
                    .objectStore('customers_cache').count()
            ).catch(() => 0) : 0
        ]);
        return { pending_invoices: pending, cached_items: items, cached_customers: customers };
    }
};

// ── Auto-init ─────────────────────────────────────────────────
SmritiOfflineStore.init();

// ── Global expose ─────────────────────────────────────────────
window.SmritiOfflineStore = SmritiOfflineStore;
