# Implementation Plan - SMRITI Retail OS Audit Enhancements

Address shift closing errors, API session safety, and India Compliance integration discrepancies identified in the deep audit.

## User Review Required

> [!IMPORTANT]
> The database fix in `shift_api.py` alters POS Invoice search filters from `cashier` (which does not exist) to `owner`. Since ERPNext defaults to the logged-in session user as `owner`, this will align shift summaries correctly with the cashier who submitted the invoice.

> [!NOTE]
> Setting the `owner` field explicitly in `billing_api.py` ensures that even if an administrator or manager executes the POS/sales checkout API, the record remains owned by the cashier processing the transaction.

## Proposed Changes

---

### Backend Components

#### [MODIFY] [shift_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/shift_api.py)
Update SQL filters for POS Invoices to use `owner` instead of `cashier`.
- Line 114: Change filter `cashier: oe.user` to `owner: oe.user`.
- Line 244: Change filter `cashier: oe.user` to `owner: oe.user`.

#### [MODIFY] [billing_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/billing_api.py)
Explicitly assign the invoice owner to ensure authorization safety.
- Line 131: Set `pos_invoice.owner = cashier` before calling `pos_invoice.save()`.
- Line 275: Set `invoice_doc.owner = cashier` before calling `invoice_doc.insert()` / `save()`.

#### [MODIFY] [hooks_logic.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/hooks_logic.py)
Improve robustness of state resolution by checking alternate GSTIN fields.
- Line 111: Resolve Customer address state using `doc.tax_id or doc.get("gstin")`.
- Line 163: Resolve Supplier address state using `doc.gstin or doc.tax_id`.

---

### Frontend JS Controllers

#### [MODIFY] [supplier.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/public/js/supplier.js)
Listen to and validate both standard and India Compliance GSTIN fields.
- Line 17: Listen and refresh on `frm.doc.gstin` as well as `frm.doc.tax_id`.
- Line 22: Register `gstin` event listener to run client-side validation.
- Line 27: Retrieve GSTIN value from `frm.doc.gstin || frm.doc.tax_id`.

---

## Verification Plan

### Automated Tests
1. **Compiles & Runs**: Run `verify_clean.py` inside the container using:
   ```bash
   docker compose -f pwd.yml exec backend bench --site frontend execute "exec(open('/home/frappe/frappe-bench/verify_clean.py').read())"
   ```
2. **Interactive DB query**: Run `get_shift_summary` via bench execute with `owner` filter to ensure no Database error is raised.

### Manual Verification
1. Login to the POS Billing screen, create a checkout transaction, and verify that the invoice is saved with `owner` as the cashier.
2. Navigate to the Shift Manager page and ensure shift summaries display correctly without MySQL errors.
3. Open a Supplier form, enter a GSTIN value into the `gstin` field, and verify that the India Compliance validation box renders successfully with registration details.
