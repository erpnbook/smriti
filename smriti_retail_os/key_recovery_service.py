# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/key_recovery_service.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/key_recovery_service.py
# @description: Custodian email onboarding, OTP validation, and midpoint splitting.
# @author: Antigravity AI
# @date: 2026-06-10
# @version: 1.8.3
#

import re
import random
import hashlib
import json
import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date

def validate_smtp_configured():
    """Verifies that an enabled outgoing Email Account exists in Frappe."""
    if not frappe.db.exists("Email Account", {"enable_outgoing": 1}):
        frappe.throw(
            _("Outgoing email is not configured. Please configure an outgoing Email Account first."),
            frappe.ValidationError
        )

def check_manager_role():
    """Enforces System Manager role check."""
    if "System Manager" not in frappe.get_roles():
        frappe.throw(
            _("Not authorized. System Manager role is required."),
            frappe.PermissionError
        )

def send_verification_email(email):
    """Onboards a key custodian and sends a 15-minute OTP."""
    check_manager_role()
    validate_smtp_configured()
    
    if not email or "@" not in email:
        frappe.throw(_("Invalid email address."), frappe.ValidationError)
        
    # Generate 6-digit OTP
    otp = "{:06d}".format(random.randint(0, 999999))
    hashed_otp = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    expiry = add_to_date(now_datetime(), minutes=15)
    
    if frappe.db.exists("SMRITI Key Custodian", email):
        doc = frappe.get_doc("SMRITI Key Custodian", email)
        doc.otp_hash = hashed_otp
        doc.otp_expiry = expiry
        doc.status = "Pending"
        doc.verified = 0
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({
            "doctype": "SMRITI Key Custodian",
            "email": email,
            "name": email,
            "custodian_name": email.split("@")[0].title(),
            "otp_hash": hashed_otp,
            "otp_expiry": expiry,
            "status": "Pending",
            "verified": 0
        })
        doc.insert(ignore_permissions=True)
        
    subject = "SMRITI Key Custodian OTP Verification"
    message = f"Your custodian verification code is: {otp}. It expires in 15 minutes."
    
    frappe.sendmail(recipients=[email], subject=subject, message=message, now=True)
    return {"status": "success", "message": f"Verification email sent to {email}."}

def confirm_verification(email, otp):
    """Validates OTP, sets verified state, and logs the event."""
    check_manager_role()
    
    if not frappe.db.exists("SMRITI Key Custodian", email):
        frappe.throw(_("Custodian {0} not found.").format(email), frappe.DoesNotExistError)
        
    doc = frappe.get_doc("SMRITI Key Custodian", email)
    
    # Check expiration
    if now_datetime() > doc.otp_expiry:
        frappe.throw(_("Verification code has expired. Please request a new OTP."), frappe.ValidationError)
        
    # Check OTP hash
    hashed = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    if hashed != doc.otp_hash:
        frappe.throw(_("Invalid verification code. Please try again."), frappe.ValidationError)
        
    doc.verified = 1
    doc.status = "Verified"
    doc.verification_date = now_datetime()
    doc.otp_hash = None
    doc.otp_expiry = None
    doc.save(ignore_permissions=True)
    
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event("Custodian Verified", f"Custodian {email} verified successfully.")
    
    return {"status": "success", "message": f"Custodian {email} verified successfully."}

def mask_email(email):
    """Masks email address for display and auditing."""
    if not email or "@" not in email:
        return "***"
    parts = email.split("@")
    if len(parts) != 2:
        return "***"
    name, domain = parts[0], parts[1]
    if len(name) <= 3:
        return "***@" + domain
    return name[:3] + "***@" + domain

