# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/backup_api.py
# @description: Configurable database and files backup, restore, and cloud-sync module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import os
import glob
import json
import shutil
import smtplib
import subprocess
import fnmatch
import frappe
from frappe import _
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from frappe.utils.backups import new_backup
from frappe.utils import get_site_path
from smriti_retail_os.security_constants import (
    SENSITIVE_EXPORT_FIELDS,
    PROTECTED_CONFIG_PATTERNS,
)


# ─── SMTP Password Encryption Helpers (F3-FIX v1.8.4) ───────────────────────
# Frappe's encrypted password store is used for SMTP credentials.
# The password is NEVER written to tabDefaultValue (plain-text JSON blob).
#
# Storage key: doctype="SMRITI Backup Config", name="smtp", fieldname="smtp_password"
# This is a virtual key — no actual SMRITI Backup Config DocType needed.
# frappe.utils.password uses tabPassword under the hood (AES encrypted at rest).

_SMTP_PWD_DOCTYPE  = "SMRITI Backup Config"
_SMTP_PWD_DOCNAME  = "smtp"
_SMTP_PWD_FIELD    = "smtp_password"


def _set_smtp_password(password):
    """
    Stores the SMTP password in Frappe's encrypted password store.
    The password is NEVER written to tabDefaultValue.
    """
    if not password:
        return
    from frappe.utils.password import set_encrypted_password
    set_encrypted_password(_SMTP_PWD_DOCTYPE, _SMTP_PWD_DOCNAME, password, _SMTP_PWD_FIELD)


def _get_smtp_password():
    """
    Retrieves the SMTP password from Frappe's encrypted password store.
    Returns empty string if not set.
    """
    try:
        from frappe.utils.password import get_decrypted_password
        return get_decrypted_password(
            _SMTP_PWD_DOCTYPE, _SMTP_PWD_DOCNAME, _SMTP_PWD_FIELD,
            raise_exception=False
        ) or ""
    except Exception:
        return ""


def migrate_legacy_smtp_password():
    """
    Migration helper — call once to migrate a plain-text SMTP password
    from the legacy tabDefaultValue JSON blob into the encrypted store.

    Safe to call multiple times (idempotent).
    Removes smtp_password from the JSON blob after migration.
    """
    settings_str = frappe.db.get_default("smriti_backup_settings")
    if not settings_str:
        return {"status": "skipped", "reason": "No legacy settings found."}

    try:
        stored = json.loads(settings_str)
    except Exception:
        return {"status": "skipped", "reason": "Could not parse legacy settings JSON."}

    legacy_pwd = stored.pop("smtp_password", None)
    if not legacy_pwd:
        return {"status": "skipped", "reason": "No plain-text smtp_password in legacy settings."}

    # Encrypt and store separately
    _set_smtp_password(legacy_pwd)

    # Re-save JSON without the password
    frappe.db.set_default("smriti_backup_settings", json.dumps(stored))
    frappe.db.commit()

    return {"status": "migrated", "message": "SMTP password migrated to encrypted store and removed from plain-text blob."}


# ─── Audit Event Logger ──────────────────────────────────────────────────────

