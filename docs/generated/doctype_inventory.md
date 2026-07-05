---
Document ID: "SMRITI-DOC-028"
Title: "SMRITI DocType Inventory"
Owner: "Release Engineering Team"
Audience: "Support Engineer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "No"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Custom DocType Inventory

* **Compiler Version:** 1.1
* **Snapshot Commit:** `f95b4fe91f273f7a6745f2f7d1de4733757db2dd`
* **Compiled At:** 2026-06-25T10:19:35Z

## Custom DocTypes List

### PSV Channel Partner
* **Artifact ID:** `ART-DOCTYPE-00001`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/psv_channel_partner/psv_channel_partner.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| customer | Customer | Link | 1 |
| location_name | Location Name | Data | 1 |
| territory | Territory | Link | 1 |
| zone | Zone | Select | 0 |
| region | Region | Data | 0 |
| area_manager | Area Manager | Link | 0 |
| effective_from | Effective From | Date | 0 |
| effective_to | Effective To | Date | 0 |
| contact_person | Contact Person | Data | 0 |
| mobile | Mobile | Data | 0 |
| email | Email | Data | 0 |
| active | Active | Check | 0 |
| status | Status | Select | 0 |
| primary_brand | Primary Brand | Data | 0 |
| brands | Brands | Table | 0 |

### PSV Channel Partner Brand
* **Artifact ID:** `ART-DOCTYPE-00002`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/psv_channel_partner_brand/psv_channel_partner_brand.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| brand | Brand | Link | 1 |
| is_primary | Is Primary | Check | 0 |

### PSV Ledger Entry
* **Artifact ID:** `ART-DOCTYPE-00003`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/psv_ledger_entry/psv_ledger_entry.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| posting_datetime | Posting Datetime | Datetime | 1 |
| channel_partner | Channel Partner | Link | 1 |
| item_variant | Item Variant | Link | 1 |
| qty | Quantity | Float | 1 |
| transaction_type | Transaction Type | Select | 1 |
| voucher_type | Voucher Type | Data | 0 |
| voucher_no | Voucher No | Data | 0 |
| unique_hash | Unique Hash | Data | 0 |
| reversal_of | Reversal Of | Link | 0 |
| reversal_reason | Reversal Reason | Small Text | 0 |
| warehouse | Warehouse | Link | 0 |
| currency | Currency | Link | 0 |
| fiscal_year | Fiscal Year | Link | 0 |
| hash_version | Hash Version | Int | 0 |

### PSV Reorder Rule
* **Artifact ID:** `ART-DOCTYPE-00004`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/psv_reorder_rule/psv_reorder_rule.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| active | Is Active | Check | 0 |
| customer | Channel | Link | 1 |
| item_template | Style/Template | Link | 1 |
| column_break_rules |  | Column Break | 0 |
| core_sizes | Core Sizes | Data | 1 |
| target_qty | Target Quantity (Per Variant) | Float | 1 |

### PSV Stock Aging Snapshot
* **Artifact ID:** `ART-DOCTYPE-00005`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/psv_stock_aging_snapshot/psv_stock_aging_snapshot.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| snapshot_date | Snapshot Date | Date | 1 |
| channel_partner | Channel Partner | Link | 1 |
| item_variant | Item Variant | Link | 1 |
| qty | Total Quantity | Float | 0 |
| brand_name | Brand Name | Data | 0 |
| item_group_name | Item Group Name | Data | 0 |
| territory_name | Territory Name | Data | 0 |
| qty_0_30 | 0-30 Days Qty | Float | 0 |
| qty_31_60 | 31-60 Days Qty | Float | 0 |
| qty_61_90 | 61-90 Days Qty | Float | 0 |
| qty_91_180 | 91-180 Days Qty | Float | 0 |
| qty_180_plus | 180+ Days Qty | Float | 0 |
| aging_alert | Aging Alert | Data | 0 |

### PSV System Settings
* **Artifact ID:** `ART-DOCTYPE-00006`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/psv_system_settings/psv_system_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| last_snapshot_run | Last Snapshot Run | Datetime | 0 |
| last_checkpoint | Last Checkpoint Partner | Data | 0 |
| last_processed_partner | Last Processed Partner | Data | 0 |
| snapshot_batch_size | Snapshot Batch Size | Int | 0 |
| redistribution_scope | Redistribution Scope | Select | 0 |
| weeks_of_cover_critical | Weeks of Cover (Critical) | Int | 0 |
| weeks_of_cover_warning | Weeks of Cover (Warning) | Int | 0 |
| weeks_of_cover_healthy | Weeks of Cover (Healthy) | Int | 0 |
| channel_health_enabled | Enable Channel Health (Phase 1.2) | Check | 0 |
| star_velocity_threshold | Star Velocity Threshold (Units/Week) | Float | 0 |

### SMRITI Address Audit Log
* **Artifact ID:** `ART-DOCTYPE-00007`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_address_audit_log/smriti_address_audit_log.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| changed_by | Changed By | Link | 0 |
| changed_at | Changed At | Datetime | 0 |
| field_name | Field Name | Data | 0 |
| old_value | Old Value | Small Text | 0 |
| new_value | New Value | Small Text | 0 |
| company | Company | Link | 0 |

### SMRITI Attribution Event
* **Artifact ID:** `ART-DOCTYPE-00008`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_attribution_event/smriti_attribution_event.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| invoice_reference | Invoice Reference | Data | 1 |
| invoice_doctype | Invoice DocType | Data | 1 |
| customer | Customer | Link | 1 |
| company | Company | Link | 1 |
| posting_date | Posting Date | Date | 1 |
| posting_time | Posting Time | Time | 1 |
| grand_total | Grand Total | Currency | 1 |
| net_total | Net Total | Currency | 1 |
| status | Status | Select | 0 |
| error_message | Error Message | Small Text | 0 |

### SMRITI Attribution Ledger
* **Artifact ID:** `ART-DOCTYPE-00009`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_attribution_ledger/smriti_attribution_ledger.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| invoice_reference | Invoice Reference | Data | 1 |
| invoice_doctype | Invoice DocType | Data | 1 |
| customer | Customer | Link | 1 |
| employee | Employee | Link | 1 |
| ownership_type | Ownership Type | Select | 1 |
| revenue_credit | Revenue Credit | Currency | 1 |
| credit_percentage | Credit Percentage | Percent | 1 |
| store | Store | Link | 1 |
| warehouse | Warehouse | Link | 0 |
| posting_date | Posting Date | Date | 1 |
| posting_time | Posting Time | Time | 1 |
| source_document | Source Document | Data | 0 |
| ledger_status | Ledger Status | Select | 1 |
| reversal_reference | Reversal Reference | Data | 0 |
| company | Company | Link | 1 |
| ownership_record | Ownership Record Reference | Link | 0 |

### SMRITI Attribution Rule
* **Artifact ID:** `ART-DOCTYPE-00010`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_attribution_rule/smriti_attribution_rule.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| rule_name | Rule Name | Data | 1 |
| is_active | Is Active | Check | 0 |

### SMRITI Benefit Audit Log
* **Artifact ID:** `ART-DOCTYPE-00011`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_audit_log/smriti_benefit_audit_log.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| transaction_id | Transaction ID | Data | 0 |
| customer | Customer | Link | 0 |
| resolution_policy | Resolution Policy | Link | 0 |
| request_payload | Request Payload | Code | 0 |
| applied_benefits | Applied Benefits | Code | 0 |
| rejected_benefits | Rejected Benefits | Code | 0 |
| execution_order | Execution Order | Text | 0 |
| final_totals | Final Totals | Code | 0 |
| timestamp | Timestamp | Datetime | 0 |

### SMRITI Benefit Instrument
* **Artifact ID:** `ART-DOCTYPE-00012`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_instrument/smriti_benefit_instrument.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| instrument_name | Instrument Name | Data | 1 |
| instrument_type | Instrument Type | Link | 1 |
| validity_days | Validity (Days) | Int | 0 |
| allow_negative_balance | Allow Negative Balance | Check | 0 |
| reversal_strategy | Reversal Strategy | Select | 1 |
| liability_account | Liability Account | Link | 0 |
| expense_account | Expense Account | Link | 0 |

### SMRITI Benefit Instrument Type
* **Artifact ID:** `ART-DOCTYPE-00013`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_instrument_type/smriti_benefit_instrument_type.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| type_name | Type Name | Data | 1 |
| description | Description | Small Text | 0 |

