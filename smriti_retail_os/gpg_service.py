# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/gpg_service.py
# @description: SMRITI Gpg Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/gpg_service.py
# @description: GPG-only symmetric encryption/decryption and key versioning.
# @author: Antigravity AI
# @date: 2026-06-10
# @version: 1.8.3
#

import os
import json
import subprocess
import hashlib
import frappe
from smriti_retail_os.security_constants import GPG_CIPHER_ALGO

def verify_gpg_available():
    """Checks if gpg is installed and accessible in the system path."""
    try:
        res = subprocess.run(["gpg", "--version"], capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False

def encrypt_file(src_path, passphrase, dest_path):
    """Encrypts a file symmetrically using GPG and deletes the original."""
    if not verify_gpg_available():
        raise RuntimeError("GPG executable is not available on the system path.")
        
    cmd = [
        "gpg",
        "--symmetric",
        "--cipher-algo",
        GPG_CIPHER_ALGO,
        "--batch",
        "--yes",
        "--passphrase-fd",
        "0",
        "-o",
        dest_path,
        src_path
    ]
    
    try:
        res = subprocess.run(cmd, input=passphrase, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"GPG encryption failed: {res.stderr}")
    except Exception as e:
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in gpg_service.py:62: {sys.exc_info()[1]}")
        raise RuntimeError(f"GPG encryption exception: {str(e)}")
        
    # Delete original source file only on success
    if os.path.exists(dest_path) and os.path.exists(src_path):
        os.remove(src_path)

def decrypt_file(enc_path, passphrase, dest_path):
    """Decrypts a symmetric encrypted GPG file."""
    if not verify_gpg_available():
        raise RuntimeError("GPG executable is not available on the system path.")
        
    cmd = [
        "gpg",
        "--decrypt",
        "--batch",
        "--yes",
        "--passphrase-fd",
        "0",
        "-o",
        dest_path,
        enc_path
    ]
    
    try:
        res = subprocess.run(cmd, input=passphrase, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"GPG decryption failed: {res.stderr}")
    except Exception as e:
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in gpg_service.py:95: {sys.exc_info()[1]}")
        raise RuntimeError(f"GPG decryption exception: {str(e)}")

def get_key_from_conf(version):
    """Retrieves a specific key version from frappe.conf. Raises RuntimeError if not found."""
    keys = frappe.conf.get("backup_encryption_keys") or {}
    if isinstance(keys, str):
        try:
            keys = json.loads(keys)
        except Exception:
            keys = {}
    
    key = keys.get(version)
    if not key:
        raise RuntimeError(f"Encryption key version {version} not found.")
    return key

def get_active_key_version_and_key():
    """Returns tuple of (active_version, key) from frappe.conf.
    If not configured, returns None, None.
    """
    version = frappe.conf.get("active_backup_encryption_key_version")
    keys = frappe.conf.get("backup_encryption_keys") or {}
    if isinstance(keys, str):
        try:
            keys = json.loads(keys)
        except Exception:
            keys = {}
            
    if not version or not keys:
        # Check if legacy key exists and initialize as v1
        legacy_key = frappe.conf.get("backup_encryption_key")
        if legacy_key:
            version = "v1"
            keys = {"v1": legacy_key}
            from frappe.installer import update_site_config
            update_site_config("backup_encryption_keys", keys)
            update_site_config("active_backup_encryption_key_version", "v1")
            frappe.conf.backup_encryption_keys = keys
            frappe.conf.active_backup_encryption_key_version = "v1"
            return "v1", legacy_key
        return None, None
        
    key = keys.get(version)
    if not key:
        return None, None
    return version, key

def get_key_fingerprint(key):
    """Returns a 16-character SHA-256 fingerprint prefix of the key."""
    if not key:
        return ""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
