---
Document ID: "KB-UIE-001"
Title: "SMRITI UIE — TallyPrime Integration Setup & Troubleshooting"
Owner: "Support Team"
Audience: "End User"
Module: "UIE"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "USER-031"
Related Modules: "Billing, Purchase Studio"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI UIE — TallyPrime Integration Setup & Troubleshooting

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Date:** 2026-07-02

---

## Overview

SMRITI UIE (Universal Integration Engine) provides bidirectional data synchronization between SMRITI Retail OS and TallyPrime. SMRITI remains the system of record for inventory, purchase, and sales transactions. TallyPrime serves as the accounting book.

**What syncs:**
- Sales Invoices (on submit)
- Purchase Invoices (on submit)
- Debit Notes / Credit Notes
- Payment Entries
- Customer and Ledger Masters (auto-created on first sync)

**What does NOT sync:**
- ERPNext General Ledger entries (Tally owns this)
- ERPNext Chart of Accounts
- Inventory valuation (remains in ERPNext)

---

## Step-by-Step Setup

### Step 1 — Enable TallyPrime Data Bridge

In TallyPrime:
1. Open TallyPrime → Gateway of Tally → Configure → Advanced Configuration
2. Enable **ODBC Server** (or Tally Data Bridge depending on version)
3. Note the **port number** (default: 9000)
4. Ensure TallyPrime is running when sync is needed

### Step 2 — Configure UIE Credentials in SMRITI

1. Go to **SMRITI → Connectivity → UIE Integration Center** (`/smriti-uie`)
2. Click **New Credential**
3. Fill in:
   - **Name:** TallyPrime Main
   - **Adapter Type:** Tally
   - **Host:** localhost (or IP if Tally is on a different machine)
   - **Port:** 9000 (or your configured port)
4. Click **Test Connection**
5. If successful, the credential shows a green ✅

### Step 3 — Configure Tally Settings

1. In UIE Integration Center → **Tally Settings**
2. Set **Company Name** (must exactly match the company name in TallyPrime)
3. Set **Auto Create Ledgers: Yes** (recommended for first sync)
4. Set **Reference Number Field:** `Bill No` (maps SMRITI bill_no to Tally reference)
5. Save

### Step 4 — First Sync

UIE syncs automatically when a Sales Invoice is submitted.

To manually trigger a sync:
1. Go to UIE Integration Center → **Sync Queue**
2. Click **Trigger Manual Sync**
3. Watch the sync log for results

---

## Sync Log — Understanding Status Codes

| Status | Meaning |
|---|---|
| Queued | Waiting to be dispatched |
| Processing | Currently being sent to Tally |
| Completed | Successfully posted to Tally |
| Failed | Error occurred — see `error_message` field |
| Skipped | Zero-value voucher, not posted (by design) |
| Duplicate | Idempotency key matched — already posted |

---

## Auto Ledger Creation

On first sync, SMRITI UIE automatically creates the following ledgers in TallyPrime if they don't exist:

| SMRITI Concept | Tally Ledger Created |
|---|---|
| Customer (first invoice) | Customer name under Sundry Debtors |
| Sales account | Mapped from SMRITI Sales settings |
| Cash/Bank payment | Mapped from SMRITI payment modes |
| Tax (CGST/SGST/IGST) | Mapped under Duties & Taxes |

> Ledger names are sourced from **UIE Tally Settings → Ledger Mapping**.

---

## Troubleshooting UIE Issues

### Issue UIE-01 — Connection Test Fails

**Error:** `Connection refused: localhost:9000`

**Checklist:**
1. Is TallyPrime running? Launch TallyPrime and open the required company.
2. Is ODBC/Data Bridge enabled in TallyPrime? (Configuration → Advanced Config)
3. Is the port number correct? Default is 9000; check your Tally configuration.
4. Is there a firewall blocking port 9000? Temporarily disable Windows Firewall and retry.
5. If Tally is on a remote machine, verify the host IP is correct and port 9000 is reachable from the SMRITI server.

---

### Issue UIE-02 — Voucher Fails with "Company Name Mismatch"

**Error:** `Company not found in Tally: ABC Retail Pvt Ltd`

**Cause:** The company name in SMRITI UIE Tally Settings does not exactly match the company name in TallyPrime.

**Resolution:**
1. In TallyPrime, go to Gateway → Select Company → note the exact company name (case-sensitive)
2. In SMRITI → UIE Tally Settings → Company Name — paste the exact name
3. Save, retry sync

---

### Issue UIE-03 — Ledger Not Created in Tally

**Symptom:** First sync completes but ledger for a customer is not visible in TallyPrime.

**Checklist:**
1. Verify **Auto Create Ledgers = Yes** in UIE Tally Settings
2. Check Sync Log for the customer creation entry — look for `create_ledger` action
3. In TallyPrime → Chart of Accounts → Sundry Debtors group — the ledger should appear there
4. If TallyPrime is not accepting new ledgers via API, check TallyPrime license status (multi-user license required for API access)

---

### Issue UIE-04 — Voucher Shows "Duplicate" Status

**Symptom:** A voucher shows `Duplicate` in the Sync Queue even though you manually re-triggered it.

**Cause:** This is by design. UIE uses an idempotency key (combination of document type + document name + posting date) to prevent double-posting to Tally.

**Resolution:** The `Duplicate` status means the voucher was already posted to Tally successfully in a previous sync. No action needed.

If you genuinely need to re-post (e.g., after correcting a Tally error):
1. Open the Sync Queue entry
2. Click **Reset Idempotency** (admin action)
3. Trigger sync again

---

### Issue UIE-05 — Zero-Value Voucher Skipped

**Symptom:** A zero-value invoice or payment does not appear in TallyPrime.

**Cause:** By design, UIE skips zero-value vouchers. Tally does not accept zero-value journal entries.

**Resolution:** If a transaction genuinely has zero value, it is typically a data entry issue. Review the invoice and correct the amounts.

---

## Sync Queue Maintenance

To keep the sync queue healthy:
- Failed entries older than 30 days can be archived (Admin → UIE → Purge Old Queue Entries)
- Sync queue should not exceed 10,000 pending entries — if it does, check if the dispatcher is running
- Restart the SMRITI scheduler if the queue is growing without processing:
  ```bash
  bench restart
  ```

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