def send_recovery_fragments():
    """Midpoint splits the active key and sends parts to the two custodians."""
    check_manager_role()
    
    custodians = frappe.get_all("SMRITI Key Custodian", filters={"status": "Verified", "verified": 1}, fields=["email"])
    if len(custodians) != 2:
        frappe.throw(_("Key recovery fragments can only be dispatched when exactly 2 verified custodians are registered."), frappe.ValidationError)
        
    from smriti_retail_os.gpg_service import get_active_key_version_and_key, get_key_fingerprint
    version, key = get_active_key_version_and_key()
    if not key:
        frappe.throw(_("No active backup encryption key is configured."), frappe.ValidationError)
        
    mid = len(key) // 2
    part1 = key[:mid]
    part2 = key[mid:]
    
    c1 = custodians[0]["email"]
    c2 = custodians[1]["email"]
    
    subject = f"SMRITI Key Recovery Fragment - Key Version {version}"
    msg1 = f"Here is your key recovery fragment (Part 1 of 2) for key version {version}:\n\n{part1}\n\nPlease keep it secure."
    msg2 = f"Here is your key recovery fragment (Part 2 of 2) for key version {version}:\n\n{part2}\n\nPlease keep it secure."
    
    # Synchronous delivery (now=True)
    frappe.sendmail(recipients=[c1], subject=subject, message=msg1, now=True)
    frappe.sendmail(recipients=[c2], subject=subject, message=msg2, now=True)
    
    for c_email in [c1, c2]:
        doc = frappe.get_doc("SMRITI Key Custodian", c_email)
        doc.last_recovery_sent = now_datetime()
        doc.save(ignore_permissions=True)
        
    masked_c1 = mask_email(c1)
    masked_c2 = mask_email(c2)
    
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event("Recovery Fragments Sent", f"Recovery key fragments for version {version} sent to {masked_c1} and {masked_c2}.")
    
    return {"status": "success", "message": f"Fragments for version {version} sent successfully."}


def rotate_encryption_key(new_key):
    """Rotates the encryption key in frappe.conf and logs the versions and fingerprints."""
    check_manager_role()
    
    if not new_key or len(new_key) < 16:
        frappe.throw(_("New encryption key must be at least 16 characters long."), frappe.ValidationError)
        
    version = frappe.conf.get("active_backup_encryption_key_version") or "v0"
    keys = frappe.conf.get("backup_encryption_keys") or {}
    if isinstance(keys, str):
        try:
            keys = json.loads(keys)
        except Exception:
            keys = {}
            
    # Parse version number and increment
    match = re.match(r"v(\d+)", version)
    if match:
        num = int(match.group(1))
    else:
        num = 0
    new_version = f"v{num + 1}"
    
    keys[new_version] = new_key
    
    from frappe.installer import update_site_config
    update_site_config("backup_encryption_keys", keys)
    update_site_config("active_backup_encryption_key_version", new_version)
    
    frappe.conf.backup_encryption_keys = keys
    frappe.conf.active_backup_encryption_key_version = new_version
    
    from smriti_retail_os.gpg_service import get_key_fingerprint
    from smriti_retail_os.backup_api import log_audit_event
    
    old_fingerprint = get_key_fingerprint(keys.get(version)) if version != "v0" else "None"
    new_fingerprint = get_key_fingerprint(new_key)
    
    log_audit_event(
        "Backup Key Rotated",
        f"Encryption Key Rotated. Old Version: {version} (Fingerprint: {old_fingerprint}). "
        f"New Version: {new_version} (Fingerprint: {new_fingerprint}). User: {frappe.session.user}"
    )
    
    return {"status": "success", "message": f"Encryption key successfully rotated to version {new_version}."}

def get_encryption_status():
    """Returns GPG status, key version/fingerprint, and custodian info."""
    # Check role
    roles = frappe.get_roles()
    if "System Manager" not in roles and "SMRITI Store Manager" not in roles:
        frappe.throw(_("Not authorized."), frappe.PermissionError)
        
    from smriti_retail_os.gpg_service import verify_gpg_available, get_active_key_version_and_key, get_key_fingerprint
    gpg_ok = verify_gpg_available()
    version, key = get_active_key_version_and_key()
    fingerprint = get_key_fingerprint(key) if key else ""
    
    from smriti_retail_os.backup_api import get_settings
    settings = get_settings()
    encryption_enabled = bool(settings.get("enable_backup_encryption", 0))
    
    custodians = frappe.get_all(
        "SMRITI Key Custodian", 
        fields=["custodian_name", "email", "status", "verified", "verification_date", "last_recovery_sent"]
    )
    
    return {
        "gpg_available": gpg_ok,
        "active_key_version": version or "None",
        "active_key_fingerprint": fingerprint or "None",
        "encryption_enabled": encryption_enabled,
        "custodians": custodians
    }
