-- SMRITI CGE v2 Database Constraints DDL Script
-- File: smriti_retail_os/patches/cge_v2_constraints.sql
-- Status: APPROVED (Phase 4C Constraint Hardening)
-- Author: SMRITI Architect / USER & AITDL
-- Date: 2026-06-19
-- 
-- Note: Do NOT execute this file directly. This is documented for migration design
-- and index validation checks. It will be run during Phase 5 Runtime Activation.

-- 1. Benefit Wallet Composite Unique Index
CREATE UNIQUE INDEX uq_wallet_cust_comp_inst
ON `tabSMRITI Benefit Wallet`
(customer, company, benefit_instrument);

-- 2. Benefit Ledger Query Index
CREATE INDEX idx_ledger_cust_inst_date
ON `tabSMRITI Benefit Ledger`
(customer, benefit_instrument, posting_date);

-- 3. Benefit Ledger Sales Return Trace Index
CREATE INDEX idx_ledger_ref
ON `tabSMRITI Benefit Ledger`
(reference_doctype, reference_name);
