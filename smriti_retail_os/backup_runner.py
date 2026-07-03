# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/backup_runner.py
# @description: Standalone python backup daemon script for auto-backups.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import os
import glob
import shutil
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import frappe

def run_backup():
    print("[SMRITI Backup Runner] Starting backup process...")
    try:
        # Initialize frappe site context — configurable via environment variables
        # H-1 remediation (hardcoding audit 2026-07-03): never assume a fixed site name or bench path
        site = os.environ.get("SMRITI_SITE", "frontend")
        bench_path = os.environ.get("BENCH_PATH", "/home/frappe/frappe-bench")
        sites_path = os.path.join(bench_path, "sites")
        frappe.init(site=site, sites_path=sites_path)
        frappe.connect()
        
        # Read SMRITI backup settings from DB
        from smriti_retail_os.backup_api import get_settings
        settings = get_settings()
        
        if not settings.get("enable_auto_backup"):
            print("  - Auto backup is disabled in settings. Skipping.")
            return
            
        backup_type = settings.get("backup_type", "Database Only")
        ignore_files = True if backup_type == "Database Only" else False
        
        print(f"  - Triggering backup ({backup_type})...")
        from frappe.utils.backups import new_backup
        generator = new_backup(ignore_files=ignore_files, force=True)
        generator.get_backup(force=True)
        
        db_path = generator.backup_path_db
        files_path = generator.backup_path_files
        private_path = generator.backup_path_private_files
        
        # Copy to host-mounted backups directory — configurable via env var
        host_backups_dir = os.environ.get("SMRITI_BACKUPS_DIR", os.path.join(bench_path, "backups"))
        if os.path.exists(host_backups_dir):
            print("  - Copying backups to host backups folder...")
            for path in [db_path, files_path, private_path]:
                if path and os.path.exists(path):
                    shutil.copy2(path, host_backups_dir)
                    print(f"    + Copied {os.path.basename(path)}")
        else:
            print(f"  - Host backups directory '{host_backups_dir}' not found. Skipping copy to host.")
                    
        # Email backup
        enable_email = settings.get("enable_email_backup") or os.environ.get("SMTP_HOST")
        if enable_email and db_path and os.path.exists(db_path):
            recipient = settings.get("email_recipient") or os.environ.get("BACKUP_RECEIVER")
            if recipient:
                print(f"  - Dispatching backup email to {recipient}...")
                try:
                    _send_email(db_path, settings, recipient)
                except Exception as mail_ex:
                    print(f"    ! Failed to send email: {mail_ex}")
            else:
                print("  - Skipping email: No recipient configured.")
                
        # Cleanup local and host backups
        retention = int(settings.get("local_retention_days", 30))
        if db_path:
            _cleanup_directory(os.path.dirname(db_path), retention)
        if os.path.exists(host_backups_dir):
            _cleanup_directory(host_backups_dir, retention)
            
        print("[SMRITI Backup Runner] Backup process completed successfully.")
        
    except Exception as ex:
        print(f"[SMRITI Backup Runner] ERROR: {ex}")
        try:
            frappe.log_error("SMRITI Backup Runner Error", str(ex))
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in backup_runner.py:86: {sys.exc_info()[1]}")

def _send_email(file_path, settings, recipient):
    host = settings.get("smtp_host") or os.environ.get("SMTP_HOST")
    port_val = settings.get("smtp_port") or os.environ.get("SMTP_PORT")
    port = int(port_val) if port_val else 587
    user = settings.get("smtp_user") or os.environ.get("SMTP_USER")
    pwd = settings.get("smtp_password") or os.environ.get("SMTP_PASS")
    use_tls = int(settings.get("use_tls", 1))
    
    if not host or not user or not pwd:
        print("    ! SMTP credentials not configured. Skipping email.")
        return
        
    msg = MIMEMultipart()
    msg['Subject'] = f"SMRITI Retail OS Auto-Backup - {os.path.basename(file_path)}"
    msg['From'] = os.environ.get("SMTP_SENDER") or user
    msg['To'] = recipient
    
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)
        
    smtp = smtplib.SMTP(host, port)
    if use_tls:
        smtp.starttls()
    smtp.login(user, pwd)
    smtp.sendmail(msg['From'], recipient, msg.as_string())
    smtp.quit()
    print("    + Email sent successfully.")

def _cleanup_directory(directory, retention_days):
    import time
    now = time.time()
    cutoff = now - (retention_days * 86400)
    cleaned = 0
    for f in glob.glob(os.path.join(directory, "*")):
        if os.path.isfile(f):
            mtime = os.path.getmtime(f)
            if mtime < cutoff:
                os.remove(f)
                cleaned += 1
    if cleaned:
        print(f"  - Cleaned up {cleaned} expired files in {directory} older than {retention_days} days.")

if __name__ == "__main__":
    run_backup()
