# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/seed_default_terms.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
import json

def execute():
    """
    Migration patch to seed 20 default SMRITI Business Dictionary terms.
    Uses a 2-phase approach to avoid forward-reference LinkValidationErrors.
    """
    default_terms = [
        {
            "term_id": "PSA",
            "term_name": "Party Stock Account",
            "term_category": "Distribution",
            "definition": "Party Stock Account maintains the ledger balances and shadow accounting of stock held by channel partners.",
            "hinglish_definition": "Distributors ya channel partners ke stock balances aur shadow ledger calculations ko track karne wala internal ledger master.",
            "term_aliases": ["PSA", "Stock Account", "Channel Account"],
            "manual_reference": "Volume 3 > Distribution Operations",
            "training_reference": "TRN-DIST-PSA",
            "related_formulas": [],
            "related_terms": ["PSV", "Party Stock Ledger"],
            "faq": [
                {"q": "Does PSA replace ERPNext warehouses?", "a": "No, it reads ERPNext master data but acts as an independent shadow ledger."}
            ],
            "common_mistakes": [
                {"mistake": "Updating general ledger direct", "a": "PSA should never write directly to ERPNext General Ledger."}
            ]
        },
        {
            "term_id": "PSV",
            "term_name": "Party Stock Visibility",
            "term_category": "Distribution",
            "definition": "Party Stock Visibility provides real-time insights into distributor and dealer inventory levels.",
            "hinglish_definition": "Distributors aur secondary retail outlets ke stock levels aur sell-through activity ko monitor karne ki central visual tracking facility.",
            "term_aliases": ["PSV", "Channel Stock Visibility", "Partner Stock"],
            "manual_reference": "Volume 3 > Inventory Analytics",
            "training_reference": "TRN-DIST-PSV",
            "related_formulas": ["SAL-001"],
            "related_terms": ["PSA", "Party Stock Ledger"],
            "faq": [
                {"q": "What is primary visibility source?", "a": "Daily partner sales uploads and dispatch sync inputs."}
            ],
            "common_mistakes": [
                {"mistake": "Mixing company warehouse with partner stock", "a": "Partner stock belongs to distributors, not the company warehouses."}
            ]
        },
        {
            "term_id": "PDT",
            "term_name": "Predictive Distribution Twin",
            "term_category": "Forecasting",
            "definition": "Predictive Distribution Twin utilizes historical demand, lead time, and variance parameters to optimize replenishment across outlets.",
            "hinglish_definition": "Sales history, lead time, aur safety stock factors ke analytics par chalne wala intelligent store replenishment algorithm.",
            "term_aliases": ["PDT", "Replenishment Engine", "Stock Planner"],
            "manual_reference": "Volume 4 > Replenishment Science",
            "training_reference": "TRN-PDT-01",
            "related_formulas": ["FRC-001", "TRF-001"],
            "related_terms": ["WOC", "Reorder Suggestion"],
            "faq": [
                {"q": "How often does PDT rebuild?", "a": "Automatically overnight, or manually from the PDT dashboard."}
            ],
            "common_mistakes": [
                {"mistake": "Running plan without approving registry rules", "a": "Always ensure CGE and reorder rules are approved."}
            ]
        },
        {
            "term_id": "WOC",
            "term_name": "Weeks of Cover",
            "term_category": "Inventory",
            "definition": "Weeks of Cover is the duration in weeks that current stock will last based on standard weekly sales velocity.",
            "hinglish_definition": "Warehouse ya store mein pada hua stock, average weekly sales velocity ke hisaab se kitne weeks tak chalega.",
            "term_aliases": ["WOC", "Weeks of Cover", "Inventory Coverage", "Stock Cover"],
            "manual_reference": "Volume 3 > Inventory Control",
            "training_reference": "TRN-INV-WOC",
            "related_formulas": ["INV-002"],
            "related_terms": ["Sales Velocity", "Stockout Risk"],
            "faq": [
                {"q": "What is normal safety WOC limit?", "a": "Typically 3 to 4 weeks depending on replenishment lead time."}
            ],
            "common_mistakes": [
                {"mistake": "Ignoring seasonal velocity changes", "a": "Static WOC calculations during festival seasons will lead to stockouts."}
            ]
        },
        {
            "term_id": "Sales Velocity",
            "term_name": "Sales Velocity",
            "term_category": "Sales",
            "definition": "Weekly sales velocity calculated over a lookback window (standard 30 days).",
            "hinglish_definition": "Kisi specific period (lookback window) ke sales data par calculate ki gayi average weekly product sales velocity.",
            "term_aliases": ["Sales Velocity", "Velocity", "Weekly Sales Rate"],
            "manual_reference": "Volume 3 > Sales Analytics",
            "training_reference": "TRN-SAL-VEL",
            "related_formulas": ["INV-001"],
            "related_terms": ["WOC"],
            "faq": [
                {"q": "Why 30-day default window?", "a": "To smooth out short-term weekend spikes while retaining recent demand trends."}
            ],
            "common_mistakes": [
                {"mistake": "Using velocity on new launches", "a": "For items with < 14 days history, use variant curves instead of sales velocity."}
            ]
        },
        {
            "term_id": "Forecast Confidence",
            "term_name": "Forecast Confidence Score",
            "term_category": "Forecasting",
            "definition": "Calculated score indicating reliability of forecasted demand based on demand volatility (Coefficient of Variation).",
            "hinglish_definition": "Demand volatility ke parameters (Coefficient of Variation) par system forecast confidence score check karta hai.",
            "term_aliases": ["Forecast Confidence", "Confidence Score", "Forecasting Reliability"],
            "manual_reference": "Volume 4 > Forecasting Science",
            "training_reference": "TRN-FRC-CONF",
            "related_formulas": ["FRC-001"],
            "related_terms": ["PDT", "Reorder Suggestion"],
            "faq": [
                {"q": "What lowers confidence?", "a": "Erratic sales, highly sparse transaction history, and frequent stockouts."}
            ],
            "common_mistakes": [
                {"mistake": "Assuming 100% confidence means exact sales", "a": "Forecast is probabilistic; always consider lead time tolerance."}
            ]
        },
        {
            "term_id": "Dead Stock",
            "term_name": "Dead Stock Score",
            "term_category": "Inventory",
            "definition": "Evaluates stock aging and inactive sales duration to calculate stock liquidation priority score.",
            "hinglish_definition": "Aise inventory items jo kaafi time se sell nahi hue hain, unki static duration par dead stock score nikaala jaata hai.",
            "term_aliases": ["Dead Stock", "Liquidation Score", "Slow Moving Stock"],
            "manual_reference": "Volume 3 > Inventory Valuation",
            "training_reference": "TRN-INV-DEAD",
            "related_formulas": ["INV-003"],
            "related_terms": ["WOC"],
            "faq": [
                {"q": "When is an item marked critical?", "a": "When inactive days exceed 90 days with positive stock value."}
            ],
            "common_mistakes": [
                {"mistake": "Failing to discount dead stock early", "a": "Liquidation margins drop further the longer dead stock stays on shelves."}
            ]
        },
        {
            "term_id": "Sell Through",
            "term_name": "Sell Through Percentage",
            "term_category": "Sales",
            "definition": "Percentage of received inventory sold within a specified sales cycle.",
            "hinglish_definition": "Ek specific stock batch mein se kitne percent mal customer ko sell ho chuka hai (total sales quantity divided by opening stock plus receipts).",
            "term_aliases": ["Sell Through", "Sell Through %", "ST%"],
            "manual_reference": "Volume 3 > Sales Performance",
            "training_reference": "TRN-SAL-ST",
            "related_formulas": ["SAL-001"],
            "related_terms": ["Sales Velocity"],
            "faq": [
                {"q": "What is a healthy ST%?", "a": "Above 60% within 8 weeks of launch is considered strong retail performance."}
            ],
            "common_mistakes": [
                {"mistake": "Excluding initial opening stock", "a": "Always add initial opening stock in the denominator to reflect true visibility."}
            ]
        },
        {
            "term_id": "Stock Accuracy",
            "term_name": "Stock Accuracy Score",
            "term_category": "Audit",
            "definition": "Measures variance between physical inventory count values and system ledger balances.",
            "hinglish_definition": "Physical counting inventory aur system ledger balances ke differences ka variance percentage calculation.",
            "term_aliases": ["Stock Accuracy", "Audit Score", "Inventory Accuracy"],
            "manual_reference": "Volume 3 > Audit Compliance",
            "training_reference": "TRN-AUD-ACC",
            "related_formulas": ["AUD-001"],
            "related_terms": ["Physical Snapshot"],
            "faq": [
                {"q": "What is the acceptable variance?", "a": "Within +/- 0.5% for high-value fashion and footwear retail."}
            ],
            "common_mistakes": [
                {"mistake": "Not posting variance adjustment immediately", "a": "Delaying adjustments leads to wrong planning in PDT."}
            ]
        },
        {
            "term_id": "Inventory Turnover",
            "term_name": "Inventory Turnover Ratio",
            "term_category": "Inventory",
            "definition": "Ratio showing how many times a company's inventory is sold and replaced over a year.",
            "hinglish_definition": "Ek saal mein inventory kitni baar total replace ya rotate hoti hai (Cost of Goods Sold divided by average inventory value).",
            "term_aliases": ["Inventory Turnover", "Turnover Ratio", "ITR"],
            "manual_reference": "Volume 3 > Financial Inventory Control",
            "training_reference": "TRN-INV-TURN",
            "related_formulas": ["INV-004"],
            "related_terms": ["WOC", "Dead Stock"],
            "faq": [
                {"q": "What is normal turnover in apparel?", "a": "Usually 4 to 6 times a year."}
            ],
            "common_mistakes": [
                {"mistake": "Calculating using retail price", "a": "Turnover must always use Cost of Goods Sold (COGS), never selling prices."}
            ]
        },
        {
            "term_id": "Outlet Health Score",
            "term_name": "Outlet Health Score",
            "term_category": "Outlet",
            "definition": "Consolidated score combining sync delay performance and ledger stock count variance indicators.",
            "hinglish_definition": "Kisi specific store outlet ki inventory sync speed aur ledger reconciliation variances ka unified indicator score.",
            "term_aliases": ["Outlet Health Score", "OHS", "Store Health"],
            "manual_reference": "Volume 5 > Store Administration",
            "training_reference": "TRN-OUT-HEALTH",
            "related_formulas": ["OHS-001"],
            "related_terms": ["Stock Accuracy"],
            "faq": [
                {"q": "How often is OHS computed?", "a": "Recalculated every hour based on latest API request logs and audit snapshots."}
            ],
            "common_mistakes": [
                {"mistake": "Neglecting sync delay adjustments", "a": "Long offline sync gaps inflate OHS artificially before actual updates."}
            ]
        },
        {
            "term_id": "Transfer Benefit Score",
            "term_name": "Transfer Benefit Score",
            "term_category": "Distribution",
            "definition": "Calculates financial retaining benefit value of transferring stock between outlets versus origin stockout risk and transit freight costs.",
            "hinglish_definition": "Ek outlet se doosre outlet mal transfer karne par margin benefit aur freight cost ka comparison assessment score.",
            "term_aliases": ["Transfer Benefit Score", "TBS", "Transfer Optimization"],
            "manual_reference": "Volume 4 > Distribution Science",
            "training_reference": "TRN-DIST-TBS",
            "related_formulas": ["TRF-001"],
            "related_terms": ["PDT", "Lead Time"],
            "faq": [
                {"q": "What threshold triggers auto-suggestions?", "a": "Transfer benefit score must be positive after deducting freight cost."}
            ],
            "common_mistakes": [
                {"mistake": "Ignoring origin location demand velocity", "a": "Transferring hot-selling items from high demand outlets causes stockouts."}
            ]
        },
        {
            "term_id": "Physical Snapshot",
            "term_name": "Physical Inventory Snapshot",
            "term_category": "Audit",
            "definition": "A frozen state of ledger balances captured for auditing against physical warehouse count sheets.",
            "hinglish_definition": "Physical counting audit ke time, database ledger stocks ko freeze karke comparative sheet banana.",
            "term_aliases": ["Physical Snapshot", "Audit Snapshot", "Stock Freeze"],
            "manual_reference": "Volume 3 > Audit Compliance",
            "training_reference": "TRN-AUD-SNAP",
            "related_formulas": ["AUD-001"],
            "related_terms": ["Stock Accuracy"],
            "faq": [
                {"q": "Can billing run during snapshot?", "a": "Yes, SMRITI handles sales delta adjustments post-reconciliation automatically."}
            ],
            "common_mistakes": [
                {"mistake": "Counting stock without freezing ledger", "a": "Always freeze snapshot state before entering physical counts."}
            ]
        },
        {
            "term_id": "Party Stock Ledger",
            "term_name": "Party Stock Ledger",
            "term_category": "Distribution",
            "definition": "Records chronological transaction ledger logs of partner stock movement (Receipts, Sales, Returns).",
            "hinglish_definition": "Channel partner ke stock transactions (mal milna, customer ko bechna, return aana) ka chronologically detailed ledger book.",
            "term_aliases": ["Party Stock Ledger", "PSL", "Channel Ledger"],
            "manual_reference": "Volume 3 > Partner Operations",
            "training_reference": "TRN-DIST-LEDGER",
            "related_formulas": [],
            "related_terms": ["PSA", "PSV"],
            "faq": [
                {"q": "Are PSL entries editable?", "a": "No, all entries are cryptographically signed and locked."}
            ],
            "common_mistakes": [
                {"mistake": "Editing transactions post-audit", "a": "Never force db updates on ledger entries, use reversal transactions."}
            ]
        },
        {
            "term_id": "Reorder Suggestion",
            "term_name": "Reorder Suggestion",
            "term_category": "Forecasting",
            "definition": "Quantity recommendations generated by forecasting engines to replenish safety stocks.",
            "hinglish_definition": "Safety stock ko maintain karne ke liye forecasting algorithms dwara suggest ki gayi purchase quantity recommendation.",
            "term_aliases": ["Reorder Suggestion", "Reorder Recs", "Replenishment Qty"],
            "manual_reference": "Volume 4 > Replenishment Science",
            "training_reference": "TRN-PDT-REC",
            "related_formulas": ["INV-001", "INV-002"],
            "related_terms": ["PDT", "Stockout Risk"],
            "faq": [
                {"q": "How is suggestion priority set?", "a": "Based on current WOC status and daily sales speed metrics."}
            ],
            "common_mistakes": [
                {"mistake": "Exceeding warehouse budget limits", "a": "Always double check CGE budget reserves before submitting PO."}
            ]
        },
        {
            "term_id": "Stockout Risk",
            "term_name": "Stockout Risk Index",
            "term_category": "Forecasting",
            "definition": "Calculates probability of stocking out before the next replenishment delivery arrives based on lead time variance.",
            "hinglish_definition": " replenishment order aane se pehle store ka mal khatam hone ke risk ka statistical index probability score.",
            "term_aliases": ["Stockout Risk", "Out of Stock Risk", "SOR"],
            "manual_reference": "Volume 4 > Forecasting Science",
            "training_reference": "TRN-FRC-RISK",
            "related_formulas": ["INV-002"],
            "related_terms": ["WOC", "Lead Time"],
            "faq": [
                {"q": "What factors inflate SOR?", "a": "Supplier delivery delays, high sales speed spikes, and low safety stock buffers."}
            ],
            "common_mistakes": [
                {"mistake": "Configuring static lead times", "a": "Suppliers take longer during holiday seasons; lead time must be dynamic."}
            ]
        },
        {
            "term_id": "Variant Curve",
            "term_name": "Variant Size Curve",
            "term_category": "Inventory",
            "definition": "Represents the demand and stock distribution ratio across sizes or variants of a style.",
            "hinglish_definition": "Kisi product style ke different sizes aur variants ki demand and availability distribution ratio model.",
            "term_aliases": ["Variant Curve", "Size Curve", "Size Ratio"],
            "manual_reference": "Volume 3 > Variant Management",
            "training_reference": "TRN-INV-CURVE",
            "related_formulas": ["VAR-001"],
            "related_terms": ["Inventory Turnover"],
            "faq": [
                {"q": "Why is size curve important?", "a": "It prevents buying non-selling sizes (extreme sizes) and stocks up on core sizes."}
            ],
            "common_mistakes": [
                {"mistake": "Assuming same curve for all categories", "a": "Footwear curves vary by gender; kids clothing has completely different ratios."}
            ]
        },
        {
            "term_id": "EMA",
            "term_name": "Exponential Moving Average",
            "term_category": "Forecasting",
            "definition": "A moving average placing greater weight and significance on the most recent demand data points.",
            "hinglish_definition": "Sales forecasting mein recent demand trends ko zyada priority dene wala weighted moving average calculations method.",
            "term_aliases": ["EMA", "Exponential Average", "Weighted Average"],
            "manual_reference": "Volume 4 > Demand Science",
            "training_reference": "TRN-FRC-EMA",
            "related_formulas": ["INV-001"],
            "related_terms": ["Sales Velocity", "Seasonality Factor"],
            "faq": [
                {"q": "What alpha value is default?", "a": "SMRITI defaults to 0.2 to balance recent trend changes against random spikes."}
            ],
            "common_mistakes": [
                {"mistake": "Using alpha close to 1.0", "a": "High alpha value makes the system fluctuate erraticly on single large orders."}
            ]
        },
        {
            "term_id": "Seasonality Factor",
            "term_name": "Seasonality Factor",
            "term_category": "Forecasting",
            "definition": "Multiplicative multiplier adjusting forecasts based on cyclical demand changes (e.g. festivals).",
            "hinglish_definition": "Sales forecasts ko festival spikes aur seasonal changes ke hisaab se adjust karne wala demand multiplier index factor.",
            "term_aliases": ["Seasonality Factor", "Seasonality Index", "Seasonal Index"],
            "manual_reference": "Volume 4 > Demand Science",
            "training_reference": "TRN-FRC-SEASON",
            "related_formulas": [],
            "related_terms": ["EMA"],
            "faq": [
                {"q": "Where does index pull from?", "a": "From regional calendar profiles and historical 3-year category demand logs."}
            ],
            "common_mistakes": [
                {"mistake": "Applying global seasonality factor", "a": "Festivals are region-specific; South region seasonality differs from North region."}
            ]
        },
        {
            "term_id": "Lead Time",
            "term_name": "Supplier Lead Time",
            "term_category": "Distribution",
            "definition": "The chronological duration between purchase order release and store shelf GRN completion.",
            "hinglish_definition": "Purchase order release karne se lekar store/warehouse par mal physically receive hone tak ka total transit and delivery days time.",
            "term_aliases": ["Lead Time", "Supplier Lead Time", "PO to GRN Time"],
            "manual_reference": "Volume 3 > Supplier Operations",
            "training_reference": "TRN-DIST-LT",
            "related_formulas": [],
            "related_terms": ["Stockout Risk", "Transfer Benefit Score"],
            "faq": [
                {"q": "Is lead time static?", "a": "It defaults to supplier profile master days but averages dynamically over the last 5 receipts."}
            ],
            "common_mistakes": [
                {"mistake": "Ignoring transit delays", "a": "Lead time calculations must cover logistics transit buffers, not just supplier factory dispatch."}
            ]
        }
    ]

    print(f"Phase 1: Seeding {len(default_terms)} SMRITI Business Dictionary terms...")
    for t in default_terms:
        exists = frappe.db.exists("SMRITI Business Term", {"term_id": t["term_id"], "term_version": "1.0.0"})
        if not exists:
            # Create parent term without child tables first to avoid LinkValidationErrors
            doc = frappe.get_doc({
                "doctype": "SMRITI Business Term",
                "term_id": t["term_id"],
                "term_name": t["term_name"],
                "term_category": t["term_category"],
                "term_version": "1.0.0",
                "status": "Approved",
                "is_active": 1,
                "effective_date": "2026-06-19",
                "definition": t["definition"],
                "hinglish_definition": t["hinglish_definition"],
                "term_aliases": json.dumps(t["term_aliases"]),
                "manual_reference": t["manual_reference"],
                "training_reference": t["training_reference"],
                "faq": json.dumps(t["faq"]),
                "common_mistakes": json.dumps(t["common_mistakes"])
            })
            doc.insert(ignore_permissions=True)
            print(f" - [Phase 1 Seeded] Term: {t['term_id']}")
        else:
            print(f" - [Phase 1 Exists] Term: {t['term_id']}")

    frappe.db.commit()

    print("Phase 2: Updating SMRITI Business Dictionary terms relations...")
    for t in default_terms:
        doc_name = frappe.db.get_value("SMRITI Business Term", {"term_id": t["term_id"], "term_version": "1.0.0"})
        if doc_name:
            doc = frappe.get_doc("SMRITI Business Term", doc_name)
            
            # Clear existing child table rows first to make execution idempotent
            doc.set("related_formulas", [])
            doc.set("related_terms", [])

            # Append formulas
            for fid in t["related_formulas"]:
                # Safe check: only append if formula exists in system
                formula_doc_name = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": fid})
                if formula_doc_name:
                    doc.append("related_formulas", {
                        "doctype": "SMRITI Related Formula",
                        "formula_id": formula_doc_name
                    })
                else:
                    print(f"   ! [Formula Missing] Skip link for: {fid}")

            # Append related terms
            for rtid in t["related_terms"]:
                related_doc_name = frappe.db.get_value("SMRITI Business Term", {"term_id": rtid, "term_version": "1.0.0"})
                if related_doc_name:
                    doc.append("related_terms", {
                        "doctype": "SMRITI Related Term",
                        "related_term_id": related_doc_name
                    })
                else:
                    print(f"   ! [Term Missing] Skip link for: {rtid}")

            doc.save(ignore_permissions=True)
            print(f" - [Phase 2 Updated] Term Relations: {t['term_id']}")

    frappe.db.commit()
    print("SMRITI Business Dictionary terms seeding complete!")
