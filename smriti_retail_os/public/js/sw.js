/**
 * @file: smriti_retail_os/public/js/sw.js
 * @description: Advanced SMRITI Retail OS Service Worker — Phase 1-3 PWA implementation.
 *               Cache strategies, offline fallback, IndexedDB background sync,
 *               and push notification support.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-04
 * @version: 2.0.0
 * @license: MIT
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Retail OS — Advanced PWA Service Worker v2.0
   Phase 1: Foundation cache
   Phase 2: Multi-strategy smart caching
   Phase 3: Offline IndexedDB + Background Sync
   Phase 4: Push notifications
   ============================================================ */

const CACHE_VERSION     = 'smriti-v2.1';
const STATIC_CACHE      = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE     = `${CACHE_VERSION}-dynamic`;
const OFFLINE_URL       = '/offline';

// ── Static assets — always cache on install ─────────────────
const STATIC_ASSETS = [
    '/offline',
    '/assets/smriti_retail_os/css/smriti_theme.css',
    '/assets/smriti_retail_os/css/smriti_sidebar.css',
    '/assets/smriti_retail_os/css/smriti_branding.css',
    '/assets/smriti_retail_os/css/smriti-reports.css',
    '/assets/smriti_retail_os/css/smriti_sales_invoice.css',
    '/assets/smriti_retail_os/js/smriti_sidebar.js',
    '/assets/smriti_retail_os/js/main.js',
    '/assets/smriti_retail_os/js/smriti_payload_bridge.js',
    '/assets/smriti_retail_os/js/smriti_pwa.js',
    '/assets/smriti_retail_os/js/smriti_offline_store.js',
    '/assets/smriti_retail_os/images/logo.svg',
];

// ── Cache routing strategies ─────────────────────────────────
const CACHE_STRATEGIES = {
    // Cache first — static assets that rarely change
    cacheFirst:           ['/assets/', '/files/', '/favicon'],
    // Network first — live API data; fall back to cache if offline
    networkFirst:         ['/api/', '/method/'],
    // Stale While Revalidate — SMRITI pages: serve cached instantly, update in background
    // POLICY: /desk is NOT a SMRITI route and must NOT be cached by the service worker.
    staleWhileRevalidate: [
        '/billing', '/sizewise_invoice', '/purchase', '/sizewise_item',
        '/smriti', '/inventory', '/eway_bill', '/customers', '/suppliers',
        '/item_master', '/security', '/platform_center', '/shift', '/barcode',
        '/products', '/sales_invoices', '/configure'
    ],
};

// ── INSTALL — pre-cache static assets ───────────────────────
self.addEventListener('install', event => {
    console.log('[SMRITI SW v2] Installing — pre-caching static assets');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => cache.addAll(STATIC_ASSETS))
            .then(() => {
                console.log('[SMRITI SW v2] Static assets cached ✅');
                return self.skipWaiting();
            })
            .catch(err => console.error('[SMRITI SW v2] Pre-cache failed:', err))
    );
});

// ── ACTIVATE — purge old cache versions ─────────────────────
self.addEventListener('activate', event => {
    console.log('[SMRITI SW v2] Activating — clearing old caches');
    event.waitUntil(
        caches.keys()
            .then(keys => Promise.all(
                keys
                    .filter(k => k !== STATIC_CACHE && k !== DYNAMIC_CACHE)
                    .map(k => {
                        console.log('[SMRITI SW v2] Deleting old cache:', k);
                        return caches.delete(k);
                    })
            ))
            .then(() => self.clients.claim())
    );
});

// ── FETCH — apply cache strategy per URL pattern ─────────────
self.addEventListener('fetch', event => {
    // Only handle GET requests
    if (event.request.method !== 'GET') return;

    const url = new URL(event.request.url);

    // Skip cross-origin requests
    if (url.origin !== location.origin) return;

    // API / method calls — Network First
    if (CACHE_STRATEGIES.networkFirst.some(p => url.pathname.startsWith(p))) {
        event.respondWith(networkFirst(event.request));
        return;
    }

    // Static assets — Cache First
    if (CACHE_STRATEGIES.cacheFirst.some(p => url.pathname.startsWith(p))) {
        event.respondWith(cacheFirst(event.request));
        return;
    }

    // SMRITI page routes — Stale While Revalidate
    if (CACHE_STRATEGIES.staleWhileRevalidate.some(p => url.pathname.startsWith(p))) {
        event.respondWith(staleWhileRevalidate(event.request));
        return;
    }

    // Default — network with offline HTML fallback
    event.respondWith(
        fetch(event.request)
            .catch(() => {
                if (event.request.mode === 'navigate') {
                    return caches.match(OFFLINE_URL);
                }
                return new Response('', { status: 503 });
            })
    );
});

// ── Strategy: Cache First ────────────────────────────────────
async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) return cached;
    try {
        const response = await fetch(request);
        if (response && response.status === 200) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        return new Response('', { status: 503 });
    }
}

// ── Strategy: Network First ──────────────────────────────────
async function networkFirst(request) {
    try {
        const response = await fetch(request);
        if (response && response.status === 200) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        const cached = await caches.match(request);
        if (cached) return cached;
        // Offline JSON error for API callers
        return new Response(
            JSON.stringify({ message: 'Offline', error: 'No network connection', offline: true }),
            { status: 503, headers: { 'Content-Type': 'application/json' } }
        );
    }
}

