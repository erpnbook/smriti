# -*- coding: utf-8 -*-
#
# @file: clienteling_service.py
# @description: Core business logic service layer for SMRITI Customer Graph and Clienteling.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.2.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, getdate, today, now_datetime
from frappe import _

def mark_dirty(customer, source=None, source_document=None):
    """
    Sets dirty status on SMRITI Customer Graph, SMRITI Customer Intelligence Graph, and SMRITI Customer Profile.
    Queues background worker task to recalculate asynchronously.
    """
    if not customer:
        return
        
    for doctype in ["SMRITI Customer Graph", "SMRITI Customer Intelligence Graph", "SMRITI Customer Profile"]:
        if frappe.db.exists(doctype, customer):
            frappe.db.set_value(doctype, customer, {
                "is_dirty": 1,
                "calculation_status": "Pending",
                "dirty_source": source,
                "dirty_document": source_document
            })
            
    # Enqueue background job to calculate asynchronously
    frappe.enqueue(
        "smriti_retail_os.clienteling.service.clienteling_service.regenerate_customer_data",
        queue="default",
        timeout=300,
        customer=customer,
        source=source,
        source_document=source_document
    )

def regenerate_customer_data(customer, source=None, source_document=None):
    """
    Background queue execution to rebuild Graph, Intelligence Graph, and Profile databases.
    """
    import time
    start_time = time.time()
    
    # Create entries if they do not exist
    for doctype in ["SMRITI Customer Graph", "SMRITI Customer Intelligence Graph", "SMRITI Customer Profile"]:
        if not frappe.db.exists(doctype, customer):
            doc = frappe.new_doc(doctype)
            doc.customer = customer
            if doctype == "SMRITI Customer Graph":
                doc.graph_version = "CIG-1.1"
            elif doctype == "SMRITI Customer Intelligence Graph":
                doc.intelligence_graph_version = "v1"
            elif doctype == "SMRITI Customer Profile":
                doc.graph_version = "CIG-1.1"
            doc.calculation_status = "Pending"
            doc.flags.ignore_permissions = True
            doc.insert()
            
    # Mark as processing
    for doctype in ["SMRITI Customer Graph", "SMRITI Customer Intelligence Graph", "SMRITI Customer Profile"]:
        frappe.db.set_value(doctype, customer, "calculation_status", "Processing")
        
    try:
        # 1. Update Customer Graph
        graph_doc = update_customer_graph(customer, source, source_document, start_time)
        
        # 2. Update Customer Intelligence Graph
        intel_doc = update_customer_intelligence_graph(customer, graph_doc, source, source_document)
        
        # 3. Update Customer Profile
        update_customer_profile(customer, graph_doc, intel_doc, source, source_document)
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000.0
        err_msg = str(e)
        if frappe.db.exists("SMRITI Customer Graph", customer):
            frappe.db.set_value("SMRITI Customer Graph", customer, {
                "calculation_status": "Failed",
                "graph_status": "Failed",
                "graph_generation_error": err_msg,
                "graph_last_generated_at": now_datetime(),
                "graph_generation_duration_ms": duration_ms
            })
        for doctype in ["SMRITI Customer Intelligence Graph", "SMRITI Customer Profile"]:
            if frappe.db.exists(doctype, customer):
                frappe.db.set_value(doctype, customer, {
                    "calculation_status": "Failed",
                    "is_dirty": 0
                })
        frappe.log_error(f"SMRITI Clienteling Graph Update Failed for {customer}: {err_msg}")
        raise e

