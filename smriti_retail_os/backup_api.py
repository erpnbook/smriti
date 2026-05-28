# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/backup_api.py
# @description: Configurable database and files backup and restore module.
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
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from frappe.utils.backups import new_backup
from frappe.utils import get_site_path


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
        frappe.throw("Not authorized", frappe.PermissionError)
        
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
        frappe.throw("Not authorized", frappe.PermissionError)
        
    if isinstance(settings, str):
        settings = json.loads(settings)
        
    frappe.db.set_default("smriti_backup_settings", json.dumps(settings))
    frappe.db.commit()
    return {"status": "success", "message": "Settings saved successfully."}


@frappe.whitelist()
def get_backup_status():
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw("Not authorized", frappe.PermissionError)
        
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
        frappe.throw("Not authorized", frappe.PermissionError)
        
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
        frappe.throw("Not authorized", frappe.PermissionError)
        
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
        
        # 2. Handle Email backup if enabled
        settings = get_settings()
        email_sent = False
        email_error = None
        
        if settings.get("enable_email_backup") and settings.get("email_recipient") and db_path:
            try:
                _email_backup(db_path, settings)
                email_sent = True
            except Exception as ex:
                email_error = str(ex)
                
        return {
            "status": "success",
            "message": "Backup completed successfully.",
            "file": os.path.basename(db_path) if db_path else "",
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
        frappe.throw("Not authorized", frappe.PermissionError)
        
    # Prevent directory traversal
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        frappe.throw("Invalid file name")
        
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    file_path = os.path.join(backups_dir, file_name)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "success", "message": f"File {file_name} deleted."}
    else:
        frappe.throw(f"File {file_name} not found.")


@frappe.whitelist()
def restore_backup(file_name):
    if "SMRITI Store Manager" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw("Not authorized", frappe.PermissionError)
        
    # Prevent directory traversal
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        frappe.throw("Invalid file name")
        
    backups_dir = os.path.join(get_site_path(), "private", "backups")
    sql_path = os.path.join(backups_dir, file_name)
    
    if not os.path.exists(sql_path):
        frappe.throw(f"Backup file {file_name} not found.")
        
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


def _email_backup(file_path, settings):
    recipient = settings.get("email_recipient")
    host = settings.get("smtp_host")
    port = int(settings.get("smtp_port", 587))
    user = settings.get("smtp_user")
    pwd = settings.get("smtp_password")
    use_tls = settings.get("use_tls", 1)
    
    if not recipient or not host or not user or not pwd:
        raise ValueError("SMTP SMTP configurations are incomplete.")
        
    msg = MIMEMultipart()
    msg['Subject'] = f"SMRITI Retail OS Auto-Backup - {os.path.basename(file_path)}"
    msg['From'] = user
    msg['To'] = recipient
    
    # Attach backup file
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)
        
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