def log_audit_event(event_type, message):
    """Writes a SMRITI audit event to the Frappe Activity Log."""
    try:
        frappe.get_doc({
            "doctype": "Activity Log",
            "user": frappe.session.user,
            "operation": event_type,
            "subject": message,
            "ip_address": getattr(frappe.local, "request_ip", None) or "Unknown",
            "status": "Success",
            "content": message,
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        # Never raise — audit failure must not interrupt the caller
        frappe.log_error("SMRITI Audit Log Error", frappe.get_traceback())


def _is_protected_file(name):
    """Returns True if name matches any PROTECTED_CONFIG_PATTERNS denylist."""
    return any(fnmatch.fnmatch(name, pat) for pat in PROTECTED_CONFIG_PATTERNS)


def _validate_backup_file_path(file_name):
    """Validates a backup file_name for safety.
    Raises ValidationError if the name contains path traversal sequences,
    directory separators, or any characters outside the expected safe set.
    """
    import re
    if not file_name:
        frappe.throw(_("File name is required."), frappe.ValidationError)
    # Reject any traversal or separator characters
    if any(c in file_name for c in ("/", "\\", "..")):
        frappe.throw(_("Invalid file name: path separators are not allowed."), frappe.ValidationError)
    # Allow only safe characters: alphanumeric, hyphen, underscore, dot, @
    if not re.match(r"^[\w.\-@]+$", file_name):
        frappe.throw(_("Invalid file name: contains disallowed characters."), frappe.ValidationError)
    # Ensure the resolved path stays inside the backups directory
    backups_dir = os.path.realpath(os.path.join(get_site_path(), "private", "backups"))
    resolved = os.path.realpath(os.path.join(backups_dir, file_name))
    if not resolved.startswith(backups_dir + os.sep) and resolved != backups_dir:
        frappe.throw(_("Invalid file path: access outside backup directory is not permitted."), frappe.PermissionError)


DEFAULT_SETTINGS = {
    "enable_local_backup": 1,
    "local_retention_days": 30,
    "enable_email_backup": 0,
    "email_recipient": "",
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
    "use_tls": 1,
    "enable_auto_backup": 1,
    "auto_backup_frequency": "Daily",
    "backup_type": "Database Only"
}


@frappe.whitelist()
def get_settings():
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    settings_str = frappe.db.get_default("smriti_backup_settings")
    if settings_str:
        try:
            stored = json.loads(settings_str)
            # Merge to ensure any new keys are defaulted
            merged = DEFAULT_SETTINGS.copy()
            merged.update(stored)
            # F3-FIX: smtp_password is no longer in the JSON blob — inject from encrypted store
            merged["smtp_password"] = _get_smtp_password()
            return merged
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in backup_api.py:179: {sys.exc_info()[1]}")
    result = DEFAULT_SETTINGS.copy()
    result["smtp_password"] = _get_smtp_password()
    return result


@frappe.whitelist()
def save_settings(settings):
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    if isinstance(settings, str):
        settings = json.loads(settings)

    # F3-FIX: Extract and separately encrypt smtp_password — NEVER store in JSON blob
    smtp_pwd = settings.pop("smtp_password", None)
    if smtp_pwd is not None:
        # Only update if a non-empty password was provided
        if smtp_pwd:
            _set_smtp_password(smtp_pwd)
        # If empty string passed, leave existing encrypted password intact

    old_settings = get_settings()
    old_enabled = old_settings.get("enable_backup_encryption", 0)
    new_enabled = settings.get("enable_backup_encryption", 0)

    if new_enabled:
        from smriti_retail_os.gpg_service import verify_gpg_available
        if not verify_gpg_available():
            raise RuntimeError("GPG executable is not available on system path.")

    if old_enabled != new_enabled:
        if "System Manager" not in frappe.get_roles():
            frappe.throw(_("System Manager role is required to modify encryption settings."), frappe.PermissionError)

        if new_enabled:
            from smriti_retail_os.gpg_service import get_active_key_version_and_key
            version, key = get_active_key_version_and_key()
            if not key:
                # Generate key on enable
                new_key = frappe.generate_hash(length=32)
                keys = {"v1": new_key}
                from frappe.installer import update_site_config
                update_site_config("backup_encryption_keys", keys)
                update_site_config("active_backup_encryption_key_version", "v1")
                frappe.conf.backup_encryption_keys = keys
                frappe.conf.active_backup_encryption_key_version = "v1"

    frappe.db.set_default("smriti_backup_settings", json.dumps(settings))
    frappe.db.commit()

    if old_enabled != new_enabled:
        if new_enabled:
            from smriti_retail_os.gpg_service import get_active_key_version_and_key, get_key_fingerprint
            version, key = get_active_key_version_and_key()
            fingerprint = get_key_fingerprint(key) if key else "None"
            log_audit_event("Backup Encryption Enabled", f"Backup encryption enabled by {frappe.session.user}. Key version: {version} (Fingerprint: {fingerprint})")
        else:
            log_audit_event("Backup Encryption Disabled", f"Backup encryption disabled by {frappe.session.user}.")

    return {"status": "success", "message": "Settings saved successfully."}



@frappe.whitelist()
def get_backup_status():
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)
        
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    if not os.path.exists(backups_dir):
        return {"total_count": 0, "total_size": "0 KB", "last_backup_date": "Never"}
        
    files = glob.glob(os.path.join(backups_dir, "*"))
    total_size = 0
    db_backups = []
    
    for f in files:
        if os.path.isfile(f):
            total_size += os.path.getsize(f)
            if "-database.sql.gz" in f:
                db_backups.append(f)
                
    last_date = "Never"
    if db_backups:
        latest = max(db_backups, key=os.path.getmtime)
        mtime = os.path.getmtime(latest)
        last_date = frappe.utils.format_datetime(frappe.utils.datetime.datetime.fromtimestamp(mtime))
        
    return {
        "total_count": len(db_backups),
        "total_size": _format_size(total_size),
        "last_backup_date": last_date
    }


@frappe.whitelist()
def get_backup_history():
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)
        
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    if not os.path.exists(backups_dir):
        return []
        
    files = glob.glob(os.path.join(backups_dir, "*"))
    history = []

    for f in files:
        if os.path.isfile(f):
            name = os.path.basename(f)

            # v1.8.2a: Omit any file matching the protected config denylist
            if _is_protected_file(name):
                continue

            # Skip sidecar json files
            if name.endswith(".json"):
                continue

            mtime = os.path.getmtime(f)
            size = os.path.getsize(f)

            # Determine type
            ftype = "other"
            if "-database.sql.gz" in name or name.endswith(".smriti.enc"):
                ftype = "database"
            elif "-files.tar" in name:
                ftype = "files"
            elif "-private-files.tar" in name:
                ftype = "private-files"

            history.append({
                "name": name,
                "size_bytes": size,
                "size": _format_size(size),
                "timestamp": mtime,
                "datetime": frappe.utils.format_datetime(frappe.utils.datetime.datetime.fromtimestamp(mtime)),
                "type": ftype
            })

    # Sort latest first
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    return history