### SMRITI Benefit Ledger
* **Artifact ID:** `ART-DOCTYPE-00014`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_ledger/smriti_benefit_ledger.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| ledger_sequence | Ledger Sequence | Data | 1 |
| customer | Customer | Link | 1 |
| company | Company | Link | 1 |
| benefit_instrument | Benefit Instrument | Link | 1 |
| transaction_type | Transaction Type | Select | 1 |
| event_type | Event Type | Select | 1 |
| amount | Amount | Float | 1 |
| balance_remaining | Balance Remaining | Float | 0 |
| reference_doctype | Reference DocType | Link | 0 |
| reference_name | Reference Name | Data | 0 |
| posting_date | Posting Date | Date | 1 |
| expiry_date | Expiry Date | Date | 0 |
| is_reversal | Is Reversal | Check | 0 |
| reversed_ledger_entry | Reversed Ledger Entry | Link | 0 |
| journal_entry | Journal Entry | Link | 0 |
| remarks | Remarks | Text | 0 |

### SMRITI Benefit Liability Snapshot
* **Artifact ID:** `ART-DOCTYPE-00015`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_liability_snapshot/smriti_benefit_liability_snapshot.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| snapshot_date | Snapshot Date | Date | 1 |
| company | Company | Link | 1 |
| benefit_instrument | Benefit Instrument | Link | 1 |
| outstanding_liability | Outstanding Liability | Float | 1 |
| reconciliation_status | Reconciliation Status | Select | 0 |
| variance | Variance | Float | 0 |

### SMRITI Benefit Resolution Policy
* **Artifact ID:** `ART-DOCTYPE-00016`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_resolution_policy/smriti_benefit_resolution_policy.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| policy_name | Policy Name | Data | 1 |
| is_active | Is Active | Check | 0 |
| sequence_details | Sequence Details | Table | 1 |

### SMRITI Benefit Resolution Sequence Detail
* **Artifact ID:** `ART-DOCTYPE-00017`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_resolution_sequence_detail/smriti_benefit_resolution_sequence_detail.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| benefit_type | Benefit Type | Select | 1 |
| execution_order | Execution Order | Int | 1 |
| allow_stacking | Allow Stacking | Check | 0 |
| exclusive_rule | Exclusive Rule | Check | 0 |

### SMRITI Benefit Wallet
* **Artifact ID:** `ART-DOCTYPE-00018`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_wallet/smriti_benefit_wallet.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| customer | Customer | Link | 1 |
| company | Company | Link | 1 |
| benefit_instrument | Benefit Instrument | Link | 1 |
| balance | Balance | Float | 0 |
| last_updated | Last Updated | Datetime | 0 |

### SMRITI Business Term
* **Artifact ID:** `ART-DOCTYPE-00019`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_business_term/smriti_business_term.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| term_id | Term ID | Data | 1 |
| term_name | Term Name | Data | 1 |
| term_category | Term Category | Select | 1 |
| term_version | Term Version | Data | 1 |
| replaces_term_id | Replaces Term | Link | 0 |
| status | Status | Select | 1 |
| is_active | Is Active | Check | 0 |
| term_aliases | Term Aliases | Long Text | 0 |
| effective_date | Effective Date | Date | 1 |
| deprecation_date | Deprecation Date | Date | 0 |
| business_owner | Business Owner | Data | 0 |
| technical_owner | Technical Owner | Data | 0 |
| definition | Definition | Long Text | 1 |
| hinglish_definition | Hinglish Definition | Long Text | 1 |
| related_formulas | Related Formulas | Table | 0 |
| related_terms | Related Terms | Table | 0 |
| formula_definition_ref | Formula Definition Ref | Link | 0 |
| formula_version | Formula Version | Data | 0 |
| explainability_note | Explainability Note | Long Text | 0 |
| faq | FAQ (JSON) | Long Text | 0 |
| common_mistakes | Common Mistakes (JSON) | Long Text | 0 |
| manual_reference | Manual Reference | Data | 0 |
| training_reference | Training Reference | Data | 0 |
| dictionary_key | Dictionary Key | Data | 0 |
| projection_path | Projection Path | Data | 0 |
| entity_type | Entity Type | Data | 0 |
| data_type | Data Type | Select | 0 |
| measure_or_dimension | Measure or Dimension | Select | 0 |
| is_groupable | Is Groupable | Check | 0 |
| is_filterable | Is Filterable | Check | 0 |
| is_reportable | Is Reportable | Check | 0 |
| default_aggregation | Default Aggregation | Select | 0 |
| approval_status | Approval Status | Select | 0 |
| dictionary_version | Dictionary Version | Data | 0 |

### SMRITI Campaign
* **Artifact ID:** `ART-DOCTYPE-00020`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_campaign/smriti_campaign.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| campaign_name | Campaign Name | Data | 1 |
| company | Company | Link | 1 |
| status | Status | Select | 1 |
| start_date | Start Date | Date | 0 |
| end_date | End Date | Date | 0 |
| budget_limit | Budget Limit | Float | 1 |
| budget_reserved | Budget Reserved | Float | 0 |
| budget_consumed | Budget Consumed | Float | 0 |
| stop_on_limit | Stop on Limit Exceeded | Check | 0 |

### SMRITI Certification Exam
* **Artifact ID:** `ART-DOCTYPE-00021`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_certification_exam/smriti_certification_exam.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| exam_id | Exam ID | Data | 1 |
| title | Title | Data | 1 |
| source_document | Source Document | Data | 1 |
| passing_score | Passing Score (%) | Percent | 1 |
| duration_minutes | Duration (Minutes) | Int | 1 |
| active | Active | Check | 0 |

### SMRITI CGE Settings
* **Artifact ID:** `ART-DOCTYPE-00022`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_cge_settings/smriti_cge_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| enable_loyalty | Enable Loyalty Studio | Check | 0 |
| enable_cashback | Enable Cashback Wallet | Check | 0 |
| enable_coupon | Enable Coupon Studio | Check | 0 |
| enable_campaign_budget | Enable Campaign Budget Enforcement | Check | 0 |
| enable_offline_cache | Enable Offline POS Caching | Check | 0 |
| enable_rule_trace | Enable Rule Evaluation Tracing | Check | 0 |
| wallet_validity_days | Wallet Validity (Days) | Int | 0 |
| amber_liability_threshold | Amber Liability Threshold | Currency | 0 |
| red_liability_threshold | Red Liability Threshold | Currency | 0 |

### SMRITI Clienteling Settings
* **Artifact ID:** `ART-DOCTYPE-00023`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_clienteling_settings/smriti_clienteling_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| enable_clienteling | Enable Clienteling Studio | Check | 0 |
| vip_threshold | VIP Candidate Threshold Score | Percent | 0 |
| dormancy_days | Standard Dormancy Days | Int | 0 |
| enable_predictions | Enable AI predictions | Check | 0 |

### SMRITI Commission Adjustment Detail
* **Artifact ID:** `ART-DOCTYPE-00024`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_commission_adjustment_detail/smriti_commission_adjustment_detail.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| reason | Reason | Data | 1 |
| amount | Amount (₹) | Currency | 1 |
| remarks | Remarks | Small Text | 0 |
| approved_by | Approved By | Data | 0 |
| approved_on | Approved On | Date | 0 |

### SMRITI Commission Event
* **Artifact ID:** `ART-DOCTYPE-00025`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_commission_event/smriti_commission_event.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| employee | Employee | Link | 1 |
| invoice_reference | Invoice Reference | Data | 1 |
| attribution_ledger | Attribution Ledger | Link | 1 |
| attributed_revenue | Attributed Revenue (₹) | Currency | 1 |
| commission_rule | Commission Rule | Link | 0 |
| commission_rate | Commission Rate (%) | Percent | 0 |
| commission_amount | Commission Amount (₹) | Currency | 1 |
| event_status | Event Status | Select | 1 |
| error_message | Error Message | Small Text | 0 |
| posting_date | Posting Date | Date | 1 |
| company | Company | Link | 1 |

### SMRITI Commission Ledger
* **Artifact ID:** `ART-DOCTYPE-00026`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_commission_ledger/smriti_commission_ledger.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| employee | Employee | Link | 1 |
| commission_event | Commission Event | Link | 0 |
| amount | Amount (₹) | Currency | 1 |
| ledger_status | Ledger Status | Select | 1 |
| reversal_reference | Reversal Reference | Data | 0 |
| posting_date | Posting Date | Date | 1 |
| posting_time | Posting Time | Time | 1 |
| company | Company | Link | 1 |

