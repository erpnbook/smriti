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
import frappe
from frappe import _
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from frappe.utils.backups import new_backup
from frappe.utils import get_site_path


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
            return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS


@frappe.whitelist()
def save_settings(settings):
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"), frappe.PermissionError)
        
    if isinstance(settings, str):
        settings = json.loads(settings)
        
    frappe.db.set_default("smriti_backup_settings", json.dumps(settings))
    frappe.db.commit()
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
            mtime = os.path.getmtime(f)
            size = os.path.getsize(f)
            
            # Determine type
            ftype = "other"
            if "-database.sql.gz" in name:
                ftype = "database"
            elif "-files.tar" in name:
                ftype = "files"
            elif "-private-files.tar" in name:
                ftype = "private-files"
            elif "-site_config_backup.json" in name:
                ftype = "config"
                
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

        # 2. Handle Cloud Sync (Rclone) - CLD-01
        cloud_res = None
        if db_path:
            cloud_res = rclone_sync(db_path)

        # 3. Handle Email notification (Scalable) - CLD-01
        settings = get_settings()
        email_sent = False
        email_error = None

        if settings.get("email_recipient"):
            try:
                _email_backup(db_path, settings, cloud_status=cloud_res)
                email_sent = True
            except Exception as ex:
                email_error = str(ex)

        return {
            "status": "success",
            "message": "Backup and sync completed.",
            "file": os.path.basename(db_path) if db_path else "",
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

    # Prevent directory traversal
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        frappe.throw(_("Invalid file name"), frappe.ValidationError)
        
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    file_path = os.path.join(backups_dir, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
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
    db_root_password = os.environ.get("MARIADB_ROOT_PASSWORD") or os.environ.get("MYSQL_ROOT_PASSWORD") or "admin"
    
    cmd = [
        "bench",
        "--site",
        frappe.local.site,
        "restore",
        sql_path,
        "--db-root-password",
        db_root_password,
        "--force"
    ]
    
    if files_tar:
        cmd.extend(["--with-public-files", files_tar])
    if private_tar:
        cmd.extend(["--with-private-files", private_tar])
        
    # Execute restore subprocess
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            frappe.log_error("SMRITI Backup Restore Failure", f"Command: {' '.join(cmd)}\nStderr: {res.stderr}\nStdout: {res.stdout}")
            return {
                "status": "failed",
                "message": res.stderr or res.stdout or "Restoration process failed. Check Error Log."
            }
            
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
    pwd = settings.get("smtp_password")
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