# ─── Site Config Export (v1.8.2a) ────────────────────────────────────────────

@frappe.whitelist()
def export_site_config(password):
    """
    v1.8.2a: Streams a redacted site config as a JSON download.
    - Sensitive fields are replaced with '*** REDACTED ***'.
    - No file is written to the backup directory or any disk location.
    - Requires System Manager role and password re-authentication.
    """
    # ADJUSTMENT 3: Guest session check before everything else
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required."), frappe.PermissionError)

    # Role check
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("System Manager role is required to export site configuration."), frappe.PermissionError)

    # Password re-authentication
    import frappe.utils.password as fup
    try:
        fup.check_password(frappe.session.user, password)
    except frappe.AuthenticationError:
        frappe.throw(_("Invalid password. Re-authentication failed."), frappe.AuthenticationError)

    # Load site config and redact in memory
    config = frappe.get_site_config()
    redacted = dict(config)
    for field in SENSITIVE_EXPORT_FIELDS:
        if field in redacted:
            redacted[field] = "*** REDACTED ***"

    # Audit log
    log_audit_event(
        "Config Exported",
        f"Site config exported by {frappe.session.user}. Sensitive fields redacted."
    )

    # Stream as download — no file written to disk
    filename = "smriti-config-export-redacted.json"
    frappe.response.filename = filename
    frappe.response.filecontent = json.dumps(redacted, indent=2).encode("utf-8")
    frappe.response.type = "download"


# ─── v1.8.4 SMTP Password Migration Endpoint ─────────────────────────────────

@frappe.whitelist()
def run_smtp_password_migration():
    """
    F3-FIX v1.8.4: Migrates a plain-text SMTP password from tabDefaultValue
    into Frappe's encrypted password store (tabPassword).

    Safe to call multiple times — idempotent.
    Restricted to System Manager only.
    """
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("System Manager role is required to run SMTP password migration."), frappe.PermissionError)
    result = migrate_legacy_smtp_password()
    log_audit_event(
        "SMTP Password Migration",
        f"SMTP password migration run by {frappe.session.user}. Result: {result.get('status')}. {result.get('message', result.get('reason', ''))}"
    )
    return result


# ─── v1.8.3 Real Whitelisted Key Recovery Methods ────────────────────────────

@frappe.whitelist()
def verify_custodian_emails(emails):
    """Onboards custodians and sends verification OTPs."""
    import json
    if isinstance(emails, str):
        try:
            emails = json.loads(emails)
        except Exception:
            emails = [emails]
    from smriti_retail_os.key_recovery_service import send_verification_email
    res = []
    for email in emails:
        res.append(send_verification_email(email))
    return res