### SMRITI Commission Rule
* **Artifact ID:** `ART-DOCTYPE-00027`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_commission_rule/smriti_commission_rule.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| rule_name | Rule Name | Data | 1 |
| employee | Employee Override | Link | 0 |
| commission_rate | Commission Rate (%) | Percent | 1 |
| min_revenue_threshold | Min Revenue Threshold (₹) | Currency | 0 |
| effective_from | Effective From | Date | 0 |
| effective_to | Effective To | Date | 0 |
| priority | Priority | Int | 0 |
| is_active | Is Active | Check | 0 |
| company | Company | Link | 1 |

### SMRITI Commission Settings
* **Artifact ID:** `ART-DOCTYPE-00028`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_commission_settings/smriti_commission_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| enable_sfc | Enable SFC | Check | 0 |
| auto_generate_events | Auto-Generate Commission Events | Check | 0 |
| auto_generate_settlements | Auto-Generate Settlements | Check | 0 |
| allow_negative_commission | Allow Negative Commission | Check | 0 |

### SMRITI Commission Settlement
* **Artifact ID:** `ART-DOCTYPE-00029`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_commission_settlement/smriti_commission_settlement.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| employee | Employee | Link | 1 |
| company | Company | Link | 1 |
| fiscal_year | Fiscal Year | Link | 1 |
| month | Month | Select | 1 |
| settlement_from_date | Settlement From Date | Date | 0 |
| settlement_to_date | Settlement To Date | Date | 0 |
| gross_commission | Gross Commission (₹) | Currency | 1 |
| adjustments | Manual Adjustments | Table | 0 |
| net_commission | Net Commission (₹) | Currency | 1 |
| settled_commission_amount | Settled Commission Amount | Currency | 0 |
| status | Status | Select | 1 |
| payment_date | Payment Date | Date | 0 |
| payment_reference | Payment Reference | Data | 0 |

### SMRITI Company Settings
* **Artifact ID:** `ART-DOCTYPE-00030`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_company_settings/smriti_company_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| sb_store | Store Identity | Section Break | 0 |
| store_trade_name | Store Trade Name | Data | 0 |
| store_logo_url | Store Logo URL | Data | 0 |
| cb_store |  | Column Break | 0 |
| brand_color | Brand Color | Color | 0 |
| receipt_footer_text | Receipt Footer Text | Small Text | 0 |
| invoice_series_prefix | Invoice Series Prefix | Data | 0 |
| sb_defaults | Operational Defaults | Section Break | 0 |
| default_warehouse | Default Warehouse | Link | 0 |
| default_pos_profile | Default POS Profile | Link | 0 |
| cb_defaults |  | Column Break | 0 |
| default_walk_in_customer | Default Walk-in Customer | Link | 0 |
| default_intrastate_tax_template | Default Intrastate Tax Template | Link | 0 |
| default_interstate_tax_template | Default Interstate Tax Template | Link | 0 |
| sb_loyalty | Loyalty Program | Section Break | 0 |
| loyalty_enabled | Enable Loyalty Program | Check | 0 |
| loyalty_points_per_rupee | Points per Rupee | Float | 0 |
| sb_cloud_backup | Cloud Backup (S3/Rclone) | Section Break | 0 |
| cloud_backup_enabled | Enable Cloud Backup | Check | 0 |
| cloud_provider | Cloud Provider | Select | 0 |
| s3_bucket | S3 Bucket Name | Data | 0 |
| cb_cloud |  | Column Break | 0 |
| s3_access_key | S3 Access Key | Data | 0 |
| s3_secret_key | S3 Secret Key | Password | 0 |
| s3_region | S3 Region | Data | 0 |
| sb_advanced | Advanced Configuration | Section Break | 0 |
| size_groups_json | Size Groups JSON | Long Text | 0 |
| destinationwise_taxes_json | Destinationwise Taxes JSON | Long Text | 0 |
| backup_settings_json | Backup Settings JSON | Long Text | 0 |
| default_printer_ip | Default Printer IP | Data | 0 |
| default_printer_port | Default Printer Port | Int | 0 |
| default_printer_lang | Default Printer Language | Select | 0 |
| default_label_size | Default Label Size | Select | 0 |

### SMRITI Coupon Campaign
* **Artifact ID:** `ART-DOCTYPE-00031`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_coupon_campaign/smriti_coupon_campaign.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| campaign_name | Campaign Name | Data | 1 |
| campaign_type | Campaign Type | Select | 1 |
| start_date | Start Date | Date | 1 |
| end_date | End Date | Date | 1 |
| budget_limit | Budget Limit | Currency | 1 |
| budget_reserved | Budget Reserved | Currency | 0 |
| budget_consumed | Budget Consumed | Currency | 0 |
| stop_on_limit | Stop on Limit Exceeded | Check | 0 |
| status | Status | Select | 1 |

### SMRITI Coupon Rule
* **Artifact ID:** `ART-DOCTYPE-00032`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_coupon_rule/smriti_coupon_rule.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| campaign | Campaign | Link | 1 |
| coupon_code | Coupon Code | Data | 1 |
| status | Status | Select | 1 |
| max_uses_per_customer | Max Uses Per Customer | Int | 0 |
| max_uses_per_mobile | Max Uses Per Mobile | Int | 0 |
| max_uses_per_day | Max Uses Per Day | Int | 0 |
| max_discount_cap | Max Discount Cap | Float | 0 |
| pricing_rule_link | Pricing Rule Link | Link | 0 |

### SMRITI Customer Benefit Profile
* **Artifact ID:** `ART-DOCTYPE-00033`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_customer_benefit_profile/smriti_customer_benefit_profile.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| customer | Customer | Link | 1 |
| active_loyalty_tier | Active Loyalty Tier | Link | 0 |
| accumulated_points | Accumulated Points | Float | 0 |
| is_eligible_for_benefits | Is Eligible For Benefits | Check | 0 |

### SMRITI Customer Graph
* **Artifact ID:** `ART-DOCTYPE-00034`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_customer_graph/smriti_customer_graph.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| customer | Customer | Link | 1 |
| purchases_count | Total Purchases | Int | 0 |
| returns_count | Total Returns | Int | 0 |
| net_revenue | Net Revenue | Currency | 0 |
| wallet_balance | Wallet Balance | Currency | 0 |
| campaign_responses_count | Campaign Responses | Int | 0 |
| attributed_revenue | Attributed Revenue | Currency | 0 |
| owned_customer_revenue | Owned Customer Revenue | Currency | 0 |
| preferred_brand | Preferred Brand | Link | 0 |
| preferred_category | Preferred Category | Link | 0 |
| preferred_size | Preferred Size | Data | 0 |
| preferred_color | Preferred Color | Data | 0 |
| last_visit_date | Last Visit Date | Date | 0 |
| visit_frequency_days | Visit Frequency (Days) | Float | 0 |
| favorite_executive | Favorite Executive | Link | 0 |
| is_dirty | Is Dirty | Check | 0 |
| dirty_source | Dirty Source | Data | 0 |
| dirty_document | Dirty Document | Data | 0 |
| graph_version | Graph Version | Data | 1 |
| calculation_status | Calculation Status | Select | 1 |
| last_calculated_on | Last Calculated On | Datetime | 0 |
| graph_last_generated_at | Graph Last Generated At | Datetime | 0 |
| graph_generation_duration_ms | Graph Generation Duration (ms) | Float | 0 |
| graph_source_version | Graph Source Version | Data | 0 |
| graph_status | Graph Status | Select | 0 |
| graph_generation_error | Graph Generation Error | Small Text | 0 |

### SMRITI Customer Intelligence Graph
* **Artifact ID:** `ART-DOCTYPE-00035`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_customer_intelligence_graph/smriti_customer_intelligence_graph.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| customer | Customer | Link | 1 |
| churn_risk_score | Churn Risk Score | Percent | 0 |
| churn_risk_level | Churn Risk Level | Select | 0 |
| churn_formula_id | Churn Formula Reference | Link | 0 |
| churn_formula_version | Churn Formula Version | Data | 0 |
| vip_candidate_score | VIP Candidate Score | Percent | 0 |
| vip_candidate_level | VIP Candidate Level | Select | 0 |
| is_vip | Is VIP | Check | 0 |
| vip_formula_id | VIP Formula Reference | Link | 0 |
| vip_formula_version | VIP Formula Version | Data | 0 |
| is_dormant | Is Dormant | Check | 0 |
| next_visit_prediction | Predicted Next Visit | Date | 0 |
| next_visit_confidence | Next Visit Confidence | Percent | 0 |
| next_purchase_prediction | Predicted Next Purchase | Link | 0 |
| next_purchase_confidence | Next Purchase Confidence | Percent | 0 |
| campaign_affinity_score | Campaign Affinity Score | Percent | 0 |
| affinity_formula_id | Affinity Formula Reference | Link | 0 |
| affinity_formula_version | Affinity Formula Version | Data | 0 |
| is_dirty | Is Dirty | Check | 0 |
| dirty_source | Dirty Source | Data | 0 |
| dirty_document | Dirty Document | Data | 0 |
| intelligence_graph_version | Intelligence Graph Version | Data | 1 |
| calculation_status | Calculation Status | Select | 1 |
| last_calculated_on | Last Calculated On | Datetime | 0 |
| customer_health_score | Customer Health Score | Percent | 0 |
| graph_version | Graph Version | Data | 0 |
| scoring_model_version | Scoring Model Version | Data | 0 |
| prediction_model_version | Prediction Model Version | Data | 0 |