// ── Strategy: Stale While Revalidate ─────────────────────────
async function staleWhileRevalidate(request) {
    const cache       = await caches.open(DYNAMIC_CACHE);
    const cached      = await cache.match(request);
    const fetchPromise = fetch(request)
        .then(response => {
            if (response && response.status === 200) {
                cache.put(request, response.clone());
            }
            return response;
        })
        .catch(() => cached);
    return cached || fetchPromise;
}

// ── BACKGROUND SYNC — offline invoice queue ──────────────────
self.addEventListener('sync', event => {
    console.log('[SMRITI SW v2] Background sync triggered:', event.tag);

    if (event.tag === 'sync-pending-invoices') {
        event.waitUntil(syncPendingInvoices());
    }
    if (event.tag === 'sync-pending-items') {
        event.waitUntil(syncPendingItemUpdates());
    }
});

async function syncPendingInvoices() {
    const db = await openSmritiDB();
    const tx = db.transaction('pending_invoices', 'readonly');
    const store = tx.objectStore('pending_invoices');

    const pending = await idbGetAll(store);
    console.log(`[SMRITI SW v2] Syncing ${pending.length} pending invoice(s)`);

    for (const invoice of pending) {
        try {
            const response = await fetch('/api/method/smriti_retail_os.billing_api.save_invoice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': invoice.csrf || 'fetch'
                },
                body: JSON.stringify({ payload: invoice.payload })
            });

            if (response.ok) {
                // Remove from queue
                const delTx = db.transaction('pending_invoices', 'readwrite');
                await idbDelete(delTx.objectStore('pending_invoices'), invoice.id);

                // Log success
                const logTx = db.transaction('sync_log', 'readwrite');
                await idbAdd(logTx.objectStore('sync_log'), {
                    action: 'invoice_synced',
                    detail: `Invoice for ${invoice.payload?.customer || 'customer'} synced`,
                    timestamp: Date.now()
                });

                // Notify user
                if (self.registration.showNotification) {
                    await self.registration.showNotification('SMRITI — Invoice Synced ✅', {
                        body: `Invoice for ${invoice.payload?.customer || 'customer'} synced successfully`,
                        icon: '/assets/smriti_retail_os/images/icon-192.png',
                        badge: '/assets/smriti_retail_os/images/icon-192.png',
                        tag: `invoice-sync-${invoice.id}`,
                        data: { url: '/billing' }
                    });
                }
            }
        } catch (err) {
            console.error('[SMRITI SW v2] Invoice sync failed:', invoice.id, err);
        }
    }
}

async function syncPendingItemUpdates() {
    // Placeholder for future item draft sync
    console.log('[SMRITI SW v2] Item sync check — no pending updates');
}

// ── PUSH NOTIFICATIONS ────────────────────────────────────────
self.addEventListener('push', event => {
    console.log('[SMRITI SW v2] Push received');
    const data = event.data?.json() || {};
    event.waitUntil(
        self.registration.showNotification(data.title || 'SMRITI Retail OS', {
            body:  data.body  || 'You have a new notification',
            icon:  '/assets/smriti_retail_os/images/icon-192.png',
            badge: '/assets/smriti_retail_os/images/icon-192.png',
            data:  { url: data.url || '/smriti' }, // POLICY: never /desk as fallback
            vibrate: [200, 100, 200],
            tag: data.tag || 'smriti-notification'
        })
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(clientList => {
                // POLICY (AITDL Rule 7): push notification target must be a SMRITI page, never /desk
                const target = event.notification.data?.url || '/smriti';
                for (const client of clientList) {
                    if (client.url.includes(target) && 'focus' in client) {
                        return client.focus();
                    }
                }
                return clients.openWindow(target);
            })
    );
});

// ── IndexedDB Helpers ─────────────────────────────────────────
function openSmritiDB() {
    return new Promise((resolve, reject) => {
        const req = indexedDB.open('SmritiRetailOS', 1);
        req.onupgradeneeded = e => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains('pending_invoices'))
                db.createObjectStore('pending_invoices', { keyPath: 'id', autoIncrement: true });
            if (!db.objectStoreNames.contains('items_cache'))
                db.createObjectStore('items_cache', { keyPath: 'item_code' });
            if (!db.objectStoreNames.contains('customers_cache'))
                db.createObjectStore('customers_cache', { keyPath: 'name' });
            if (!db.objectStoreNames.contains('sync_log'))
                db.createObjectStore('sync_log', { keyPath: 'id', autoIncrement: true });
        };
        req.onsuccess = e => resolve(e.target.result);
        req.onerror   = e => reject(e.target.error);
    });
}

function idbGetAll(store) {
    return new Promise((resolve, reject) => {
        const req = store.getAll();
        req.onsuccess = () => resolve(req.result);
        req.onerror   = () => reject(req.error);
    });
}

function idbDelete(store, key) {
    return new Promise((resolve, reject) => {
        const req = store.delete(key);
        req.onsuccess = () => resolve();
        req.onerror   = () => reject(req.error);
    });
}

function idbAdd(store, data) {
    return new Promise((resolve, reject) => {
        const req = store.add(data);
        req.onsuccess = () => resolve(req.result);
        req.onerror   = () => reject(req.error);
    });
}
