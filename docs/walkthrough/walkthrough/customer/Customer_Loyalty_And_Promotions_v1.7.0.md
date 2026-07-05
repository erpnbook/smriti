# Customer: Loyalty & Promotions

## 1. Purpose
Implement SMRITI Retail OS Phase 7 — Loyalty & Promotions, introducing a robust, dark glassmorphic loyalty schemes manager console and a seamless points earning and redemption flow inside the POS billing screen.

## 2. Scope
* **Loyalty Backend API & Auto-Provisioning**: `smriti_retail_os/loyalty_api.py`, `smriti_retail_os/setup.py`
* **Manager Loyalty Console**: `smriti_retail_os/page/smriti-loyalty/`
* **POS Billing & Navigation Integration**: `smriti_retail_os/public/js/smriti_billing.js`, `smriti_retail_os/public/js/smriti_sidebar.js`, `smriti_retail_os/public/js/main.js`

## 3. Files Created
* `smriti_retail_os/loyalty_api.py`
* `smriti_retail_os/page/smriti-loyalty/smriti-loyalty.json`
* `smriti_retail_os/page/smriti-loyalty/smriti-loyalty.js`
* `smriti_retail_os/page/smriti-loyalty/smriti-loyalty.css`

## 4. Files Modified
* `smriti_retail_os/setup.py`
* `smriti_retail_os/public/js/smriti_billing.js`
* `smriti_retail_os/public/js/smriti_sidebar.js`
* `smriti_retail_os/public/js/main.js`

## 5. Architecture Decisions
* **ERPNext Native Hooking**: Build directly on top of ERPNext's standard `Loyalty Program` and `Loyalty Point Entry` doctypes for seamless ledger integration, rather than maintaining a separate proprietary transaction log.
* **Whitelisted API Bridge**: Expose loyalty operations through a SMRITI custom whitelisted API bridge to keep POS transactions lightning fast.

## 6. Design Rationale
* **Manager Console Layout**: A three-column manager dashboard layout (programs on left, rules in middle, customer enrollment search on right) makes configuring and managing programs intuitive.
* **POS Experience**: Keep loyalty points balance visible on the active customer profile card to remind operators to cross-sell.

## 7. Implementation Summary
* **loyalty_api.py**: Created four whitelisted methods: `get_loyalty_details`, `get_loyalty_schemes`, `save_loyalty_scheme`, and `enroll_customer`.
* **setup.py**: Initialized default program "SMRITI Standard Loyalty" (1 Pt = ₹1.00 conversion) during app setup/migration.
* **smriti-loyalty**: Created the custom dashboard using glassmorphic UI elements and empty state pulse animations.
* **POS Billing Integration**: Modified `smriti_billing.js` to fetch customer loyalty balances dynamically on customer selection and held draft recalls. Implemented redemption points validation to clamp inputs.

## 8. Tests Executed
* **Manual Verification Flow**: Verified customer lookup, enrollment, points calculation, and checkout redemption validation.

## 9. Verification Results
* **Manager Console**: Accessing `/app/smriti-loyalty` displays the premium loyalty panel successfully.
* **Customer Onboarding**: Onboarding and assigning programs works instantly.
* **POS Billing**: Point redemption reduces the pending grand total due and submits POS invoice successfully.

## 10. Known Limitations
Does not support automatic tier upgrades based on historical annual customer spend.

## 11. Future Work
Integrate transactional SMS alerts when a customer earns or redeems loyalty points.

## 12. Related ADRs
None.

## 13. Related RFCs
None.