### SMRITI Customer Interaction
* **Artifact ID:** `ART-DOCTYPE-00036`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_customer_interaction/smriti_customer_interaction.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| customer | Customer | Link | 1 |
| interaction_date | Interaction Date | Date | 1 |
| interaction_time | Interaction Time | Time | 1 |
| interaction_type | Interaction Type | Select | 1 |
| employee | Employee | Link | 1 |
| interaction_outcome | Interaction Outcome | Select | 1 |
| store | Store | Link | 1 |
| channel | Channel | Select | 1 |
| details | Details | Small Text | 0 |
| ref_doc_type | Ref DocType | Data | 0 |
| ref_doc_name | Ref Name | Data | 0 |

### SMRITI Customer Ownership
* **Artifact ID:** `ART-DOCTYPE-00037`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_customer_ownership/smriti_customer_ownership.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| customer | Customer | Link | 1 |
| primary_owner | Primary Owner | Link | 1 |
| secondary_owner | Secondary Owner | Link | 0 |
| start_date | Start Date | Date | 1 |
| end_date | End Date | Date | 0 |
| is_active | Is Active | Check | 0 |
| company | Company | Link | 1 |

### SMRITI Customer Profile
* **Artifact ID:** `ART-DOCTYPE-00038`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_customer_profile/smriti_customer_profile.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| customer | Customer | Link | 1 |
| preferred_brand | Preferred Brand | Link | 0 |
| preferred_category | Preferred Category | Link | 0 |
| preferred_size | Preferred Size | Data | 0 |
| preferred_color | Preferred Color | Data | 0 |
| last_visit_date | Last Visit Date | Date | 0 |
| visit_frequency_days | Visit Frequency (Days) | Float | 0 |
| favorite_executive | Favorite Executive | Link | 0 |
| average_basket_value | Average Basket Value (ABV) | Currency | 0 |
| lifetime_value | Lifetime Value (LTV) | Currency | 0 |
| likely_purchase_prediction | Likely Purchase Prediction | Link | 0 |
| prediction_confidence | Prediction Confidence | Percent | 0 |
| next_visit_prediction | Predicted Next Visit | Date | 0 |
| next_visit_confidence | Next Visit Confidence | Percent | 0 |
| next_purchase_confidence | Next Purchase Confidence | Percent | 0 |
| churn_risk_score | Churn Risk Score | Percent | 0 |
| churn_risk_level | Churn Risk Level | Select | 0 |
| vip_candidate_score | VIP Candidate Score | Percent | 0 |
| vip_candidate_level | VIP Candidate Level | Select | 0 |
| is_vip | Is VIP | Check | 0 |
| campaign_affinity_score | Campaign Affinity Score | Percent | 0 |
| engagement_score | Engagement Score | Percent | 0 |
| customer_health_score | Customer Health Score | Percent | 0 |
| is_dirty | Is Dirty | Check | 0 |
| dirty_source | Dirty Source | Data | 0 |
| dirty_document | Dirty Document | Data | 0 |
| graph_version | Graph Version | Data | 1 |
| calculation_status | Calculation Status | Select | 1 |
| last_calculated_on | Last Calculated On | Datetime | 0 |

### SMRITI Custom Attribute
* **Artifact ID:** `ART-DOCTYPE-00039`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_custom_attribute/smriti_custom_attribute.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_code | Attribute Code | Data | 1 |
| attribute_name | Attribute Name | Data | 1 |
| attribute_group | Attribute Group | Select | 1 |
| attribute_scope | Attribute Scope | Select | 0 |
| entity_type | Entity Type | Select | 1 |
| attribute_type | Attribute Type | Select | 1 |
| options | Options | Text | 0 |
| is_filterable | Is Filterable | Check | 0 |
| is_reportable | Is Reportable | Check | 0 |

### SMRITI Entity Attribute Value
* **Artifact ID:** `ART-DOCTYPE-00040`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_entity_attribute_value/smriti_entity_attribute_value.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| parenttype | Parent Type | Data | 1 |
| parent | Parent Name | Data | 1 |
| attribute_code | Attribute Code | Link | 1 |
| attribute_value | Attribute Value | Text | 1 |

### SMRITI Explain Audit Event
* **Artifact ID:** `ART-DOCTYPE-00041`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_explain_audit_event/smriti_explain_audit_event.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| user | User | Link | 1 |
| metric | Metric | Data | 1 |
| customer | Customer | Link | 1 |
| formula_id | Formula Reference | Link | 0 |
| timestamp | Timestamp | Datetime | 1 |
| session_id | Session ID | Data | 0 |
| source_screen | Source Screen | Data | 0 |

### SMRITI Formula Definition
* **Artifact ID:** `ART-DOCTYPE-00042`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_formula_definition/smriti_formula_definition.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| formula_id | Formula ID | Data | 1 |
| formula_name | Formula Name | Data | 1 |
| formula_version | Formula Version | Data | 1 |
| formula_category | Formula Category | Select | 1 |
| status | Status | Select | 1 |
| is_active | Is Active | Check | 0 |
| replaces_formula_id | Replaces Formula | Link | 0 |
| effective_date | Effective Date | Date | 1 |
| deprecation_date | Deprecation Date | Date | 0 |
| implementation_reference | Implementation Reference | Data | 0 |
| dependent_features | Dependent Features | Long Text | 0 |
| formula_expression | Formula Expression | Long Text | 1 |
| formula_language | Formula Language | Data | 0 |
| variables_and_inputs | Variables and Inputs | Long Text | 0 |
| data_sources | Data Sources | Long Text | 0 |
| business_owner | Business Owner | Data | 0 |
| technical_owner | Technical Owner | Data | 0 |
| business_meaning | Business Meaning | Long Text | 0 |
| worked_example | Worked Example | Long Text | 0 |
| interpretation_guide | Interpretation Guide | Long Text | 0 |
| recommended_action | Recommended Action | Long Text | 0 |
| explainability_json | Explainability JSON | Long Text | 0 |
| migration_notes | Migration Notes | Long Text | 0 |

### SMRITI Gender
* **Artifact ID:** `ART-DOCTYPE-00043`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_gender/smriti_gender.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_value | Value | Data | 1 |

### SMRITI Heel Type
* **Artifact ID:** `ART-DOCTYPE-00044`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_heel_type/smriti_heel_type.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_value | Value | Data | 1 |

### SMRITI Key Custodian
* **Artifact ID:** `ART-DOCTYPE-00045`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_key_custodian/smriti_key_custodian.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| custodian_name | Custodian Name | Data | 1 |
| email | Email | Data | 1 |
| verified | Verified | Check | 0 |
| verification_date | Verification Date | Datetime | 0 |
| last_recovery_sent | Last Recovery Sent | Datetime | 0 |
| status | Status | Select | 0 |
| otp_hash | OTP Hash | Data | 0 |
| otp_expiry | OTP Expiry | Datetime | 0 |

### SMRITI Knowledge Asset
* **Artifact ID:** `ART-DOCTYPE-00046`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_knowledge_asset/smriti_knowledge_asset.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| asset_code | Asset Code | Data | 1 |
| asset_uri | Asset URI | Data | 1 |
| asset_type | Asset Type | Select | 1 |
| asset_icon | Asset Icon | Data | 0 |
| title | Title | Data | 1 |
| status | Status | Select | 1 |
| is_active | Is Active | Check | 0 |
| visibility | Visibility | Select | 0 |
| access_policy | Access Policy | Select | 0 |
| asset_tags | Asset Tags | Small Text | 0 |
| version | Version | Data | 0 |
| owner | Owner | Link | 0 |
| reference_doctype | Reference DocType | Link | 1 |
| reference_name | Reference Name | Data | 1 |