def update_customer_graph(customer, source=None, source_document=None, start_time=None):
    import time
    if not start_time:
        start_time = time.time()
        
    doc = frappe.get_doc("SMRITI Customer Graph", customer)
    
    # 1. Fetch Invoices and Returns
    invoices = frappe.db.get_all(
        "Sales Invoice",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "posting_date", "grand_total", "is_return"]
    )
    
    pos_invoices = frappe.db.get_all(
        "POS Invoice",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "posting_date", "grand_total", "is_return"]
    )
    
    all_sales = invoices + pos_invoices
    
    purchases = [s for s in all_sales if not s.is_return]
    returns = [s for s in all_sales if s.is_return]
    
    purchases_count = len(purchases)
    returns_count = len(returns)
    
    net_revenue = sum(flt(s.grand_total) for s in purchases) - sum(flt(s.grand_total) for s in returns)
    
    # Calculate Visit Frequency
    dates = sorted(list(set([getdate(s.posting_date) for s in purchases])))
    visit_frequency = 0.0
    last_visit = None
    if dates:
        last_visit = dates[-1]
        if len(dates) > 1:
            intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            visit_frequency = flt(sum(intervals) / len(intervals))
            
    # Preferred item attributes mode
    items = get_purchased_item_details(customer)
    preferred_brand = get_mode(items, "brand")
    preferred_category = get_mode(items, "item_group")
    preferred_size = get_mode(items, "size")
    preferred_color = get_mode(items, "color")
    
    # Favorite Executive from Attribution Ledger
    favorite_executive = frappe.db.get_value(
        "SMRITI Attribution Ledger",
        filters={"customer": customer, "docstatus": 1},
        fieldname="employee",
        order_by="creation desc"
    )
    
    # Attributed revenue
    attributed_revenue = flt(frappe.db.sql("""
        select sum(revenue_credit) from `tabSMRITI Attribution Ledger`
        where customer = %s and docstatus = 1
    """, customer)[0][0])
    
    # Owned customer revenue matching SMRITI Customer Ownership
    owned_customer_revenue = 0.0
    owner = frappe.db.get_value("SMRITI Customer Ownership", {"customer": customer, "is_active": 1}, "primary_owner")
    if owner:
        owned_customer_revenue = flt(frappe.db.sql("""
            select sum(revenue_credit) from `tabSMRITI Attribution Ledger`
            where customer = %s and employee = %s and docstatus = 1
        """, (customer, owner))[0][0])
        
    # Wallet balance from CGE Wallet Ledger or Benefit Ledger
    wallet_balance = 0.0
    if frappe.db.exists("DocType", "SMRITI Wallet Ledger"):
        # Sum balance_remaining of Credits
        wallet_balance = flt(frappe.db.sql("""
            select sum(balance_remaining)
            from `tabSMRITI Wallet Ledger`
            where customer = %s and transaction_type = 'Credit'
              and is_expired = 0 and (expiry_date is null or expiry_date >= %s)
        """, (customer, today()))[0][0])
    elif frappe.db.exists("DocType", "SMRITI Benefit Ledger"):
        wallet_balance = flt(frappe.db.sql("""
            select sum(case when transaction_type = 'Credit' then amount else -amount end)
            from `tabSMRITI Benefit Ledger`
            where customer = %s
        """, customer)[0][0])
        
    # Campaign Responses Count
    campaign_responses_count = 0
    if frappe.db.exists("DocType", "SMRITI Campaign Response"):
        campaign_responses_count = frappe.db.count("SMRITI Campaign Response", {"customer": customer})
    elif frappe.db.exists("DocType", "SMRITI Benefit Ledger"):
        campaign_responses_count = frappe.db.count("SMRITI Benefit Ledger", {"customer": customer, "event_type": "EARN"})
        
    # Save Graph Data
    doc.purchases_count = purchases_count
    doc.returns_count = returns_count
    doc.net_revenue = net_revenue
    doc.wallet_balance = wallet_balance
    doc.campaign_responses_count = campaign_responses_count
    doc.attributed_revenue = attributed_revenue
    doc.owned_customer_revenue = owned_customer_revenue
    doc.preferred_brand = preferred_brand
    doc.preferred_category = preferred_category
    doc.preferred_size = preferred_size
    doc.preferred_color = preferred_color
    doc.last_visit_date = last_visit
    doc.visit_frequency_days = visit_frequency
    doc.favorite_executive = favorite_executive
    doc.is_dirty = 0
    doc.dirty_source = source
    doc.dirty_document = source_document
    doc.calculation_status = "Completed"
    doc.last_calculated_on = now_datetime()
    
    # GAP-01 Observability Fields
    duration_ms = (time.time() - start_time) * 1000.0
    doc.graph_last_generated_at = now_datetime()
    doc.graph_generation_duration_ms = duration_ms
    doc.graph_source_version = "CIG-1.1"
    doc.graph_status = "Completed"
    doc.graph_generation_error = None
    
    doc.flags.ignore_permissions = True
    doc.save()
    return doc