@frappe.whitelist()
def send_recovery_key(recipient_email=None):
    """Delegates to key_recovery_service.send_recovery_fragments."""
    from smriti_retail_os.key_recovery_service import send_recovery_fragments
    return send_recovery_fragments()


@frappe.whitelist()
def get_encryption_status():
    """Returns GPG status, active version, active key fingerprint and custodians."""
    from smriti_retail_os.key_recovery_service import get_encryption_status as ges
    return ges()


@frappe.whitelist()
def confirm_custodian_otp(email, otp):
    """Verifies the custodian OTP and sets status."""
    from smriti_retail_os.key_recovery_service import confirm_verification
    return confirm_verification(email, otp)


@frappe.whitelist()
def rotate_encryption_key(new_key):
    """Rotates the encryption key in frappe.conf and logs old/new versions."""
    from smriti_retail_os.key_recovery_service import rotate_encryption_key as rek
    return rek(new_key)


@frappe.whitelist()
def take_backup_now(backup_type="Database Only"):
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)
        
    ignore_files = True
    if backup_type == "Database & Files":
        ignore_files = False
        
    try:
        # Run Frappe's native backup generator
        generator = new_backup(ignore_files=ignore_files, force=True)
        generator.get_backup(force=True)
        
        # Paths generated
        db_path = generator.backup_path_db
        
        # 1. Run retention cleanups
        _cleanup_old_backups()

        # Encryption Logic (v1.8.3)
        settings = get_settings()
        encryption_enabled = bool(settings.get("enable_backup_encryption", 0))
        target_path = db_path
        
        if encryption_enabled and db_path:
            import hashlib
            from smriti_retail_os.gpg_service import verify_gpg_available, get_active_key_version_and_key, get_key_fingerprint, encrypt_file
            
            if not verify_gpg_available():
                log_audit_event("GPG Executable Missing", f"GPG is missing on site {frappe.local.site} at {frappe.utils.now()}.")
                raise RuntimeError("GPG executable is not available on system path.")
                
            version, key = get_active_key_version_and_key()
            if not key:
                frappe.throw(_("No active encryption key configured for encrypted backup."), frappe.ValidationError)
                
            if db_path.endswith("-database.sql.gz"):
                base_prefix = db_path[:-len("-database.sql.gz")]
                enc_path = f"{base_prefix}-database-{version}.smriti.enc"
                meta_path = f"{base_prefix}-database-{version}.smriti.json"
            else:
                enc_path = f"{db_path}-{version}.smriti.enc"
                meta_path = f"{db_path}-{version}.smriti.json"
                
            # Perform encryption and delete plaintext original
            encrypt_file(db_path, key, enc_path)
            
            # Compute SHA-256 hash of the encrypted file
            sha256 = hashlib.sha256()
            with open(enc_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            backup_sha256 = sha256.hexdigest()
            
            # Write metadata sidecar file
            meta_data = {
                "backup_id": os.path.basename(enc_path).split("-")[0],
                "key_version": version,
                "encrypted": True,
                "cipher": "AES256",
                "backup_sha256": backup_sha256
            }
            with open(meta_path, "w") as f:
                json.dump(meta_data, f, indent=2)
                
            # Log audit event
            fingerprint = get_key_fingerprint(key)
            log_audit_event(
                "Backup Encrypted",
                f"Database backup encrypted using key version {version} (Fingerprint: {fingerprint}). File: {os.path.basename(enc_path)}"
            )
            target_path = enc_path

        # 2. Handle Cloud Sync (Rclone) - CLD-01
        cloud_res = None
        if target_path:
            cloud_res = rclone_sync(target_path)

        # 3. Handle Email notification (Scalable) - CLD-01
        email_sent = False
        email_error = None

        if settings.get("email_recipient") and target_path:
            try:
                _email_backup(target_path, settings, cloud_status=cloud_res)
                email_sent = True
            except Exception as ex:
                email_error = str(ex)

        return {
            "status": "success",
            "message": "Backup and sync completed.",
            "file": os.path.basename(target_path) if target_path else "",
            "cloud_sync": cloud_res,
            "email_sent": email_sent,
            "email_error": email_error
        }
    except Exception as e:
        frappe.log_error("SMRITI Backup Error", str(e))
        return {
            "status": "failed",
            "message": str(e)
        }


@frappe.whitelist()
def delete_backup(file_name):
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    _validate_backup_file_path(file_name)
        
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    file_path = os.path.join(backups_dir, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        # Also clean up the metadata sidecar json file if deleting an encrypted backup
        if file_name.endswith(".smriti.enc"):
            meta_path = file_path.replace(".smriti.enc", ".smriti.json")
            if os.path.exists(meta_path):
                os.remove(meta_path)
        return {"status": "success", "message": f"File {file_name} deleted."}
    else:
        frappe.throw(_("File {0} not found.").format(file_name), frappe.DoesNotExistError)


@frappe.whitelist()
def restore_backup(file_name):
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)

    _validate_backup_file_path(file_name)
        
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    sql_path = os.path.join(backups_dir, file_name)
    
    if not os.path.exists(sql_path):
        frappe.throw(_("Backup file {0} not found.").format(file_name), frappe.DoesNotExistError)

    # Helper function to publish progress
    def publish_progress(message, percent):
        frappe.publish_realtime(
            "smriti.backup.progress",
            {"message": message, "percent": percent},
            user=frappe.session.user
        )

    # Check if backup file is encrypted
    is_encrypted = file_name.endswith(".smriti.enc")
    decrypted_tmp_path = None
    target_sql_path = sql_path
    key_version = "None"
    
    try:
        if is_encrypted:
            import re
            import hashlib
            import tempfile
            from smriti_retail_os.gpg_service import verify_gpg_available, get_key_from_conf, decrypt_file
            
            # Verify GPG available
            if not verify_gpg_available():
                log_audit_event("GPG Executable Missing", f"GPG is missing on site {frappe.local.site} at {frappe.utils.now()}.")
                raise RuntimeError("GPG executable is not available on system path.")
                
            # Parse version from filename
            version_match = re.search(r"-database-(v\d+)\.smriti\.enc$", file_name)
            if not version_match:
                version_match = re.search(r"-(v\d+)\.smriti\.enc$", file_name)
                
            if not version_match:
                version_match = re.search(r"-v(\d+)", file_name)
                if version_match:
                    filename_version = f"v{version_match.group(1)}"
                else:
                    raise RuntimeError(f"Could not parse key version from filename {file_name}")
            else:
                filename_version = version_match.group(1)
                
            key_version = filename_version
                
            # Check sidecar JSON
            meta_file_name = file_name.replace(".smriti.enc", ".smriti.json")
            meta_path = os.path.join(backups_dir, meta_file_name)
            if not os.path.exists(meta_path):
                raise RuntimeError(f"Metadata sidecar file {meta_file_name} not found.")
                
            with open(meta_path, "r") as f:
                meta_data = json.load(f)
                
            # Validate version
            meta_version = meta_data.get("key_version")
            if meta_version != filename_version:
                raise RuntimeError(f"Key version mismatch: filename version is {filename_version}, sidecar version is {meta_version}.")
                
            # Validate hash integrity
            sha256 = hashlib.sha256()
            with open(sql_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            actual_sha = sha256.hexdigest()
            expected_sha = meta_data.get("backup_sha256")
            if actual_sha != expected_sha:
                raise RuntimeError(f"Integrity check failed: encrypted backup file SHA-256 is {actual_sha}, expected {expected_sha}.")
                
            # 1. Progress: Decrypting backup...
            publish_progress("Decrypting backup...", 20)
            
            # Decrypt to a temporary location
            tmp_fd, decrypted_tmp_path = tempfile.mkstemp(suffix="-database.sql.gz", dir=backups_dir)
            os.close(tmp_fd)
            
            # Get key
            key = get_key_from_conf(filename_version)
            
            # Decrypt
            decrypt_file(sql_path, key, decrypted_tmp_path)
            target_sql_path = decrypted_tmp_path

        # 2. Progress: Verifying decrypted file...
        publish_progress("Verifying decrypted file...", 40)

        # Find matching files and private files
        prefix = file_name.split("-")[0] # E.g. "20260529_025305"
        
        # Try different suffix formats to be safe
        files_tar = None
        private_tar = None
        
        for suffix in ["files.tar", "frontend-files.tar", "frontend-public_files.tar"]:
            test_path = os.path.join(backups_dir, f"{prefix}-{suffix}")
            if os.path.exists(test_path):
                files_tar = test_path
                break
                
        for suffix in ["private-files.tar", "frontend-private-files.tar", "frontend-private_files.tar"]:
            test_path = os.path.join(backups_dir, f"{prefix}-{suffix}")
            if os.path.exists(test_path):
                private_tar = test_path
                break
                
        # Retrieve MariaDB root password
        db_root_password = os.environ.get("MARIADB_ROOT_PASSWORD") or os.environ.get("MYSQL_ROOT_PASSWORD")
        if not db_root_password:
            frappe.throw(_("MARIADB_ROOT_PASSWORD or MYSQL_ROOT_PASSWORD environment variable is not set. Restore cannot proceed."), frappe.ValidationError)
        
        cmd = [
            "bench",
            "--site",
            frappe.local.site,
            "restore",
            target_sql_path,
            "--db-root-password",
            db_root_password,
            "--force"
        ]
        
        if files_tar:
            cmd.extend(["--with-public-files", files_tar])
        if private_tar:
            cmd.extend(["--with-private-files", private_tar])
            
        # 3. Progress: Restoring database...
        publish_progress("Restoring database...", 60)

        # Execute restore subprocess
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                frappe.log_error("SMRITI Backup Restore Failure", f"Command: {' '.join(cmd)}\nStderr: {res.stderr}\nStdout: {res.stdout}")
                return {
                    "status": "failed",
                    "message": res.stderr or res.stdout or "Restoration process failed. Check Error Log."
                }
                
            # Log successful restore audit event
            if is_encrypted:
                log_audit_event(
                    "Encrypted Restore",
                    f"Encrypted backup restored. Filename: {file_name}. Key version: {key_version}. User: {frappe.session.user}"
                )
                
            # 4. Progress: Restore complete.
            publish_progress("Restore complete.", 100)

            return {
                "status": "success",
                "message": "Backup restored successfully. Logging out to reload session database."
            }
        except Exception as e:
            frappe.log_error("SMRITI Backup Restore Exception", str(e))
            return {
                "status": "failed",
                "message": str(e)
            }
    finally:
        # 5. Progress: Cleaning temporary files...
        publish_progress("Cleaning temporary files...", 80)
        
        # Secure deletion of decrypted temp file in all execution flows (shred / zero-overwrite fallback)
        if decrypted_tmp_path and os.path.exists(decrypted_tmp_path):
            import shutil
            shred_path = shutil.which("shred")
            if shred_path:
                try:
                    subprocess.run([shred_path, "-u", "-z", "-n", "1", decrypted_tmp_path], check=True, capture_output=True)
                except Exception:
                    try:
                        os.remove(decrypted_tmp_path)
                    except Exception:
                        import sys
                        _frappe = sys.modules.get('frappe')
                        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in backup_api.py:749: {sys.exc_info()[1]}")
            else:
                try:
                    # Fallback zero-overwrite
                    size = os.path.getsize(decrypted_tmp_path)
                    with open(decrypted_tmp_path, "r+b") as f:
                        f.write(b"\x00" * size)
                    os.remove(decrypted_tmp_path)
                except Exception:
                    try:
                        os.remove(decrypted_tmp_path)
                    except Exception:
                        import sys
                        _frappe = sys.modules.get('frappe')
                        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in backup_api.py:761: {sys.exc_info()[1]}")
        decrypted_tmp_path = None


def run_scheduled_backup():
    """Triggered by Frappe scheduler Daily. Checks configuration and runs backup/email/cleanup."""
    try:
        settings = get_settings()
        if not settings.get("enable_auto_backup"):
            return
            
        # Optional frequency logic: Daily is always run. 
        # Weekly/Monthly checks current day
        freq = settings.get("auto_backup_frequency")
        today = frappe.utils.datetime.date.today()
        
        if freq == "Weekly" and today.weekday() != 6: # Run on Sundays only
            return
        if freq == "Monthly" and today.day != 1: # Run on 1st of month only
            return
            
        # Trigger
        backup_type = settings.get("backup_type", "Database Only")
        take_backup_now(backup_type)
    except Exception as ex:
        frappe.log_error("SMRITI Scheduled Backup Error", str(ex))


def _cleanup_old_backups():
    settings = get_settings()
    if not settings.get("enable_local_backup"):
        return

    retention_days = int(settings.get("local_retention_days", 30))
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    if not os.path.exists(backups_dir):
        return

    import time
    now = time.time()
    cutoff = now - (retention_days * 86400)

    files = glob.glob(os.path.join(backups_dir, "*"))
    cleaned = 0
    for f in files:
        if os.path.isfile(f):
            mtime = os.path.getmtime(f)
            if mtime < cutoff:
                os.remove(f)
                cleaned += 1

    if cleaned:
        print(f"[SMRITI Backup] Cleaned up {cleaned} expired backup files older than {retention_days} days.")


def rclone_sync(file_path):
    """
    CLD-01: Syncs backup to cloud storage using rclone.
    Credentials fetched from SMRITI Company Settings.
    """
    company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    if not frappe.db.exists("SMRITI Company Settings", company):
        return {"status": "skipped", "message": "Settings not configured."}

    settings = frappe.get_doc("SMRITI Company Settings", company)
    if not settings.get("cloud_backup_enabled"):
        return {"status": "skipped", "message": "Cloud backup disabled in settings."}

    # Dynamic rclone config via environment variables (Secure)
    env = os.environ.copy()
    env["RCLONE_CONFIG_SMRITI_TYPE"] = "s3"
    env["RCLONE_CONFIG_SMRITI_PROVIDER"] = "Other" # Generic S3
    env["RCLONE_CONFIG_SMRITI_ACCESS_KEY_ID"] = settings.get("s3_access_key") or ""
    env["RCLONE_CONFIG_SMRITI_SECRET_ACCESS_KEY"] = settings.get_password("s3_secret_key") or ""
    env["RCLONE_CONFIG_SMRITI_REGION"] = settings.get("s3_region") or "ap-south-1"

    bucket = settings.get("s3_bucket") or "smriti-backups"
    remote_path = f"smriti:{bucket}/{os.path.basename(file_path)}"

    try:
        # Atomic rclone copy
        subprocess.run(["rclone", "copyto", file_path, remote_path], env=env, check=True, capture_output=True)
        return {"status": "success", "message": f"Synced to {remote_path}"}
    except Exception as e:
        msg = str(e)
        if hasattr(e, 'stderr'): msg = e.stderr
        frappe.log_error("SMRITI Rclone Error", msg)
        return {"status": "failed", "message": msg}


def _email_backup(file_path, settings, cloud_status=None):
    """
    CLD-01: Send scalable notification instead of heavy attachments.
    """
    recipient = settings.get("email_recipient")
    host = settings.get("smtp_host")
    port = int(settings.get("smtp_port", 587))
    user = settings.get("smtp_user")
    # F3-FIX: Always read SMTP password from encrypted store — never from plain-text settings dict.
    # settings.smtp_password may be populated by get_settings() for legacy callers,
    # but we always prefer the encrypted store as authoritative source.
    pwd = _get_smtp_password() or settings.get("smtp_password") or ""
    use_tls = settings.get("use_tls", 1)

    if not recipient or not host or not user or not pwd:
        return # Silently skip if not configured

    from email.mime.text import MIMEText

    filename = os.path.basename(file_path)
    subject = f"SMRITI Backup Notification - {filename}"

    body = f"""
SMRITI Retail OS - Automated Backup Report
------------------------------------------
Date: {frappe.utils.now()}
File: {filename}
Size: {_format_size(os.path.getsize(file_path))}

Cloud Sync Status:
{json.dumps(cloud_status, indent=2) if cloud_status else "Not Attempted"}

Note: Large backup files are no longer attached to this email to ensure reliability.
Please retrieve backups from your configured Cloud Storage or the local SMRITI Recovery Layer.
"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = recipient

    # Send
    smtp = smtplib.SMTP(host, port)
    if use_tls:
        smtp.starttls()
    smtp.login(user, pwd)
    smtp.sendmail(user, recipient, msg.as_string())
    smtp.quit()

def _format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1048576:
        return f"{size_bytes / 1024.0:.1f} KB"
    elif size_bytes < 1073741824:
        return f"{size_bytes / 1048576.0:.1f} MB"
    else:
        return f"{size_bytes / 1073741824.0:.1f} GB"