### SMRITI Knowledge Relation
* **Artifact ID:** `ART-DOCTYPE-00047`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_knowledge_relation/smriti_knowledge_relation.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| source_asset_id | Source Asset ID | Link | 1 |
| target_asset_id | Target Asset ID | Link | 1 |
| relationship_type | Relationship Type | Select | 1 |
| strength | Strength | Select | 0 |
| is_primary | Is Primary | Check | 0 |
| tenant_scope | Tenant Scope | Select | 0 |
| visibility | Visibility | Select | 0 |

### SMRITI Liability Snapshot
* **Artifact ID:** `ART-DOCTYPE-00048`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_liability_snapshot/smriti_liability_snapshot.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 0 |
| snapshot_date | Snapshot Date | Date | 1 |
| loyalty_liability | Loyalty Liability | Currency | 1 |
| cashback_liability | Cashback Liability | Currency | 1 |
| coupon_liability | Coupon Liability | Currency | 1 |
| giftcard_liability | Gift Card Liability | Currency | 1 |

### SMRITI License
* **Artifact ID:** `ART-DOCTYPE-00049`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_license/smriti_license.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| organization_name | Organization Name | Data | 0 |
| store_name | Store Name | Data | 0 |
| owner_name | Owner Name | Data | 0 |
| section_identity | Business Identity | Section Break | 0 |
| gstin | GSTIN | Data | 0 |
| pan | PAN | Data | 0 |
| business_type | Business Type | Data | 0 |
| section_license | License | Section Break | 0 |
| license_key | License Key | Password | 0 |
| license_key_suffix | License Key Suffix | Data | 0 |
| license_type | License Type | Select | 0 |
| license_status | License Status | Select | 0 |
| license_health | License Health | Select | 0 |
| section_grace | Grace & Warning Thresholds | Section Break | 0 |
| grace_reason | Grace Reason | Select | 0 |
| grace_period_days | Grace Period (Days) | Int | 0 |
| warning_threshold_days | Warning Threshold (Days) | Int | 0 |
| section_dates | Dates | Section Break | 0 |
| activation_date | Activation Date | Date | 0 |
| expiry_date | Expiry Date | Date | 0 |
| last_license_validation | Last Validation | Datetime | 0 |
| section_install | Installation Identity | Section Break | 0 |
| installation_id | Installation ID | Data | 0 |
| device_id | Device ID | Data | 0 |
| server_id | Server ID | Data | 0 |
| site_name | Site Name | Data | 0 |
| site_url | Site URL | Data | 0 |
| server_fingerprint | Server Fingerprint | Data | 0 |
| section_contact | Registration Contact | Section Break | 0 |
| registered_domain | Registered Domain | Data | 0 |
| registered_email | Registered Email | Data | 0 |
| registered_mobile | Registered Mobile | Data | 0 |
| created_on | Created On | Datetime | 0 |
| section_plan | Plan & Limits | Section Break | 0 |
| current_plan | Current Plan | Data | 0 |
| user_limit | User Limit | Int | 0 |
| store_limit | Store Limit | Int | 0 |
| section_support | Support | Section Break | 0 |
| customer_id | Customer ID | Data | 0 |
| support_contract_status | Support Contract Status | Data | 0 |
| amc_status | AMC Status | Data | 0 |
| section_sync | Sync & Offline | Section Break | 0 |
| last_sync | Last Sync | Datetime | 0 |
| offline_validation_status | Offline Validation Status | Select | 0 |
| section_tamper | Integrity | Section Break | 0 |
| tamper_detected | Tamper Detected | Check | 0 |
| tamper_reason | Tamper Reason | Data | 0 |
| last_integrity_check | Last Integrity Check | Datetime | 0 |
| checksum_hash | Checksum Hash | Password | 0 |
| section_integrity | Phase-2 Security (Reserved) | Section Break | 0 |
| license_signature | License Signature | Password | 0 |
| activation_token | Activation Token | Password | 0 |
| section_phase3 | Phase-3 SaaS (Reserved) | Section Break | 0 |
| instance_id | Instance ID | Data | 0 |
| tenant_id | Tenant ID | Data | 0 |
| section_features | Feature Entitlements | Section Break | 0 |
| features | Features | Table | 0 |
| section_activity | Activity Log | Section Break | 0 |
| activity_log | Activity Log | Table | 0 |
| section_validation | Validation History | Section Break | 0 |
| validation_history | Validation History | Table | 0 |

### SMRITI License Activity Log
* **Artifact ID:** `ART-DOCTYPE-00050`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_license_activity_log/smriti_license_activity_log.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| timestamp | Timestamp | Datetime | 0 |
| action | Action | Select | 0 |
| performed_by | Performed By | Link | 0 |
| result | Result | Data | 0 |
| remarks | Remarks | Small Text | 0 |

### SMRITI License Features
* **Artifact ID:** `ART-DOCTYPE-00051`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_license_features/smriti_license_features.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| feature_code | Feature Code | Data | 1 |
| feature_name | Feature Name | Data | 0 |
| enabled | Enabled | Check | 0 |
| tier_minimum | Tier Minimum | Select | 0 |
| restriction_level | Restriction Level (Grace Period) | Select | 0 |

### SMRITI License Validation History
* **Artifact ID:** `ART-DOCTYPE-00052`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_license_validation_history/smriti_license_validation_history.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| timestamp | Timestamp | Datetime | 0 |
| validation_type | Validation Type | Select | 0 |
| result | Result | Data | 0 |
| signature_check_result | Signature Check Result | Select | 0 |
| remarks | Remarks | Small Text | 0 |

### SMRITI Loyalty Program
* **Artifact ID:** `ART-DOCTYPE-00053`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_loyalty_program/smriti_loyalty_program.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| program_name | Program Name | Data | 1 |
| description | Description | Small Text | 0 |
| linked_erpnext_program | Linked ERPNext Program | Link | 0 |

### SMRITI Loyalty Rule
* **Artifact ID:** `ART-DOCTYPE-00054`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_loyalty_rule/smriti_loyalty_rule.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| rule_name | Rule Name | Data | 1 |
| version | Version | Int | 1 |
| status | Status | Select | 1 |
| effective_from | Effective From | Date | 0 |
| effective_to | Effective To | Date | 0 |
| supersedes_rule | Supersedes Rule | Link | 0 |
| rule_type | Rule Type | Select | 1 |
| dimension | Dimension | Select | 1 |
| dimension_doctype | Dimension DocType | Select | 1 |
| dimension_value | Dimension Value | Dynamic Link | 1 |
| rule_value | Rule Value | Float | 1 |
| priority | Priority | Int | 0 |
| allow_stack | Allow Stacking | Check | 0 |

### SMRITI Loyalty Tier
* **Artifact ID:** `ART-DOCTYPE-00055`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_loyalty_tier/smriti_loyalty_tier.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| tier_name | Tier Name | Data | 1 |
| min_points | Minimum Points | Float | 1 |
| tier_multiplier | Tier Multiplier | Float | 1 |
| validity_months | Validity (Months) | Int | 0 |
| active | Active | Check | 0 |
| tier_benefits | Tier Benefits | Text | 0 |

### SMRITI Membership Tier
* **Artifact ID:** `ART-DOCTYPE-00056`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_membership_tier/smriti_membership_tier.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| tier_name | Tier Name | Data | 1 |
| min_points | Minimum Points | Float | 1 |
| min_lifetime_spend | Minimum Lifetime Spend | Currency | 0 |
| tier_multiplier | Tier Multiplier | Float | 1 |
| active | Active | Check | 0 |

### SMRITI Merchandise Category
* **Artifact ID:** `ART-DOCTYPE-00057`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_merchandise_category/smriti_merchandise_category.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_value | Value | Data | 1 |

### SMRITI Outsole
* **Artifact ID:** `ART-DOCTYPE-00058`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_outsole/smriti_outsole.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_value | Value | Data | 1 |

### SMRITI Party Physical Item
* **Artifact ID:** `ART-DOCTYPE-00059`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_party_physical_item/smriti_party_physical_item.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| item_code | Item Code | Link | 1 |
| system_qty | System Qty | Float | 0 |
| physical_qty | Physical Qty | Float | 1 |
| variance | Variance | Float | 0 |
| variance_reason | Variance Reason | Select | 0 |

### SMRITI Party Physical Snapshot
* **Artifact ID:** `ART-DOCTYPE-00060`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_party_physical_snapshot/smriti_party_physical_snapshot.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| party_stock_account | Party Stock Account | Link | 1 |
| audit_date | Audit Date | Date | 1 |
| status | Status | Select | 0 |
| approved_by | Approved By | Link | 0 |
| approved_on | Approved On | Datetime | 0 |
| items | Snapshot Items | Table | 0 |

