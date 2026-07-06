/**
 * @file: smriti_retail_os/public/js/smriti_pwa.js
 * @description: SMRITI Retail OS — PWA Registration, Install Prompt, Offline Detection,
 *               Background Sync trigger, and Update Banner.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-04
 * @version: 1.8.6
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI PWA Controller
   ─ Service Worker registration + update detection
   ─ Install prompt (beforeinstallprompt)
   ─ Online/offline detection + toast
   ─ Background sync trigger when back online
   ─ Update available banner
   ============================================================ */

const SMRITI_PWA = {

    deferredPrompt:  null,
    swRegistration:  null,
    isOnline:        navigator.onLine,

    // ── Boot ──────────────────────────────────────────────────
    init() {
        this.registerServiceWorker();
        this.setupInstallPrompt();
        this.setupOfflineDetection();
        this.injectManifestLink();
        console.log('[SMRITI PWA] Initialized');
    },

    // ── Service Worker Registration ───────────────────────────
    async registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            console.warn('[SMRITI PWA] Service Worker not supported in this browser');
            return;
        }
        try {
            // SW must be served from root — routed via website_route_rules in hooks.py
            const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
            this.swRegistration = reg;
            console.log('[SMRITI PWA] Service Worker registered ✅  scope:', reg.scope);

            // Check for pending updates immediately
            reg.update();

            // Watch for new SW installing
            reg.addEventListener('updatefound', () => {
                const newSW = reg.installing;
                if (!newSW) return;
                newSW.addEventListener('statechange', () => {
                    if (newSW.state === 'installed' && navigator.serviceWorker.controller) {
                        // New version waiting — show banner
                        this.showUpdateBanner(newSW);
                    }
                });
            });

        } catch (err) {
            console.error('[SMRITI PWA] Service Worker registration failed:', err);
        }
    },

    // ── Install Prompt (Add to Home Screen) ───────────────────
    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', e => {
            e.preventDefault();
            this.deferredPrompt = e;
            console.log('[SMRITI PWA] Install prompt captured');
            this._showInstallButton();
        });

        window.addEventListener('appinstalled', () => {
            console.log('[SMRITI PWA] App successfully installed 🎉');
            this._hideInstallButton();
            this.deferredPrompt = null;
            if (typeof frappe !== 'undefined' && frappe.show_alert) {
                frappe.show_alert({ message: 'SMRITI installed as an app!', indicator: 'green' }, 4);
            }
        });
    },

    async triggerInstall() {
        if (!this.deferredPrompt) {
            console.warn('[SMRITI PWA] No install prompt available');
            return;
        }
        this.deferredPrompt.prompt();
        const { outcome } = await this.deferredPrompt.userChoice;
        console.log('[SMRITI PWA] User install choice:', outcome);
        this.deferredPrompt = null;
        this._hideInstallButton();
    },

    _showInstallButton() {
        const btn = document.getElementById('pwa-install-btn');
        if (btn) btn.style.display = 'flex';
    },

    _hideInstallButton() {
        const btn = document.getElementById('pwa-install-btn');
        if (btn) btn.style.display = 'none';
    },

    // ── Offline / Online Detection ────────────────────────────
    setupOfflineDetection() {
        const update = () => {
            this.isOnline = navigator.onLine;
            this._updateNetworkBadge();
            if (this.isOnline) {
                this._showToast('🟢 Back online — syncing pending data…', 'green');
                this.triggerBackgroundSync();
            } else {
                this._showToast('📡 You are offline — data will sync when reconnected', 'orange');
            }
        };
        window.addEventListener('online',  update);
        window.addEventListener('offline', update);
        // Set initial badge on load
        setTimeout(() => this._updateNetworkBadge(), 500);
    },

    _updateNetworkBadge() {
        const el = document.getElementById('network-status');
        if (!el) return;
        el.textContent = this.isOnline ? '🟢 Online' : '🔴 Offline';
        el.style.color  = this.isOnline ? '#10b981'  : '#ef4444';
    },

    _showToast(message, color) {
        // Frappe toast if available
        if (typeof frappe !== 'undefined' && frappe.show_alert) {
            frappe.show_alert({ message, indicator: color || 'blue' }, 5);
            return;
        }
        // Fallback vanilla toast
        const toast = document.createElement('div');
        toast.style.cssText = `
            position:fixed; bottom:24px; left:50%; transform:translateX(-50%) translateY(80px);
            background:#1e293b; color:#e2e8f0; padding:12px 24px; border-radius:10px;
            z-index:99999; font-family:system-ui,sans-serif; font-size:0.9rem;
            border:1px solid rgba(255,255,255,0.1); box-shadow:0 8px 32px rgba(0,0,0,0.4);
            transition:transform 0.3s ease;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(-50%) translateY(0)';
        });
        setTimeout(() => {
            toast.style.transform = 'translateX(-50%) translateY(80px)';
            setTimeout(() => toast.remove(), 350);
        }, 4000);
    },

    // ── Background Sync Trigger ───────────────────────────────
    async triggerBackgroundSync() {
        if (!this.swRegistration) return;
        if (!('sync' in this.swRegistration)) {
            console.warn('[SMRITI PWA] Background Sync API not supported');
            return;
        }
        try {
            await this.swRegistration.sync.register('sync-pending-invoices');
            await this.swRegistration.sync.register('sync-pending-items');
            console.log('[SMRITI PWA] Background sync registered ✅');
        } catch (err) {
            console.error('[SMRITI PWA] Background sync registration failed:', err);
        }
    },

    // ── Update Banner ─────────────────────────────────────────
    showUpdateBanner(newSW) {
        // Remove any existing banner
        const existing = document.getElementById('smriti-update-banner');
        if (existing) existing.remove();

        const banner = document.createElement('div');
        banner.id = 'smriti-update-banner';
        banner.style.cssText = `
            position:fixed; bottom:20px; left:50%; transform:translateX(-50%);
            background:linear-gradient(135deg,#0f766e,#0d9488);
            color:white; padding:12px 20px; border-radius:12px;
            z-index:99999; display:flex; gap:12px; align-items:center;
            box-shadow:0 8px 32px rgba(15,118,110,0.4);
            font-family:system-ui,sans-serif; font-size:0.9rem;
            border:1px solid rgba(255,255,255,0.2);
            animation: slideUp 0.3s ease;
        `;
        banner.innerHTML = `
            <span>🔄 New version of SMRITI available!</span>
            <button id="smriti-update-now" style="
                background:white; color:#0f766e; border:none;
                padding:6px 14px; border-radius:6px; cursor:pointer;
                font-weight:600; font-size:0.85rem;
            ">Update Now</button>
            <button id="smriti-update-dismiss" style="
                background:transparent; color:rgba(255,255,255,0.7);
                border:none; cursor:pointer; font-size:1.1rem; padding:0 4px;
            ">✕</button>
        `;
        document.body.appendChild(banner);

        document.getElementById('smriti-update-now').onclick = () => {
            if (newSW) newSW.postMessage({ action: 'skipWaiting' });
            window.location.reload();
        };
        document.getElementById('smriti-update-dismiss').onclick = () => {
            banner.remove();
        };
    },

    // ── Manifest Link Injection ───────────────────────────────
    injectManifestLink() {
        if (!document.querySelector('link[rel="manifest"]')) {
            const link  = document.createElement('link');
            link.rel    = 'manifest';
            link.href   = '/assets/smriti_retail_os/manifest.json';
            document.head.appendChild(link);
            console.log('[SMRITI PWA] manifest.json injected into <head>');
        }
    },

    // ── Request Push Notification Permission ──────────────────
    async requestPushPermission() {
        if (!('Notification' in window)) return;
        const permission = await Notification.requestPermission();
        console.log('[SMRITI PWA] Notification permission:', permission);
        return permission;
    }
};

// ── Auto-init on load ─────────────────────────────────────────
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SMRITI_PWA.init());
} else {
    SMRITI_PWA.init();
}

// ── Global expose ─────────────────────────────────────────────
window.SMRITI_PWA = SMRITI_PWA;
