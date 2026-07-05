---
Document ID: "USER-006"
Title: "SMRITI OS Offline POS Operations & PWA Architecture Guide"
Owner: "Operations Team"
Audience: "End User"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI OS Offline POS Operations & PWA Architecture Guide

> **Author:** Jawahar R Mallah (<jawahar.mallah@gmail.com>)  
> **Last Updated:** 2026-06-19  

This guide details the Progressive Web App (PWA) offline checkout architecture, local data structures, and support instructions for SMRITI Retail OS.

## 🧱 Architectural Overview

SMRITI POS employs a Service Worker and IndexedDB-based queue to ensure cashiers can continue checkout operations during complete network blackouts.

```
┌────────────────────────────────────────────────────────┐
│                  SMRITI Web UI (POS)                    │
│   Online: REST API Checkout     Offline: IDB Queue     │
└───────────┬───────────────────────────────┬────────────┘
            │ (REST fails / offline)        │ (Restored)
            ▼                               ▼
┌────────────────────────┐       ┌──────────────────────┐
│  IndexedDB Database    │       │   Service Worker     │
│  Store: pending_invoices│ ────> │   Auto-Sync Handler  │
└────────────────────────┘       └──────────┬───────────┘
                                            │
                                            ▼
                                 ┌──────────────────────┐
                                 │ ERPNext Sales Invoice│
                                 └──────────────────────┘
```

### 1. Service Worker Scope & Serving
*   **MIME-type Enforcer**: In Frappe, dynamic routes are served as `text/html`. SMRITI overrides this by intercepting `/sw.js` at the `before_request` hook level inside `boot.py`, raising a Werkzeug response exception to serve `/sw.js` with `Content-Type: application/javascript; charset=utf-8` and `Service-Worker-Allowed: /`.
*   **Scope**: The Service Worker registers at scope `/` so it can control all standalone POS routes (`/billing`, `/smriti`, etc.) and intercept cache requests.

### 2. Local Data Queuing
*   When a cashier clicks **Pay** offline:
    1. The REST API network connection fails or `navigator.onLine` evaluates to `false`.
    2. SMRITI catches the exception and prompts the user that they are offline.
    3. The payload is passed to `window.SmritiOfflineStore.savePendingInvoice(payload, CSRF_TOKEN)`.
    4. The payload is saved in browser IndexedDB under database `SmritiRetailOS`, object store `pending_invoices`.
    5. The cart resets, allowing the cashier to scan the next customer's items.

---

## 🟢 Online / Offline Status Badge

*   The POS header contains a status badge `#network-status` representing connection integrity:
    *   `🟢 Online`: SMRITI communicates directly with the server.
    *   `🔴 Offline`: SMRITI is operating in offline mode. Invoices will be queued locally.

---

## 🔄 Automatic Background Sync

Once the network connection is restored:
1. SMRITI's Service Worker registers a `sync` event or periodically attempts background reconnection.
2. It fetches all pending transactions from the local `pending_invoices` store in chronological (FIFO) order.
3. It sends the payload using the standard billing API (`smriti_retail_os.billing.api.checkout`).
4. If successful, it shows a browser notification to the cashier and deletes the synced transaction from IndexedDB.

---

## 🛠️ Verification & Support Commands

### 1. View Local IndexedDB Queue
Support engineers can inspect the offline queue in the browser:
1. Open DevTools (`F12`) -> **Application** -> **IndexedDB** -> **SmritiRetailOS** -> **pending_invoices**.
2. Each record shows the invoice JSON payload including item lists, pricing, and cashier ID.

### 2. Manual Re-Sync Trigger
If background sync is delayed, trigger synchronization via the console:
```javascript
window.SmritiOfflineStore.syncPendingInvoices();
```

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL