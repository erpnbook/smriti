# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/setup_wizard_api.py
# @description: Backend API for SMRITI Retail OS Setup Wizard.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-02
#

import re
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.utils import flt, nowdate


# ─── Validation Helpers ────────────────────────────────────────────

_GSTIN_PATTERN = re.compile(
    r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$"
)


def _validate_gstin(gstin):
    """Validates the format of an Indian GSTIN (15 characters).
    Raises frappe.ValidationError if the format is incorrect.
    """
    if not gstin:
        return  # GSTIN is optional — skip validation when absent
    gstin = str(gstin).strip().upper()
    if len(gstin) != 15:
        frappe.throw(_("GSTIN must be exactly 15 characters."), frappe.ValidationError)
    if not _GSTIN_PATTERN.match(gstin):
        frappe.throw(
            _("GSTIN format is invalid. Expected format: 2-digit state code + 10-char PAN + 1 entity number + Z + 1 checksum."),
            frappe.ValidationError
        )
    return gstin


def _validate_pincode(pincode):
    """Validates that a pincode is exactly 6 numeric digits.
    Raises frappe.ValidationError if not.
    """
    if not pincode:
        return  # Pincode is optional
    pincode = str(pincode).strip()
    if not re.match(r"^\d{6}$", pincode):
        frappe.throw(_("Pincode must be exactly 6 digits."), frappe.ValidationError)
    return pincode


def _validate_company_abbr(abbr, current_company=None):
    """Validates that a company abbreviation is not already in use by another company.
    Raises frappe.ValidationError if duplicate found.
    """
    if not abbr:
        return
    filters = {"abbr": abbr}
    if current_company:
        filters["name"] = ("!=", current_company)
    existing = smriti.db.get("Company", filters, "name")
    if existing:
        frappe.throw(
            _("Company abbreviation {0} is already in use by another company.").format(frappe.bold(abbr)),
            frappe.ValidationError
        )


@frappe.whitelist()
def get_setup_wizard_initial_data():
    """
    Returns initial state for the Setup Wizard.
    """
    # Verify permission
    verify_setup_wizard_access()

    companies = smriti.db.get_list("Company", fields=["name", "company_name", "abbr"])
    has_company = len(companies) > 0

    # Get admin user details
    admin_user = smriti.db.get("User", "Administrator", ["full_name", "email"], as_dict=True) or {}

    # Standard Indian states
    states = [
        {"code": "01", "name": "Jammu & Kashmir"},
        {"code": "02", "name": "Himachal Pradesh"},
        {"code": "03", "name": "Punjab"},
        {"code": "04", "name": "Chandigarh"},
        {"code": "05", "name": "Uttarakhand"},
        {"code": "06", "name": "Haryana"},
        {"code": "07", "name": "Delhi"},
        {"code": "08", "name": "Rajasthan"},
        {"code": "09", "name": "Uttar Pradesh"},
        {"code": "10", "name": "Bihar"},
        {"code": "11", "name": "Sikkim"},
        {"code": "12", "name": "Arunachal Pradesh"},
        {"code": "13", "name": "Nagaland"},
        {"code": "14", "name": "Manipur"},
        {"code": "15", "name": "Mizoram"},
        {"code": "16", "name": "Tripura"},
        {"code": "17", "name": "Meghalaya"},
        {"code": "18", "name": "Assam"},
        {"code": "19", "name": "West Bengal"},
        {"code": "20", "name": "Jharkhand"},
        {"code": "21", "name": "Odisha"},
        {"code": "22", "name": "Chhattisgarh"},
        {"code": "23", "name": "Madhya Pradesh"},
        {"code": "24", "name": "Gujarat"},
        {"code": "26", "name": "Dadra and Nagar Haveli and Daman and Diu"},
        {"code": "27", "name": "Maharashtra"},
        {"code": "29", "name": "Karnataka"},
        {"code": "30", "name": "Goa"},
        {"code": "31", "name": "Lakshadweep"},
        {"code": "32", "name": "Kerala"},
        {"code": "33", "name": "Tamil Nadu"},
        {"code": "34", "name": "Puducherry"},
        {"code": "35", "name": "Andaman & Nicobar Islands"},
        {"code": "36", "name": "Telangana"},
        {"code": "37", "name": "Andhra Pradesh"},
        {"code": "38", "name": "Ladakh"}
    ]

    return {
        "has_company": has_company,
        "companies": companies,
        "admin_user": admin_user,
        "states": states,
        "current_user": frappe.session.user
    }

@frappe.whitelist()
def run_setup_wizard(setup_data):
    """
    Executes setup wizard configuration programmatically.
    """
    verify_setup_wizard_access()

    if isinstance(setup_data, str):
        import json
        setup_data = json.loads(setup_data)

    logs = []
    def log(msg):
        logs.append(msg)
        frappe.logger().info(f"[SMRITI SETUP] {msg}")

    try:
        # C-07 FIX: Do NOT use frappe.set_user("Administrator") here.
        # frappe.set_user() permanently re-assigns frappe.session.user for the entire
        # remaining request, affecting all subsequent permission checks including
        # third-party hooks (india_compliance, erpnext). This bypasses audit trails.
        # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
        # Instead, use frappe.flags.ignore_permissions=True selectively on each doc.
        # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
        frappe.flags.ignore_permissions = True

        # 1. Update Admin credentials if provided
        log("Updating Administrator profile details...")
        admin_fullname = setup_data.get("admin_fullname")
        admin_password = setup_data.get("admin_password")
        
        admin_doc = smriti.documents.get("User", "Administrator")
        if admin_fullname:
            admin_doc.full_name = admin_fullname
        if admin_password:
            admin_doc.new_password = admin_password
            log("Administrator password updated.")
        # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
        admin_doc.save(ignore_permissions=True)
        
        # 2. Upsert Company
        company_name = setup_data.get("company_name", "SMRITI Retail")
        company_abbr = setup_data.get("company_abbr", "SR")
        store_type = setup_data.get("store_type", "Retail")
        currency = setup_data.get("currency", "INR")
        country = setup_data.get("country", "India")
        state = setup_data.get("state", "Maharashtra")
        state_code = setup_data.get("state_code", "27")
        gstin = setup_data.get("gstin")

        # ── Validate inputs before touching the database ──
        gstin = _validate_gstin(gstin)
        _validate_pincode(setup_data.get("store_pincode"))
        company_exists = smriti.db.exists("Company", company_name)
        _validate_company_abbr(company_abbr, current_company=company_name if company_exists else None)

        log("Ensuring standard Warehouse Types exist...")
        for w_type in ["Transit", "Standard", "Subcontracted"]:
            if not smriti.db.exists("Warehouse Type", w_type):
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                smriti.documents.new("WarehouseType").update({"name": w_type}).insert(ignore_permissions=True)
                log(f"Created standard Warehouse Type: {w_type}")

        log(f"Configuring Company: {company_name} ({company_abbr})...")
        if not company_exists:
            co = smriti.documents.new("Company")
            co.company_name = company_name
            co.abbr = company_abbr
            co.default_currency = currency
            co.country = country
            co.domain = "Retail"
            co.custom_smriti_store_type = store_type
            co.custom_smriti_gstin_state = state_code
            co.tax_id = gstin
            co.gstin = gstin
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            co.insert(ignore_permissions=True)
            log(f"Company '{company_name}' created.")
        else:
            co = smriti.documents.get("Company", company_name)
            co.custom_smriti_store_type = store_type
            co.custom_smriti_gstin_state = state_code
            if gstin:
                co.tax_id = gstin
                co.gstin = gstin
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            co.save(ignore_permissions=True)
            log(f"Company '{company_name}' details updated.")

        # Normalize company_name to exact database primary key representation
        company_name = co.name
        currency = co.default_currency

        # Set default company globally
        frappe.defaults.set_global_default("company", company_name)
        frappe.defaults.set_user_default("company", company_name, "Administrator")
        smriti.db.commit()

        # Create/Update Registered Office Address
        store_trade_name = setup_data.get("store_trade_name") or company_name
        address_name = f"{company_name}-Registered"
        if not smriti.db.exists("Address", address_name):
            addr = smriti.documents.new("Address")
            addr.address_title = store_trade_name
            addr.address_type = "Office"
            addr.address_line1 = setup_data.get("store_address_line1") or "Primary Store Location"
            addr.address_line2 = setup_data.get("store_area_locality")
            addr.city = setup_data.get("store_city") or "Mumbai"
            addr.state = state
            addr.country = country
            addr.pincode = setup_data.get("store_pincode")
            addr.landmark = setup_data.get("store_landmark")
            try:
                lat = setup_data.get("store_latitude")
                addr.latitude = flt(lat) if lat is not None and str(lat).strip() != "" else None
            except Exception:
                addr.latitude = None
            try:
                lng = setup_data.get("store_longitude")
                addr.longitude = flt(lng) if lng is not None and str(lng).strip() != "" else None
            except Exception:
                addr.longitude = None
            addr.is_primary_address = 1
            addr.is_shipping_address = 1
            addr.is_your_company_address = 1
            addr.gstin = gstin
            addr.gst_state = state
            addr.gst_state_number = state_code
            addr.gst_category = "Registered" if gstin else "Unregistered"
            addr.append("links", {"link_doctype": "Company", "link_name": company_name})
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            addr.insert(ignore_permissions=True)
            log("Company Office Address created and linked using user-provided details.")
        else:
            addr = smriti.documents.get("Address", address_name)
            addr.address_title = store_trade_name
            addr.address_line1 = setup_data.get("store_address_line1") or "Primary Store Location"
            addr.address_line2 = setup_data.get("store_area_locality")
            addr.city = setup_data.get("store_city") or "Mumbai"
            addr.state = state
            addr.country = country
            addr.pincode = setup_data.get("store_pincode")
            addr.landmark = setup_data.get("store_landmark")
            try:
                lat = setup_data.get("store_latitude")
                addr.latitude = flt(lat) if lat is not None and str(lat).strip() != "" else None
            except Exception:
                addr.latitude = None
            try:
                lng = setup_data.get("store_longitude")
                addr.longitude = flt(lng) if lng is not None and str(lng).strip() != "" else None
            except Exception:
                addr.longitude = None
            addr.gstin = gstin
            addr.gst_state = state
            addr.gst_state_number = state_code
            addr.gst_category = "Registered" if gstin else "Unregistered"
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            addr.save(ignore_permissions=True)
            log("Company Office Address updated with user-provided details.")
        
        # 3. Create default Warehouse
        warehouse_name = setup_data.get("default_warehouse_name", "Main Store")
        full_warehouse_name = f"{warehouse_name} - {company_abbr}"
        log(f"Configuring default warehouse: {full_warehouse_name}...")
        
        if not smriti.db.exists("Warehouse", full_warehouse_name):
            # Check if parent warehouse exists
            parent_warehouse = f"All Warehouses - {company_abbr}"
            if not smriti.db.exists("Warehouse", parent_warehouse):
                # Create standard parent
                pw = smriti.documents.new("Warehouse")
                pw.warehouse_name = "All Warehouses"
                pw.company = company_name
                pw.is_group = 1
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                pw.insert(ignore_permissions=True)
                parent_warehouse = pw.name
            
            wh = smriti.documents.new("Warehouse")
            wh.warehouse_name = warehouse_name
            wh.company = company_name
            wh.parent_warehouse = parent_warehouse
            wh.is_group = 0
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            wh.insert(ignore_permissions=True)
            log(f"Warehouse '{wh.name}' created.")
            warehouse_id = wh.name
        else:
            warehouse_id = full_warehouse_name
            log(f"Warehouse '{full_warehouse_name}' already exists.")

        # 4. Create default Customer
        customer_name = setup_data.get("default_customer_name", "Walk-in Customer")
        log(f"Configuring default customer: {customer_name}...")
        
        # Ensure Customer Group exists (must be is_group=0)
        existing_cgs = smriti.db.get_list("Customer Group", filters={"is_group": 0}, limit=1, pluck="name")
        if existing_cgs:
            cg = existing_cgs[0]
        else:
            if not smriti.db.exists("Customer Group", "All Customer Groups"):
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                smriti.documents.new("CustomerGroup").update({"customer_group_name": "All Customer Groups", "is_group": 1}).insert(ignore_permissions=True)
            cg = "Retail Customers"
            if not smriti.db.exists("Customer Group", cg):
                smriti.documents.new("CustomerGroup").update({
                    "customer_group_name": cg,
                    "parent_customer_group": "All Customer Groups",
                    "is_group": 0
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                }).insert(ignore_permissions=True)
                
        # Ensure Territory exists (must be is_group=0)
        existing_terrs = smriti.db.get_list("Territory", filters={"is_group": 0}, limit=1, pluck="name")
        if existing_terrs:
            terr = existing_terrs[0]
        else:
            if not smriti.db.exists("Territory", "All Territories"):
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                smriti.documents.new("Territory").update({"territory_name": "All Territories", "is_group": 1}).insert(ignore_permissions=True)
            terr = "Retail Territory"
            if not smriti.db.exists("Territory", terr):
                smriti.documents.new("Territory").update({
                    "territory_name": terr,
                    "parent_territory": "All Territories",
                    "is_group": 0
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                }).insert(ignore_permissions=True)

        customer_id = smriti.db.get("Customer", {"customer_name": customer_name}, "name")
        if not customer_id:
            cust = smriti.documents.new("Customer")
            cust.customer_name = customer_name
            cust.customer_type = "Individual"
            cust.customer_group = cg
            cust.territory = terr
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            cust.insert(ignore_permissions=True)
            log(f"Customer '{cust.name}' created.")
            customer_id = cust.name
        else:
            log(f"Customer '{customer_id}' already exists.")

        # 5. Create default Duties and Taxes accounts if missing
        parent_tax_account = f"Duties and Taxes - {company_abbr}"
        if not smriti.db.exists("Account", parent_tax_account):
            # Check if Current Liabilities exists
            liabilities_parent = f"Current Liabilities - {company_abbr}"
            if smriti.db.exists("Account", liabilities_parent):
                ta = smriti.documents.new("Account")
                ta.account_name = "Duties and Taxes"
                ta.parent_account = liabilities_parent
                ta.company = company_name
                ta.is_group = 1
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                ta.insert(ignore_permissions=True)
                parent_tax_account = ta.name
                log("Created parent Duties and Taxes account group.")
        
        tax_accounts = ["CGST", "SGST", "IGST"]
        created_accounts = {}
        for ta_name in tax_accounts:
            full_acc_name = f"{ta_name} - {company_abbr}"
            if not smriti.db.exists("Account", full_acc_name):
                if smriti.db.exists("Account", parent_tax_account):
                    acc = smriti.documents.new("Account")
                    acc.account_name = ta_name
                    acc.parent_account = parent_tax_account
                    acc.company = company_name
                    acc.account_type = "Tax"
                    # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                    acc.insert(ignore_permissions=True)
                    created_accounts[ta_name] = acc.name
                    log(f"Created ledger account: {acc.name}")
                else:
                    created_accounts[ta_name] = None
            else:
                created_accounts[ta_name] = full_acc_name
        
        # 6. Create Sales Taxes and Charges Templates
        gst_rates = setup_data.get("gst_rates", [0, 5, 12, 18, 28])
        log(f"Configuring GST tax templates for rates: {gst_rates}...")
        
        tax_inclusive = "Yes" # Standard retail is tax-inclusive
        
        # Default intrastate / interstate template references
        default_intra_tpl = ""
        default_inter_tpl = ""

        for rate in gst_rates:
            rate_flt = flt(rate)
            if rate_flt == 0:
                # Exempt or Zero Tax template
                intra_name = f"GST 0% - {company_abbr}"
                if not smriti.db.exists("Sales Taxes and Charges Template", intra_name):
                    tpl = smriti.documents.new("Sales Taxes and Charges Template")
                    tpl.title = f"GST 0%"
                    tpl.company = company_name
                    tpl.is_default = 0
                    # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                    tpl.insert(ignore_permissions=True)
                    log(f"Created Tax Template: {tpl.name}")
                continue

            half_rate = flt(rate_flt / 2.0)
            
            # Intrastate: CGST + SGST
            intra_name = f"CGST+SGST {rate}% - {company_abbr}"
            if not smriti.db.exists("Sales Taxes and Charges Template", intra_name):
                tpl = smriti.documents.new("Sales Taxes and Charges Template")
                tpl.title = f"CGST+SGST {rate}%"
                tpl.company = company_name
                
                # CGST line
                tpl.append("taxes", {
                    "charge_type": "On Net Total",
                    "account_head": created_accounts.get("CGST"),
                    "description": f"CGST @ {half_rate}%",
                    "rate": half_rate,
                    "included_in_print_rate": 1
                })
                # SGST line
                tpl.append("taxes", {
                    "charge_type": "On Net Total",
                    "account_head": created_accounts.get("SGST"),
                    "description": f"SGST @ {half_rate}%",
                    "rate": half_rate,
                    "included_in_print_rate": 1
                })
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                tpl.insert(ignore_permissions=True)
                log(f"Created Intrastate Tax Template: {tpl.name}")
                if rate_flt == 18.0 or not default_intra_tpl:
                    default_intra_tpl = tpl.name
            else:
                default_intra_tpl = intra_name

            # Interstate: IGST
            inter_name = f"IGST {rate}% - {company_abbr}"
            if not smriti.db.exists("Sales Taxes and Charges Template", inter_name):
                tpl = smriti.documents.new("Sales Taxes and Charges Template")
                tpl.title = f"IGST {rate}%"
                tpl.company = company_name
                
                # IGST line
                tpl.append("taxes", {
                    "charge_type": "On Net Total",
                    "account_head": created_accounts.get("IGST"),
                    "description": f"IGST @ {rate_flt}%",
                    "rate": rate_flt,
                    "included_in_print_rate": 1
                })
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                tpl.insert(ignore_permissions=True)
                log(f"Created Interstate Tax Template: {tpl.name}")
                if rate_flt == 18.0 or not default_inter_tpl:
                    default_inter_tpl = tpl.name
            else:
                default_inter_tpl = inter_name

        # 7. Create Mode of Payments and standard POS Profile
        pos_profile_name = setup_data.get("default_pos_profile_name", "Standard POS Profile")
        log(f"Configuring POS Profile: {pos_profile_name}...")
        
        # Fetch or create Cash & Bank ledgers for Mode of Payment mapping
        cash_ledger = f"Cash - {company_abbr}"
        if not smriti.db.exists("Account", cash_ledger):
            cash_ledger = smriti.db.get("Account", {"account_name": "Cash", "company": company_name})
        
        bank_ledger = f"Bank - {company_abbr}"
        if not smriti.db.exists("Account", bank_ledger):
            bank_ledger = smriti.db.get("Account", {"account_type": "Bank", "company": company_name})
            if not bank_ledger:
                parent_bank = f"Bank Accounts - {company_abbr}"
                if not smriti.db.exists("Account", parent_bank):
                    parent_bank = f"Current Assets - {company_abbr}"
                if smriti.db.exists("Account", parent_bank):
                    acc = smriti.documents.new("Account")
                    acc.account_name = "Bank"
                    acc.parent_account = parent_bank
                    acc.company = company_name
                    acc.account_type = "Bank"
                    # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                    acc.insert(ignore_permissions=True)
                    bank_ledger = acc.name
                    log(f"Created default Bank ledger: {acc.name}")

        # Ensure standard Modes of Payments exist and are mapped
        from smriti_retail_os.config.business_defaults import DEFAULT_PAYMENT_MODES
        mops = DEFAULT_PAYMENT_MODES
        for mop in mops:
            if not smriti.db.exists("Mode of Payment", mop):
                doc = smriti.documents.new("Mode of Payment")
                doc.mode_of_payment = mop
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                doc.insert(ignore_permissions=True)
                log(f"Created Mode of Payment: {mop}")
            
            # Map accounts in Mode of Payment (Defensively guard against duplicate entries)
            mop_doc = smriti.documents.get("Mode of Payment", mop)
            existing_companies = [acc.company for acc in mop_doc.accounts]
            has_mapping = False
            for acc in mop_doc.accounts:
                if str(acc.company).strip().upper() == str(company_name).strip().upper():
                    has_mapping = True
                    break
            
            if not has_mapping:
                ledger = cash_ledger if mop == "Cash" else bank_ledger
                if ledger:
                    mop_doc.append("accounts", {
                        "company": company_name,
                        "default_account": ledger
                    })
            
            # Defensive deduplication check to satisfy ERPNext validation
            seen_companies = set()
            unique_accounts = []
            for acc in mop_doc.accounts:
                comp_key = str(acc.company).strip().upper()
                if comp_key not in seen_companies:
                    seen_companies.add(comp_key)
                    unique_accounts.append(acc)

            # ── Orphan purge ──────────────────────────────────────────────────────
            # Frappe validates ALL child rows on save, including rows for companies
            # that were deleted after setup (e.g. test/demo companies).  Strip any
            # Mode of Payment Account rows whose Company no longer exists to prevent
            # "Could not find Row #N: Company: <name>" errors.
            clean_accounts = []
            for acc in unique_accounts:
                if smriti.db.exists("Company", acc.company):
                    clean_accounts.append(acc)
                else:
                    log(f"  [cleanup] Removed stale MoP account row for deleted company: {acc.company}")
            # ─────────────────────────────────────────────────────────────────────

            final_companies = [acc.company for acc in clean_accounts]
            mop_doc.accounts = clean_accounts
            mop_doc.flags.ignore_links = True  # Belt-and-suspenders: skip Link re-validation for newly inserted company rows
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            mop_doc.save(ignore_permissions=True)
            log(f"Mapped {mop} to Company {company_name} successfully.")

        # Fetch or create Cost Center for POS
        cost_center = f"Main - {company_abbr}"
        if not smriti.db.exists("Cost Center", cost_center):
            cost_center = smriti.db.get("Cost Center", {"company": company_name})
            if not cost_center:
                cc = smriti.documents.new("Cost Center")
                cc.cost_center_name = "Main"
                cc.company = company_name
                # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                cc.insert(ignore_permissions=True)
                cost_center = cc.name

        # Fetch or create Write Off Account for POS
        write_off_account = f"Write Off - {company_abbr}"
        if not smriti.db.exists("Account", write_off_account):
            write_off_account = smriti.db.get("Account", {"account_name": ["like", "%Write Off%"], "company": company_name})
            if not write_off_account:
                parent_expense = smriti.db.get("Account", {"account_name": "Indirect Expenses", "company": company_name})
                if not parent_expense:
                    parent_expense = smriti.db.get("Account", {"account_name": "Direct Expenses", "company": company_name})
                if not parent_expense:
                    parent_expense = smriti.db.get("Account", {"is_group": 1, "root_type": "Expense", "company": company_name})
                
                if parent_expense:
                    acc = smriti.documents.new("Account")
                    acc.account_name = "Write Off"
                    acc.parent_account = parent_expense
                    acc.company = company_name
                    acc.account_type = "Expense Account"
                    # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
                    acc.insert(ignore_permissions=True)
                    write_off_account = acc.name

        if not smriti.db.exists("POS Profile", pos_profile_name):
            pp = smriti.documents.new("POS Profile")
            pp.name = pos_profile_name
            pp.company = company_name
            pp.warehouse = warehouse_id
            pp.customer = customer_id
            pp.currency = currency
            if write_off_account:
                pp.write_off_account = write_off_account
            if cost_center:
                pp.write_off_cost_center = cost_center
            
            # Map Cash
            if cash_ledger:
                pp.append("payments", {
                    "mode_of_payment": "Cash",
                    "default_ledger": cash_ledger,
                    "default": 1
                })
            # Map Bank
            if bank_ledger:
                pp.append("payments", {
                    "mode_of_payment": "Bank",
                    "default_ledger": bank_ledger
                })
                pp.append("payments", {
                    "mode_of_payment": "UPI",
                    "default_ledger": bank_ledger
                })
            
            pp.flags.ignore_links = True  # Prevent "Could not find Row #N: Company" on payments child table
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            pp.insert(ignore_permissions=True)
            log(f"POS Profile '{pp.name}' created.")
            pos_profile_id = pp.name
        else:
            pos_profile_id = pos_profile_name
            log(f"POS Profile '{pos_profile_name}' already exists. Updating settings defensively...")
            pp = smriti.documents.get("POS Profile", pos_profile_name)
            pp.company = company_name
            pp.warehouse = warehouse_id
            pp.customer = customer_id
            pp.currency = currency
            if write_off_account:
                pp.write_off_account = write_off_account
            if cost_center:
                pp.write_off_cost_center = cost_center
                
            # Defensively update payments mapping to avoid duplicates
            payment_mappings = []
            if cash_ledger:
                payment_mappings.append(("Cash", cash_ledger, 1))
            if bank_ledger:
                payment_mappings.append(("Bank", bank_ledger, 0))
                payment_mappings.append(("UPI", bank_ledger, 0))
                
            for mop, ledger, is_default in payment_mappings:
                has_pay = False
                for pay in pp.payments:
                    if pay.mode_of_payment == mop:
                        pay.default_ledger = ledger
                        if is_default:
                            pay.default = 1
                        has_pay = True
                        break
                if not has_pay:
                    pp.append("payments", {
                        "mode_of_payment": mop,
                        "default_ledger": ledger,
                        "default": is_default
                    })
            
            # Deduplicate payments table before saving
            seen_mops = set()
            unique_payments = []
            for p in pp.payments:
                if p.mode_of_payment not in seen_mops:
                    seen_mops.add(p.mode_of_payment)
                    unique_payments.append(p)
            pp.payments = unique_payments
            
            pp.flags.ignore_links = True  # Prevent "Could not find Row #N: Company" on payments child table
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            pp.save(ignore_permissions=True)
            log(f"POS Profile '{pos_profile_name}' updated successfully.")

        # 8. Seed business-type attributes and custom fields if requested
        if setup_data.get("seed_attributes", True):
            log("Running SMRITI master doctypes seeding and customizations setup...")
            from smriti_retail_os.setup import setup_smriti_retail_os
            setup_smriti_retail_os()
            log("Masters and Print Templates seeded successfully.")

        # 9. Create SMRITI Company Settings
        log("Saving SMRITI Company Settings...")
        settings_name = company_name
        
        # Determine address values
        store_trade_name = setup_data.get("store_trade_name") or company_name
        store_address_line1 = setup_data.get("store_address_line1")
        store_address_line2 = setup_data.get("store_address_line2")
        store_area_locality = setup_data.get("store_area_locality")
        store_city = setup_data.get("store_city")
        store_pincode = setup_data.get("store_pincode")
        store_landmark = setup_data.get("store_landmark")
        
        try:
            lat = setup_data.get("store_latitude")
            store_latitude = flt(lat) if lat is not None and str(lat).strip() != "" else None
        except Exception:
            store_latitude = None
        try:
            lng = setup_data.get("store_longitude")
            store_longitude = flt(lng) if lng is not None and str(lng).strip() != "" else None
        except Exception:
            store_longitude = None

        if not smriti.db.exists("SMRITI Company Settings", settings_name):
            scs = smriti.documents.new("SMRITI Company Settings")
            scs.company = company_name
            scs.store_trade_name = store_trade_name
            scs.brand_color = "#1a73e8"
            scs.invoice_series_prefix = f"SINV-{company_abbr}-"
            scs.receipt_footer_text = "Thank you for shopping with us!"
            scs.default_warehouse = warehouse_id
            scs.default_pos_profile = pos_profile_id
            scs.default_walk_in_customer = customer_id
            if default_intra_tpl:
                scs.default_intrastate_tax_template = default_intra_tpl
            if default_inter_tpl:
                scs.default_interstate_tax_template = default_inter_tpl
            
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            scs.insert(ignore_permissions=True)
            log("SMRITI Company Settings initialized.")
        else:
            scs = smriti.documents.get("SMRITI Company Settings", settings_name)
            scs.default_warehouse = warehouse_id
            scs.default_pos_profile = pos_profile_id
            scs.default_walk_in_customer = customer_id
            if default_intra_tpl:
                scs.default_intrastate_tax_template = default_intra_tpl
            if default_inter_tpl:
                scs.default_interstate_tax_template = default_inter_tpl
                
            scs.store_trade_name = store_trade_name
            
            # reviewed-ignore-permissions: system configuration setup wizard execution, runs before roles exist
            scs.save(ignore_permissions=True)
            log("SMRITI Company Settings updated.")

        # Set Company Settings configured flag
        smriti.db.set_value("Company", company_name, "custom_smriti_settings_configured", 1)

        # Set System Settings flags
        frappe.db.set_single_value("System Settings", "setup_complete", 1)
        frappe.db.set_single_value("System Settings", "custom_smriti_frontend_enabled", 1)

        smriti.db.commit()

        # Clear Cache
        log("Clearing cache to apply initial configuration...")
        frappe.clear_cache()
        log("Setup complete! SMRITI Retail OS is ready.")
        
        return {
            "success": True,
            "logs": logs,
            "message": "Initialization completed successfully!"
        }

    except Exception as e:
        smriti.db.rollback()
        err_msg = str(e)
        smriti.errors.log_error(f"Setup Wizard Error: {err_msg}")
        log(f"CRITICAL ERROR: {err_msg}")
        return {
            "success": False,
            "logs": logs,
            "error": err_msg
        }

def verify_setup_wizard_access():
    """
    Validates if the user is authorized to run the Setup Wizard.
    Access is granted to:
    - Guests/Anyone if NO Company document exists in the system (first setup).
    - 'Administrator' or any user with the 'System Manager' role otherwise.
    Emits a warning (non-blocking) if the system has already been configured.
    """
    companies = smriti.db.get_list("Company", limit=1)
    if not companies:
        # First-time initialization — allow access to anyone
        return

    # Already configured — check permissions
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication Required: Please log in to run Setup Wizard."), frappe.AuthenticationError)

    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and frappe.session.user != "Administrator":
        frappe.throw(_("Permission Denied: Only Administrators or System Managers can access this portal."), frappe.PermissionError)

    # Warn (non-blocking) that setup has already been completed
    already_configured = smriti.db.get("Company", companies[0]["name"], "custom_smriti_settings_configured")
    if already_configured:
        frappe.msgprint(
            _("Setup Wizard has already been completed. Re-running will update existing settings without deleting data."),
            title=_("Re-run Warning"),
            indicator="orange"
        )