### SMRITI Party Sales Item
* **Artifact ID:** `ART-DOCTYPE-00061`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_party_sales_item/smriti_party_sales_item.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| date | Date | Date | 0 |
| item_code | Item Code | Link | 1 |
| qty_sold | Quantity Sold | Float | 1 |

### SMRITI Party Sales Upload
* **Artifact ID:** `ART-DOCTYPE-00062`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_party_sales_upload/smriti_party_sales_upload.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| party_stock_account | Party Stock Account | Link | 1 |
| period_start_date | Period Start Date | Date | 1 |
| period_end_date | Period End Date | Date | 1 |
| excel_file | Upload Excel File | Attach | 0 |
| file_hash | File Hash | Data | 0 |
| status | Status | Select | 0 |
| items | Sales Items | Table | 0 |

### SMRITI Party Stock Account
* **Artifact ID:** `ART-DOCTYPE-00063`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_party_stock_account/smriti_party_stock_account.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| customer | Customer | Link | 1 |
| location_name | Location Name | Data | 1 |
| zone | Zone | Select | 0 |
| region | Region | Data | 0 |
| area_manager | Area Manager | Link | 0 |
| contact_person | Contact Person | Data | 0 |
| mobile | Mobile | Data | 0 |
| email | Email | Data | 0 |
| active | Active | Check | 0 |
| status | Status | Select | 0 |
| sb_tracking | Tracking Configuration | Section Break | 0 |
| tracking_mode | Tracking Mode | Select | 0 |
| pos_enabled | POS Integrated | Check | 0 |
| sales_upload_enabled | Sales Upload Enabled | Check | 0 |
| audit_enabled | Physical Audit Enabled | Check | 0 |
| auto_reorder_enabled | Auto Reorder Evaluation | Check | 0 |

### SMRITI Party Stock Ledger Entry
* **Artifact ID:** `ART-DOCTYPE-00064`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_party_stock_ledger_entry/smriti_party_stock_ledger_entry.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| posting_datetime | Posting Datetime | Datetime | 1 |
| party_stock_account | Party Stock Account | Link | 1 |
| item_code | Item Code | Link | 1 |
| qty | Quantity | Float | 1 |
| voucher_type | Voucher Type | Select | 1 |
| voucher_no | Voucher No | Data | 1 |
| unique_hash | Unique Hash | Data | 1 |
| adjustment_type | Adjustment Type | Select | 0 |
| reason | Reason | Small Text | 0 |
| approved_by | Approved By | Link | 0 |
| approved_on | Approved On | Datetime | 0 |

### SMRITI Print Job
* **Artifact ID:** `ART-DOCTYPE-00065`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_print_job/smriti_print_job.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| job_id | Job ID | Data | 0 |
| item_code | Item Code | Link | 0 |
| barcode | Barcode | Data | 0 |
| template_name | Template Name | Data | 0 |
| printer_ip | Printer IP | Data | 0 |
| printer_port | Printer Port | Int | 0 |
| print_qty | Print Qty | Int | 0 |
| payload_hash | Payload Hash | Data | 0 |
| payload_preview | Payload Preview | Data | 0 |
| status | Status | Select | 0 |
| error_message | Error Message | Text | 0 |
| created_by | Created By | Data | 0 |
| created_on | Created On | Datetime | 0 |
| completed_on | Completed On | Datetime | 0 |

### SMRITI Print Template
* **Artifact ID:** `ART-DOCTYPE-00066`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_print_template/smriti_print_template.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| template_title | Template Title | Data | 1 |
| label_size | Label Size | Select | 1 |
| printer_language | Printer Language | Select | 1 |
| printer_family | Printer Family | Select | 1 |
| raw_template | Raw PRN Template | Code | 1 |
| custom_field_mappings_json | Field Mappings JSON | Long Text | 0 |
| custom_visual_layout_json | Visual Layout JSON | Long Text | 0 |
| custom_version | Template Version | Data | 0 |
| custom_active | Active | Check | 0 |
| custom_is_default | Is Default | Check | 0 |
| template_checksum | Template Checksum | Data | 0 |

### SMRITI Print Template Version
* **Artifact ID:** `ART-DOCTYPE-00067`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_print_template_version/smriti_print_template_version.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| template | Parent Template | Link | 1 |
| version_number | Version Number | Data | 1 |
| version_label | Version Label/Notes | Data | 0 |
| raw_template | Raw PRN Template | Code | 1 |
| custom_field_mappings_json | Field Mappings JSON | Long Text | 0 |
| custom_visual_layout_json | Visual Layout JSON | Long Text | 0 |
| template_checksum | Template Checksum | Data | 0 |
| restored_from_version | Restored From Version | Data | 0 |
| change_timestamp | Change Timestamp | Datetime | 0 |
| changed_by | Changed By | Link | 0 |

### SMRITI Promotion Rule
* **Artifact ID:** `ART-DOCTYPE-00068`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_promotion_rule/smriti_promotion_rule.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| campaign | Campaign | Link | 1 |
| rule_name | Rule Name | Data | 1 |
| valid_from | Valid From | Date | 1 |
| valid_upto | Valid Upto | Date | 1 |
| apply_on | Apply On | Select | 1 |
| dimension_value | Dimension Value | Data | 0 |
| discount_type | Discount Type | Select | 1 |
| discount_value | Discount Value | Float | 1 |
| priority | Priority | Int | 0 |

### SMRITI Provision Log
* **Artifact ID:** `ART-DOCTYPE-00069`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_provision_log/smriti_provision_log.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| run_id | Run ID | Data | 0 |
| step_sequence | Step # | Int | 0 |
| column_break_1 |  | Column Break | 0 |
| activation | Activation | Link | 1 |
| operator | Operator | Link | 0 |
| section_break_step | Step Details | Section Break | 0 |
| step_name | Step Name | Data | 0 |
| step_status | Step Status | Select | 0 |
| column_break_2 |  | Column Break | 0 |
| step_time | Step Time | Datetime | 0 |
| section_break_msg | Message / Error | Section Break | 0 |
| step_message | Step Message | Small Text | 0 |

### SMRITI PSV Activity Log
* **Artifact ID:** `ART-DOCTYPE-00070`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_activity_log/smriti_psv_activity_log.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| timestamp | Timestamp | Datetime | 1 |
| user | User | Link | 1 |
| action_type | Action Type | Select | 1 |
| event_type | Event Type | Data | 0 |
| party_stock_account | Party Stock Account | Link | 0 |
| reference_doctype | Reference DocType | Data | 0 |
| reference_name | Reference Name | Data | 0 |
| ip_address | IP Address | Data | 0 |
| details | Details | Small Text | 0 |

### SMRITI PSV Exam Attempt
* **Artifact ID:** `ART-DOCTYPE-00071`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_exam_attempt/smriti_psv_exam_attempt.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attempt_id | Attempt ID | Data | 1 |
| user | User | Link | 1 |
| exam_id | Exam Reference | Link | 1 |
| start_time | Start Time | Datetime | 1 |
| end_time | End Time | Datetime | 0 |
| score | Score (%) | Percent | 0 |
| correct_answers | Correct Answers | Int | 0 |
| total_questions | Total Questions | Int | 0 |
| status | Status | Select | 1 |
| submitted_answers_json | Submitted Answers (JSON) | Long Text | 0 |
| certificate_hash | Certificate Hash | Data | 0 |

### SMRITI PSV Exception Record
* **Artifact ID:** `ART-DOCTYPE-00072`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_exception_record/smriti_psv_exception_record.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| timestamp | Timestamp | Datetime | 1 |
| party_stock_account | Party Stock Account | Link | 1 |
| alert_key | Alert Key | Data | 0 |
| alert_type | Alert Type | Select | 0 |
| severity | Severity | Select | 0 |
| last_seen | Last Seen | Datetime | 0 |
| sales_invoice | Sales Invoice | Link | 0 |
| item_code | Item Code | Link | 0 |
| missing_qty | Missing Qty | Float | 0 |
| status | Status | Select | 0 |
| reconciliation_notes | Reconciliation Notes | Small Text | 0 |
| reconciled_by | Reconciled By | Link | 0 |
| reconciled_on | Reconciled On | Datetime | 0 |