def update_customer_profile(customer, graph_doc, intel_doc, source=None, source_document=None):
    doc = frappe.get_doc("SMRITI Customer Profile", customer)
    
    # Read derived variables from Customer Graph
    doc.preferred_brand = graph_doc.preferred_brand
    doc.preferred_category = graph_doc.preferred_category
    doc.preferred_size = graph_doc.preferred_size
    doc.preferred_color = graph_doc.preferred_color
    doc.last_visit_date = graph_doc.last_visit_date
    doc.visit_frequency_days = graph_doc.visit_frequency_days
    doc.favorite_executive = graph_doc.favorite_executive
    
    # Retrieve Formula Expressions from SMRITI Formula Registry without hardcoding calculations
    abv_expr = None
    ltv_expr = None
    if frappe.db.exists("DocType", "SMRITI Formula Definition"):
        abv_expr = frappe.db.get_value("SMRITI Formula Definition", {"formula_name": "Average Basket Value"}, "formula_expression")
        ltv_expr = frappe.db.get_value("SMRITI Formula Definition", {"formula_name": "Lifetime Value"}, "formula_expression")
        
    # Evaluate formulas safely
    context = {
        "net_revenue": flt(graph_doc.net_revenue),
        "purchases_count": int(graph_doc.purchases_count)
    }
    
    # Default fallbacks if definitions missing
    if ltv_expr:
        try:
            doc.lifetime_value = flt(eval(ltv_expr, {}, context))
        except Exception:
            doc.lifetime_value = flt(graph_doc.net_revenue)
    else:
        doc.lifetime_value = flt(graph_doc.net_revenue)
        
    if abv_expr:
        try:
            doc.average_basket_value = flt(eval(abv_expr, {}, context)) if graph_doc.purchases_count > 0 else 0.0
        except Exception:
            doc.average_basket_value = flt(graph_doc.net_revenue / graph_doc.purchases_count) if graph_doc.purchases_count > 0 else 0.0
    else:
        doc.average_basket_value = flt(graph_doc.net_revenue / graph_doc.purchases_count) if graph_doc.purchases_count > 0 else 0.0
        
    # Map derived intelligence fields from SMRITI Customer Intelligence Graph
    doc.churn_risk_score = intel_doc.churn_risk_score
    doc.churn_risk_level = intel_doc.churn_risk_level
    doc.vip_candidate_score = intel_doc.vip_candidate_score
    doc.vip_candidate_level = intel_doc.vip_candidate_level
    doc.is_vip = intel_doc.is_vip
    doc.campaign_affinity_score = intel_doc.campaign_affinity_score
    doc.customer_health_score = intel_doc.customer_health_score
    
    doc.next_visit_prediction = intel_doc.next_visit_prediction
    doc.next_visit_confidence = intel_doc.next_visit_confidence
    doc.likely_purchase_prediction = intel_doc.next_purchase_prediction
    doc.prediction_confidence = intel_doc.next_purchase_confidence
    doc.next_purchase_confidence = intel_doc.next_purchase_confidence
    
    # Engagement Score Calculation
    doc.engagement_score = calculate_engagement_score(graph_doc.purchases_count, graph_doc.net_revenue, graph_doc.returns_count)
    doc.is_dirty = 0
    doc.dirty_source = source
    doc.dirty_document = source_document
    doc.calculation_status = "Completed"
    doc.last_calculated_on = now_datetime()
    
    doc.flags.ignore_permissions = True
    doc.save()

def update_customer_intelligence_graph(customer, graph_doc, source=None, source_document=None):
    doc = frappe.get_doc("SMRITI Customer Intelligence Graph", customer)
    
    # 1. Fetch settings
    settings = frappe.get_single("SMRITI Clienteling Settings")
    vip_threshold = flt(settings.vip_threshold) if settings.vip_threshold is not None else 80.0
    dormancy_days = int(settings.dormancy_days) if settings.dormancy_days is not None else 90
    enable_predictions = settings.enable_predictions if settings.enable_predictions is not None else 1
 
    # 2. Calculate days since last visit
    last_visit_date = graph_doc.last_visit_date
    if last_visit_date:
        days_since_last_visit = (getdate(today()) - getdate(last_visit_date)).days
    else:
        days_since_last_visit = 0
    visit_frequency_days = flt(graph_doc.visit_frequency_days)
 
    # 3. Churn Risk Score
    churn_risk_score = 0.0
    churn_risk_level = "Healthy"
    churn_expr, churn_ver = get_formula_details("TST-CHURN")
    if not churn_expr:
        churn_expr = "(days_since_last_visit - visit_frequency_days) / visit_frequency_days * 100"
        churn_ver = "1.0.0"
        
    if visit_frequency_days > 0:
        context = {
            "days_since_last_visit": days_since_last_visit,
            "visit_frequency_days": visit_frequency_days
        }
        try:
            churn_risk_score = flt(eval(churn_expr, {"min": min, "max": max}, context))
        except Exception:
            churn_risk_score = flt((days_since_last_visit - visit_frequency_days) / visit_frequency_days * 100)
    else:
        churn_risk_score = 0.0
        
    churn_risk_score = max(0.0, min(100.0, churn_risk_score))
    
    if churn_risk_score < 40.0:
        churn_risk_level = "Healthy"
    elif churn_risk_score < 70.0:
        churn_risk_level = "Warning"
    else:
        churn_risk_level = "Critical"
 
    # 4. VIP Candidate Score
    net_revenue = flt(graph_doc.net_revenue)
    purchases_count = int(graph_doc.purchases_count)
    abv = flt(net_revenue / purchases_count) if purchases_count > 0 else 0.0
    
    vip_expr, vip_ver = get_formula_details("TST-VIP")
    if not vip_expr:
        vip_expr = "(net_revenue / 50000 * 50) + (abv / 5000 * 30) + min(20, purchases_count * 2.0)"
        vip_ver = "1.0.0"
        
    vip_context = {
        "net_revenue": net_revenue,
        "abv": abv,
        "purchases_count": purchases_count
    }
    
    try:
        vip_candidate_score = flt(eval(vip_expr, {"min": min, "max": max}, vip_context))
    except Exception:
        vip_candidate_score = (net_revenue / 50000.0 * 50.0) + (abv / 5000.0 * 30.0) + min(20.0, purchases_count * 2.0)
        
    vip_candidate_score = max(0.0, min(100.0, vip_candidate_score))
    
    if vip_candidate_score < 40.0:
        vip_candidate_level = "Low"
    elif vip_candidate_score < 80.0:
        vip_candidate_level = "Medium"
    else:
        vip_candidate_level = "High"
        
    is_vip = 1 if vip_candidate_score >= vip_threshold else 0
 
    # 5. Campaign Affinity Score
    campaign_responses = 0
    if frappe.db.exists("DocType", "SMRITI Campaign Response"):
        campaign_responses += frappe.db.count("SMRITI Campaign Response", {"customer": customer})
    if frappe.db.exists("DocType", "SMRITI Benefit Ledger"):
        campaign_responses += frappe.db.count("SMRITI Benefit Ledger", {"customer": customer, "event_type": "EARN"})
        
    affinity_expr, affinity_ver = get_formula_details("TST-AFFINITY")
    if not affinity_expr:
        affinity_expr = "campaign_responses * 20.0"
        affinity_ver = "1.0.0"
        
    affinity_context = {
        "campaign_responses": campaign_responses
    }
    
    try:
        campaign_affinity_score = flt(eval(affinity_expr, {"min": min, "max": max}, affinity_context))
    except Exception:
        campaign_affinity_score = campaign_responses * 20.0
        
    campaign_affinity_score = max(0.0, min(100.0, campaign_affinity_score))
 
    # 5.5. Composite Customer Health Score
    health_expr, health_ver = get_formula_details("TST-HEALTH")
    if not health_expr:
        health_expr = "(100 - churn_risk_score) * 0.4 + vip_candidate_score * 0.4 + campaign_affinity_score * 0.2"
        health_ver = "1.0.0"
        
    health_context = {
        "churn_risk_score": churn_risk_score,
        "vip_candidate_score": vip_candidate_score,
        "campaign_affinity_score": campaign_affinity_score
    }
    try:
        customer_health_score = flt(eval(health_expr, {"min": min, "max": max}, health_context))
    except Exception:
        customer_health_score = (100.0 - churn_risk_score) * 0.4 + vip_candidate_score * 0.4 + campaign_affinity_score * 0.2
        
    customer_health_score = max(0.0, min(100.0, customer_health_score))
 
    # 6. Dormancy
    is_dormant = 0
    if last_visit_date:
        is_dormant = 1 if days_since_last_visit >= dormancy_days else 0
 
    # 7. Predictions
    next_visit_prediction = None
    next_visit_confidence = 0.0
    next_purchase_prediction = None
    next_purchase_confidence = 0.0
    
    if enable_predictions:
        pdt_pred = get_pdt_predictions(customer)
        next_purchase_prediction = pdt_pred.get("likely_purchase")
        next_purchase_confidence = flt(pdt_pred.get("confidence", 0.0))
        next_visit_prediction = pdt_pred.get("predicted_next_visit")
        next_visit_confidence = flt(pdt_pred.get("next_visit_confidence", pdt_pred.get("confidence", 0.0)))
        
    # Confidence clamping
    next_visit_confidence = max(0.0, min(100.0, next_visit_confidence))
    next_purchase_confidence = max(0.0, min(100.0, next_purchase_confidence))
 
    # 8. Save Doc Fields
    doc.churn_risk_score = churn_risk_score
    doc.churn_risk_level = churn_risk_level
    doc.churn_formula_id = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": "TST-CHURN"}, "name")
    doc.churn_formula_version = churn_ver
    
    doc.vip_candidate_score = vip_candidate_score
    doc.vip_candidate_level = vip_candidate_level
    doc.is_vip = is_vip
    doc.vip_formula_id = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": "TST-VIP"}, "name")
    doc.vip_formula_version = vip_ver
    
    doc.is_dormant = is_dormant
    doc.next_visit_prediction = next_visit_prediction
    doc.next_visit_confidence = next_visit_confidence
    doc.next_purchase_prediction = next_purchase_prediction
    doc.next_purchase_confidence = next_purchase_confidence
    
    doc.campaign_affinity_score = campaign_affinity_score
    doc.affinity_formula_id = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": "TST-AFFINITY"}, "name")
    doc.affinity_formula_version = affinity_ver
    
    # GAP-03, GAP-05 Customer Health & Governance versions
    doc.customer_health_score = customer_health_score
    doc.graph_version = "CIG-1.1"
    doc.scoring_model_version = "SCORING-1.0"
    doc.prediction_model_version = "PDT-1.0"
    
    doc.is_dirty = 0
    doc.dirty_source = source
    doc.dirty_document = source_document
    doc.intelligence_graph_version = "v1"
    doc.calculation_status = "Completed"
    doc.last_calculated_on = now_datetime()
    
    doc.flags.ignore_permissions = True
    doc.save()
    
    return doc

def get_formula_details(formula_id):
    """
    Returns (expression, version) for active formula.
    """
    formula = frappe.db.get_value(
        "SMRITI Formula Definition",
        {"formula_id": formula_id, "is_active": 1},
        ["formula_expression", "formula_version"],
        as_dict=True
    )
    if formula:
        return formula.formula_expression, formula.formula_version
    return None, None

def get_purchased_item_details(customer):
    items_raw = frappe.db.sql("""
        SELECT sii.item_code, i.brand, i.item_group
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        JOIN `tabItem` i ON sii.item_code = i.name
        WHERE si.customer = %s AND si.docstatus = 1 AND si.is_return = 0
        UNION ALL
        SELECT pii.item_code, i.brand, i.item_group
        FROM `tabPOS Invoice Item` pii
        JOIN `tabPOS Invoice` pi ON pii.parent = pi.name
        JOIN `tabItem` i ON pii.item_code = i.name
        WHERE pi.customer = %s AND pi.docstatus = 1 AND pi.is_return = 0
    """, (customer, customer), as_dict=True)

    results = []
    for item in items_raw:
        item_code = item["item_code"]
        size = frappe.db.get_value("Item Variant Attribute", {"parent": item_code, "attribute": ["like", "%size%"]}, "attribute_value")
        color = frappe.db.get_value("Item Variant Attribute", {"parent": item_code, "attribute": ["like", "%color%"]}, "attribute_value")
        results.append({
            "brand": item["brand"],
            "item_group": item["item_group"],
            "size": size,
            "color": color
        })
    return results

def get_mode(items, field):
    values = [i.get(field) for i in items if i.get(field)]
    if not values:
        return None
    return max(set(values), key=values.count)

def get_pdt_predictions(customer):
    try:
        from smriti_retail_os.pdt.service import prediction_service
        return prediction_service.get_customer_prediction(customer)
    except ImportError:
        return {"likely_purchase": None, "confidence": 0.0, "predicted_next_visit": None}

def calculate_engagement_score(purchases, net_revenue, returns):
    score = 0.0
    if purchases > 0:
        score += min(purchases * 10, 50)
    if net_revenue > 0:
        score += min((net_revenue / 5000) * 10, 40)
    return_ratio = returns / purchases if purchases > 0 else 0
    score -= min(return_ratio * 30, 20)
    return max(0.0, min(100.0, score))


def on_invoice_submit(doc, method=None):
    if doc.customer:
        mark_dirty(doc.customer, source="Sales Invoice", source_document=doc.name)


def on_invoice_cancel(doc, method=None):
    if doc.customer:
        mark_dirty(doc.customer, source="Sales Invoice", source_document=doc.name)


def on_pos_invoice_submit(doc, method=None):
    if doc.customer:
        mark_dirty(doc.customer, source="POS Invoice", source_document=doc.name)


def on_pos_invoice_cancel(doc, method=None):
    if doc.customer:
        mark_dirty(doc.customer, source="POS Invoice", source_document=doc.name)