### SMRITI PSV Reorder Rule
* **Artifact ID:** `ART-DOCTYPE-00073`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_reorder_rule/smriti_psv_reorder_rule.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| party_stock_account | Party Stock Account | Link | 1 |
| item_group | Item Group (Group-level fallback) | Link | 0 |
| item_variant | Item Variant (Highest Priority) | Link | 0 |
| section_break_stock | Stock Parameters | Section Break | 0 |
| min_stock | Minimum Stock | Float | 0 |
| max_stock | Maximum Stock (Replenishment Cap) | Float | 0 |
| column_break_1 |  | Column Break | 0 |
| safety_stock | Safety Stock | Float | 0 |
| lead_time_days | Lead Time (Days) | Int | 0 |
| target_days_cover | Target Days Cover | Int | 0 |
| section_break_status |  | Section Break | 0 |
| active | Active | Check | 0 |

### SMRITI PSV Settings
* **Artifact ID:** `ART-DOCTYPE-00074`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_settings/smriti_psv_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| upload_frequency | Upload Frequency | Select | 0 |
| velocity_weight | Velocity Weight (0.0 - 1.0) | Float | 0 |
| ageing_weight | Ageing Weight (0.0 - 1.0) | Float | 0 |
| accuracy_weight | Accuracy Weight (0.0 - 1.0) | Float | 0 |
| discipline_weight | Discipline Weight (0.0 - 1.0) | Float | 0 |
| alert_variance_percentage | Alert Variance Limit (%) | Float | 0 |
| allow_negative_on_snapshot | Allow Negative Balances | Check | 0 |
| section_break_health | Health Monitoring | Section Break | 0 |
| health_check_enabled | Enable Daily Health Check | Check | 0 |
| section_break_reorder | V1.1 Reorder Intelligence Defaults | Section Break | 0 |
| default_lead_time_days | Default Lead Time (Days) | Int | 0 |
| default_safety_stock | Default Safety Stock | Float | 0 |
| default_target_days_cover | Default Target Days Cover | Int | 0 |
| reorder_avg_weeks | Sale Average Lookback (Weeks) | Int | 0 |
| section_break_pdt_forecasting | PDT Forecasting Parameters | Section Break | 0 |
| ema_alpha | EMA Alpha (Forecast Smoothing) | Float | 0 |
| variant_dimension | Variant Dimension Attribute | Data | 0 |

### SMRITI PSV Transaction
* **Artifact ID:** `ART-DOCTYPE-00075`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_transaction/smriti_psv_transaction.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| party_stock_account | Party Stock Account | Link | 1 |
| posting_date | Posting Date | Date | 1 |
| transaction_type | Transaction Type | Select | 1 |
| company | Company | Link | 1 |
| cb_header |  | Column Break | 0 |
| reference_doctype | Reference DocType | Link | 0 |
| reference_name | Reference Name | Dynamic Link | 0 |
| mapping_fingerprint | Mapping Fingerprint | Data | 0 |
| opening_import_batch | Opening Import Batch | Data | 0 |
| sb_items | Items | Section Break | 0 |
| items | Items | Table | 1 |
| sb_status | Status | Section Break | 0 |
| status | Status | Select | 0 |
| amended_from | Amended From | Link | 0 |
| remarks | Remarks | Small Text | 0 |

### SMRITI PSV Transaction Item
* **Artifact ID:** `ART-DOCTYPE-00076`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_transaction_item/smriti_psv_transaction_item.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| item_code | Item Variant | Link | 1 |
| qty | Qty | Float | 1 |
| rate | Rate | Currency | 0 |
| reason | Reason/Note | Data | 0 |

### SMRITI Purchase Class
* **Artifact ID:** `ART-DOCTYPE-00077`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_purchase_class/smriti_purchase_class.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_value | Value | Data | 1 |

### SMRITI Related Formula
* **Artifact ID:** `ART-DOCTYPE-00078`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_related_formula/smriti_related_formula.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| formula_id | Formula ID | Link | 1 |

### SMRITI Related Term
* **Artifact ID:** `ART-DOCTYPE-00079`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_related_term/smriti_related_term.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| related_term_id | Related Term ID | Link | 1 |

### SMRITI Report Role
* **Artifact ID:** `ART-DOCTYPE-00080`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_report_role/smriti_report_role.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| role | Role | Link | 1 |
| export_allowed | Export Allowed | Check | 0 |

### SMRITI Report Template
* **Artifact ID:** `ART-DOCTYPE-00081`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_report_template/smriti_report_template.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| report_key | Report Key | Data | 1 |
| report_name | Report Name | Data | 1 |
| report_category | Report Category | Select | 1 |
| source_doctype | Source DocType | Link | 0 |
| columns_json | Columns JSON | Long Text | 0 |
| filters_json | Filters JSON | Long Text | 0 |
| group_by | Group By | Data | 0 |
| order_by | Order By | Data | 0 |
| branch_restricted | Branch Restricted | Check | 0 |
| company_restricted | Company Restricted | Check | 0 |
| cache_minutes | Cache Minutes | Int | 0 |
| schema_version | Schema Version | Int | 0 |
| template_version | Template Version | Int | 0 |
| layout_json | Layout JSON | Long Text | 0 |
| chart_json | Chart JSON | Long Text | 0 |
| pivot_json | Pivot JSON | Long Text | 0 |
| widget_json | Widget JSON | Long Text | 0 |
| is_public | Is Public | Check | 0 |
| role_access | Role Access | Table | 0 |

### SMRITI Rule Evaluation Log
* **Artifact ID:** `ART-DOCTYPE-00082`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_rule_evaluation_log/smriti_rule_evaluation_log.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| invoice | Invoice | Link | 1 |
| rule_name | Rule Name | Data | 0 |
| rule_type | Rule Type | Select | 1 |
| status | Status | Select | 1 |
| reason | Reason | Text | 0 |
| multiplier | Multiplier | Float | 0 |
| discount_amount | Discount Amount | Float | 0 |
| timestamp | Timestamp | Datetime | 1 |

### SMRITI Sales KPI Snapshot
* **Artifact ID:** `ART-DOCTYPE-00083`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_sales_kpi_snapshot/smriti_sales_kpi_snapshot.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| employee | Employee | Link | 1 |
| store | Store | Link | 1 |
| date | Date | Date | 1 |
| revenue | Revenue | Currency | 0 |
| transactions | Transactions | Int | 0 |
| customers | Customers | Int | 0 |
| company | Company | Link | 1 |

### SMRITI Sales Target
* **Artifact ID:** `ART-DOCTYPE-00084`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_sales_target/smriti_sales_target.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| employee | Employee | Link | 1 |
| company | Company | Link | 1 |
| fiscal_year | Fiscal Year | Link | 1 |
| month | Month | Select | 1 |
| target_amount | Target Amount | Currency | 1 |
| target_qty | Target Qty | Float | 0 |

### SMRITI Saved View
* **Artifact ID:** `ART-DOCTYPE-00085`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_saved_view/smriti_saved_view.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| view_name | View Name | Data | 1 |
| report_template | Report Template | Link | 1 |
| user | User | Link | 1 |
| applied_filters_json | Applied Filters JSON | Long Text | 0 |
| visible_columns_json | Visible Columns JSON | Long Text | 0 |
| is_default | Is Default | Check | 0 |

### SMRITI SFM Settings
* **Artifact ID:** `ART-DOCTYPE-00086`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_sfm_settings/smriti_sfm_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| enable_sfm | Enable SFM | Check | 0 |
| ownership_precedence | Ownership Precedence | Check | 0 |
| primary_split_pct | Primary split percentage | Percent | 0 |
| secondary_split_pct | Secondary split percentage | Percent | 0 |
| walkin_employee | Walk-In Fallback Employee | Link | 0 |

### SMRITI SKU Twin
* **Artifact ID:** `ART-DOCTYPE-00087`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_sku_twin/smriti_sku_twin.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| company | Company | Link | 1 |
| party_stock_account | Party Stock Account | Link | 1 |
| item_code | Item Code | Link | 1 |
| current_stock | Current Stock | Float | 0 |
| weekly_velocity | Weekly Velocity | Float | 0 |
| velocity_confidence | Velocity Confidence | Float | 0 |
| velocity_std_dev | Velocity Std Dev | Float | 0 |
| weeks_of_cover | Weeks of Cover | Float | 0 |
| dead_stock_score | Dead Stock Score | Float | 0 |
| dead_stock_probability | Dead Stock Probability | Select | 0 |
| reorder_suggestion | Reorder Suggestion | Float | 0 |
| transfer_benefit_score | Transfer Benefit Score | Float | 0 |
| recommended_transfer_source | Recommended Transfer Source | Link | 0 |
| recommended_transfer_qty | Recommended Transfer Qty | Float | 0 |
| twin_state | Twin State | Select | 0 |
| forecast_version | Forecast Version | Data | 0 |
| forecast_date | Forecast Date | Date | 0 |
| forecast_model | Forecast Model | Data | 0 |
| forecast_parameters | Forecast Parameters | Long Text | 0 |
| recommendation_type | Recommendation Type | Select | 0 |
| reason_codes | Reason Codes | Long Text | 0 |
| recommendation_reason | Recommendation Reason | Long Text | 0 |
| last_recalculated | Last Recalculated | Datetime | 0 |
| freshness_status | Freshness Status | Select | 0 |
| twin_quality_score | Twin Quality Score | Float | 0 |
| twin_quality_status | Twin Quality Status | Select | 0 |
| variant_curve_status | Variant Curve Status | Select | 0 |
| missing_sizes | Missing Sizes | Long Text | 0 |
| cache_version | Cache Version | Data | 0 |
| next_recalculation_due | Next Recalculation Due | Datetime | 0 |
| source_event | Source Event | Select | 0 |
| seasonality_factor | Seasonality Factor | Float | 0 |
| supplier_lead_days | Supplier Lead Days | Int | 0 |
| predicted_stockout_date | Predicted Stockout Date | Date | 0 |
| metadata_json | Metadata JSON | Long Text | 0 |

### SMRITI Store
* **Artifact ID:** `ART-DOCTYPE-00088`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_store/smriti_store.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| store_name | Store Name | Data | 1 |
| default_warehouse | Default Warehouse | Link | 0 |
| company | Company | Link | 1 |

### SMRITI Sub Category
* **Artifact ID:** `ART-DOCTYPE-00089`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_sub_category/smriti_sub_category.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_value | Value | Data | 1 |

### SMRITI Trial Activation
* **Artifact ID:** `ART-DOCTYPE-00090`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_trial_activation/smriti_trial_activation.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| activation_reference | Activation Reference | Data | 0 |
| activation_type | Activation Type | Select | 1 |
| trial_lead | Trial Lead | Link | 1 |
| column_break_1 |  | Column Break | 0 |
| store_name | Store Name | Data | 0 |
| owner_name | Owner Name | Data | 0 |
| mobile | Mobile | Data | 0 |
| section_break_provisioning | Provisioning Details | Section Break | 0 |
| company_name | Company Name (ERPNext) | Data | 0 |
| activation_status | Activation Status | Select | 0 |
| column_break_2 |  | Column Break | 0 |
| trial_start_date | Trial Start Date | Datetime | 0 |
| trial_end_date | Trial End Date | Datetime | 0 |
| activated_by | Activated By | Link | 0 |
| section_break_provision_ops | Provisioning Operations | Section Break | 0 |
| provision_run_id | Last Provision Run ID | Data | 0 |
| retry_count | Retry Count | Int | 0 |
| column_break_3 |  | Column Break | 0 |
| last_failure_reason | Last Failure Reason | Small Text | 0 |
| section_break_reminders | Reminder Tracking | Section Break | 0 |
| reminder_7d_sent | D-7 Reminder Sent | Check | 0 |
| reminder_3d_sent | D-3 Reminder Sent | Check | 0 |
| reminder_1d_sent | D-1 Reminder Sent | Check | 0 |
| section_break_checklist | Onboarding Checklist | Section Break | 0 |
| checklist | Checklist | Table | 0 |
| section_break_notes | Notes | Section Break | 0 |
| notes | Notes | Small Text | 0 |

### SMRITI Trial Checklist
* **Artifact ID:** `ART-DOCTYPE-00091`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_trial_checklist/smriti_trial_checklist.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| task_name | Task | Select | 1 |
| is_done | Done | Check | 0 |
| column_break_1 |  | Column Break | 0 |
| done_by | Done By | Link | 0 |
| done_at | Done At | Datetime | 0 |

### SMRITI Trial Lead
* **Artifact ID:** `ART-DOCTYPE-00092`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_trial_lead/smriti_trial_lead.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| store_name | Store Name | Data | 1 |
| owner_name | Owner Name | Data | 1 |
| mobile | Mobile | Data | 1 |
| city | City | Data | 0 |
| business_type | Business Type | Data | 0 |
| plan_selected | Plan Selected | Select | 0 |
| warehouses | Warehouses | Int | 0 |
| monthly_sales | Monthly Sales (₹) | Currency | 0 |
| source | Source | Data | 0 |
| status | Status | Select | 0 |
| submitted_at | Submitted At | Datetime | 0 |
| notes | Notes | Small Text | 0 |

### SMRITI Trial Settings
* **Artifact ID:** `ART-DOCTYPE-00093`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_trial_settings/smriti_trial_settings.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| section_reminders | Trial Reminder Configuration | Section Break | 0 |
| reminder_days | Reminder Days | Data | 0 |
| reminder_email_sender | Reminder Email Sender | Data | 0 |
| section_break_1 | Provisioning Configuration | Section Break | 0 |
| stale_provisioning_hours | Stale Provisioning Threshold (hours) | Int | 0 |
| admin_notification_email | Admin Notification Email | Data | 0 |
| section_break_health | Health Check | Section Break | 0 |
| enable_health_check | Enable Daily Health Check | Check | 0 |
| health_check_log_days | Health Log Retention (days) | Int | 0 |

### SMRITI Upper Material
* **Artifact ID:** `ART-DOCTYPE-00094`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_upper_material/smriti_upper_material.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| attribute_value | Value | Data | 1 |

### SMRITI Walk In Analytics
* **Artifact ID:** `ART-DOCTYPE-00095`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_walk_in_analytics/smriti_walk_in_analytics.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| date | Date | Date | 1 |
| store | Store | Link | 1 |
| total_walk_ins | Total Walk-Ins | Int | 1 |
| total_conversions | Conversions | Int | 1 |
| conversion_rate | Conversion Rate | Percent | 1 |
| total_revenue | Total Revenue | Currency | 1 |
| avg_engagement_minutes | Avg Engagement (Minutes) | Float | 1 |
| outlet_conversion_index | Outlet Conversion Index | Float | 0 |
| executive_performance_index | Executive Performance Index | Float | 0 |
| store_retention_index | Store Retention Index | Float | 0 |

### SMRITI Walk In Visit
* **Artifact ID:** `ART-DOCTYPE-00096`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_walk_in_visit/smriti_walk_in_visit.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| visit_date | Visit Date | Date | 1 |
| visit_time | Visit Time | Time | 1 |
| store | Store | Link | 1 |
| executive | Sales Executive | Link | 0 |
| customer | Customer | Link | 0 |
| customer_phone | Customer Phone | Data | 0 |
| status | Funnel Status | Select | 1 |
| reason_for_no_purchase | Exit Reason | Select | 0 |
| sales_invoice | Attributed Invoice | Link | 0 |
| pos_invoice | Attributed POS Invoice | Link | 0 |
| engagement_duration | Engagement (Minutes) | Int | 0 |
| remarks | Remarks | Small Text | 0 |

### SMRITI Wallet Ledger
* **Artifact ID:** `ART-DOCTYPE-00097`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_ledger/smriti_wallet_ledger.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| ledger_sequence | Ledger Sequence | Data | 0 |
| customer | Customer | Link | 1 |
| company | Company | Link | 0 |
| wallet_type | Wallet Type | Select | 1 |
| transaction_type | Transaction Type | Select | 1 |
| amount | Amount | Currency | 1 |
| balance_remaining | Balance Remaining | Currency | 0 |
| reference_invoice | Reference Invoice | Link | 0 |
| expiry_date | Expiry Date | Date | 0 |
| journal_entry | Journal Entry | Link | 0 |
| is_reversal | Is Reversal | Check | 0 |
| is_expired | Is Expired | Check | 0 |
| remarks | Remarks | Small Text | 0 |

### SMRITI Wallet Reconciliation Snapshot
* **Artifact ID:** `ART-DOCTYPE-00098`
* **Schema Origin:** `apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_reconciliation_snapshot/smriti_wallet_reconciliation_snapshot.json`
* **Evidence Type:** `JSON`

| Fieldname | Label | Fieldtype | Mandatory |
| :--- | :--- | :--- | :--- |
| snapshot_date | Snapshot Date | Date | 1 |
| wallet_total | Wallet Total | Currency | 1 |
| ledger_total | Ledger Total | Currency | 1 |
| variance | Variance | Currency | 1 |
| status | Status | Select | 1 |
| details | Details | Text | 0 |
