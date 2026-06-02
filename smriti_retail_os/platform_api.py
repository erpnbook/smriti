# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/platform_api.py
# @description: Technical administration APIs for the SMRITI Platform Center.
#               - Enforces Administrator/Admin user restriction
#               - Provides diagnostics, system health, backups, migrations, repair tools
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-02
# @version: 1.1.0
# @license: MIT
#

import frappe
import os
import json
import subprocess
from frappe import _
from frappe.utils import get_site_path, now_datetime

def _check_access(action):
    """
    Enforces access rules based on user role and session:
    - 'Administrator' gets full access to everything.
    - 'Admin' gets access only to: view health, view/create/download backups, and restore backup.
    - Any other user is blocked.
    """
    user = frappe.session.user
    if user == "Administrator":
        return True
    elif user == "Admin":
        allowed_admin_actions = ["health", "get_backups", "create_backup", "restore_backup"]
        if action in allowed_admin_actions:
            return True
        frappe.throw(
            _("Access Denied: Admin user is not authorized to perform this action ({0}).").format(action),
            frappe.PermissionError
        )
    else:
        frappe.throw(
            _("Access Denied: Platform Center is restricted to Administrator and Admin accounts only."),
            frappe.PermissionError
        )

@frappe.whitelist()
def get_system_health():
    """Fetches System Health metrics."""
    _check_access("health")
    
    # 1. Site Status
    site_status = {
        "site_name": frappe.local.site,
        "db_name": frappe.conf.db_name,
        "frappe_version": frappe.__version__,
    }
    try:
        from smriti_retail_os.branding_api import get_versions
        versions = get_versions()
        site_status["versions"] = versions
    except Exception:
        site_status["versions"] = {}

    # 2. Database Status
    db_status = {
        "db_type": frappe.db.db_type,
        "db_host": frappe.conf.db_host or "localhost",
        "db_port": frappe.conf.db_port or "3306",
    }
    try:
        db_status["db_version"] = frappe.db.sql("SELECT VERSION()")[0][0]
        db_status["table_count"] = frappe.db.sql("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()")[0][0]
    except Exception as e:
        db_status["error"] = str(e)

    # 3. Scheduler Status
    scheduler_status = {}
    try:
        from frappe.utils.scheduler import is_scheduler_inactive
        scheduler_status["active"] = not is_scheduler_inactive()
        scheduler_status["last_event"] = frappe.db.get_global("scheduler_last_event") or "Never"
    except Exception as e:
        scheduler_status["error"] = str(e)

    # 4. Redis Status
    redis_status = {}
    try:
        redis_status["cache_ping"] = frappe.cache().ping()
        info = frappe.cache().info()
        redis_status["used_memory_human"] = info.get("used_memory_human", "N/A")
        redis_status["redis_version"] = info.get("redis_version", "N/A")
        redis_status["uptime_in_days"] = info.get("uptime_in_days", "N/A")
    except Exception as e:
        redis_status["error"] = str(e)

    # 5. Queue Status
    queue_status = {}
    try:
        from frappe.utils.background_jobs import get_queue_list
        queues = get_queue_list()
        queue_status["queues"] = queues
        # Total jobs count
        queue_status["failed_jobs_count"] = frappe.db.count("Error Log", {"method": ["like", "%RQ Job%"]})
    except Exception as e:
        queue_status["error"] = str(e)

    # 6. Last Migration Status
    migration_status = {}
    try:
        last_patches = frappe.db.get_all(
            "Patch Log",
            fields=["patch", "creation"],
            limit=5,
            order_by="creation desc"
        )
        migration_status["last_patches"] = last_patches
    except Exception as e:
        migration_status["error"] = str(e)

    return {
        "site_status": site_status,
        "db_status": db_status,
        "scheduler_status": scheduler_status,
        "redis_status": redis_status,
        "queue_status": queue_status,
        "migration_status": migration_status
    }

@frappe.whitelist()
def get_backup_history():
    """Lists files in the private/backups directory."""
    _check_access("get_backups")
    
    backup_path = get_site_path("private", "backups")
    if not os.path.exists(backup_path):
        return []
        
    backups = []
    for f in os.listdir(backup_path):
        fpath = os.path.join(backup_path, f)
        if os.path.isfile(fpath) and (f.endswith(".gz") or f.endswith(".json")):
            stat = os.stat(fpath)
            backups.append({
                "filename": f,
                "size_bytes": stat.st_size,
                "modified": now_datetime().fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
            
    # Sort latest first
    backups.sort(key=lambda x: x["modified"], reverse=True)
    return backups

@frappe.whitelist()
def trigger_backup(backup_type="all"):
    """Triggers backup in the background."""
    _check_access("create_backup")
    
    from frappe.utils.backups import new_backup
    try:
        backup_files_only = False
        backup_db_only = False
        
        if backup_type == "database":
            backup_db_only = True
        elif backup_type == "files":
            backup_files_only = True
            
        if backup_type == "all":
            odb = new_backup(with_files=True)
        elif backup_files_only:
            odb = new_backup(with_files=True, backup_db=False)
        else:
            odb = new_backup(with_files=False)
            
        return {
            "success": True,
            "message": _("Backup created successfully!"),
            "data": odb
        }
    except Exception as e:
        frappe.log_error(f"Platform Center Backup Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def run_migration_action(action):
    """Executes migration actions."""
    _check_access("migration")
    
    logs = []
    try:
        if action == "clear_cache":
            frappe.clear_cache()
            logs.append("Cache cleared successfully.")
        elif action == "clear_website_cache":
            frappe.clear_website_cache()
            logs.append("Website cache cleared successfully.")
        elif action == "rebuild_search":
            from frappe.search.sqlite_search import rebuild_sqlite_search_index
            rebuild_sqlite_search_index()
            logs.append("Search index rebuilt successfully.")
        elif action == "reload_doctypes":
            from smriti_retail_os.setup import setup_smriti_retail_os
            setup_smriti_retail_os()
            logs.append("SMRITI custom DocTypes and attributes reloaded.")
        elif action == "run_migrate":
            cmd = ["bench", "--site", frappe.local.site, "migrate"]
            frappe.enqueue("smriti_retail_os.platform_api.execute_command", cmd=cmd, queue="long", job_name="Platform Center Migrate")
            logs.append("Migration triggered in the background. Check logs shortly.")
        else:
            frappe.throw(_("Invalid migration action."))
            
        return {"success": True, "logs": logs}
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_command(cmd):
    """Worker task to execute bench command."""
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        frappe.logger().info(f"[Platform Center] {cmd} Output: {res.stdout}")
    except Exception as e:
        frappe.log_error(f"[Platform Center] Failed command {cmd}: {str(e)}")

@frappe.whitelist()
def get_diagnostics(log_type="error", limit=50):
    """Returns diagnostics and log listings."""
    _check_access("diagnostics")
    
    limit = int(limit)
    if log_type == "error":
        return frappe.db.get_all(
            "Error Log",
            fields=["name", "method", "creation", "error"],
            limit=limit,
            order_by="creation desc"
        )
    elif log_type == "failed_jobs":
        return frappe.db.get_all(
            "Error Log",
            filters={"method": ["like", "%RQ Job%"]},
            fields=["name", "method", "creation", "error"],
            limit=limit,
            order_by="creation desc"
        )
    elif log_type == "jobs":
        from frappe.utils.background_jobs import get_queue
        jobs = []
        try:
            for q_name in ["default", "long", "short"]:
                q = get_queue(q_name)
                for j in q.jobs:
                    jobs.append({
                        "id": j.id,
                        "name": j.name,
                        "created_at": j.created_at.strftime("%Y-%m-%d %H:%M:%S") if j.created_at else "",
                        "queue": q_name,
                        "status": j.get_status()
                    })
        except Exception:
            pass
        return jobs
    return []

@frappe.whitelist()
def run_repair(tool, dry_run=0):
    """Runs targeted repairs and checks."""
    _check_access("repair")
    
    dry_run = int(dry_run)
    logs = []
    records = []
    try:
        if tool == "verify_master":
            from smriti_retail_os.setup import seed_master_doctypes
            seed_master_doctypes()
            logs.append("SMRITI custom master lists and footwear attributes verified/seeded.")
            
        elif tool == "verify_company":
            from smriti_retail_os.company_api import get_active_company, ensure_company_settings
            co = get_active_company()
            if co:
                ensure_company_settings(co)
                logs.append(f"Company Settings verified for '{co}'.")
            else:
                logs.append("No active company found to verify.")
                
        elif tool == "verify_gst":
            from smriti_retail_os.company_api import get_active_company
            co = get_active_company()
            if co:
                abbr = frappe.db.get_value("Company", co, "abbr")
                mops = ["CGST", "SGST", "IGST"]
                for mop in mops:
                    full_acc = f"{mop} - {abbr}"
                    if not frappe.db.exists("Account", full_acc):
                        logs.append(f"WARNING: Tax ledger {full_acc} is missing.")
                    else:
                        logs.append(f"OK: Tax ledger {full_acc} verified.")
            else:
                logs.append("No active company to verify GST Configuration.")
                
        elif tool == "rebuild_permissions":
            from smriti_retail_os.setup import setup_smriti_retail_os
            setup_smriti_retail_os()
            logs.append("SMRITI roles (Cashier, Store Manager) and workspace permissions rebuilt.")
            
        elif tool == "fix_broken_links":
            companies = frappe.get_all("Company", pluck="name")
            stale_rows = frappe.db.sql("""
                SELECT name, parent, company, idx FROM `tabMode of Payment Account`
            """, as_dict=True)
            cleaned = 0
            for row in stale_rows:
                if row.company not in companies:
                    records.append({
                        "name": row.name,
                        "parent": row.parent,
                        "company": row.company,
                        "idx": row.idx
                    })
                    if not dry_run:
                        frappe.db.delete("Mode of Payment Account", {"name": row.name})
                        logs.append(f"Deleted stale Mode of Payment Account row: {row.name} for non-existent company '{row.company}'.")
                        cleaned += 1
            
            if dry_run:
                logs.append(f"Dry Run: Found {len(records)} stale references that would be deleted.")
            else:
                if cleaned == 0:
                    logs.append("No stale company references found in child tables.")
                else:
                    frappe.db.commit()
                    logs.append(f"Successfully cleaned {cleaned} stale links from the database.")
            
        return {"success": True, "logs": logs, "records": records}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def toggle_maintenance_mode(enable):
    """Toggles emergency maintenance mode in site_config.json."""
    _check_access("maintenance")
    
    enable = int(enable)
    try:
        from frappe.installer import update_site_config
        update_site_config("maintenance_mode", enable)
        return {
            "success": True,
            "message": _("Maintenance mode {0}").format(_("enabled") if enable else _("disabled"))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_backup_summary(file_name):
    """Returns restore summary metadata for a backup file."""
    _check_access("restore_backup")
    
    # Prevent directory traversal
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        frappe.throw(_("Invalid file name"))
        
    backups_dir = get_site_path("private", "backups")
    file_path = os.path.join(backups_dir, file_name)
    
    if not os.path.exists(file_path):
        frappe.throw(_("Backup file {0} not found.").format(file_name))
        
    stat = os.stat(file_path)
    from smriti_retail_os.backup_api import _format_size
    
    return {
        "filename": file_name,
        "date": now_datetime().fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "size_bytes": stat.st_size,
        "size_formatted": _format_size(stat.st_size),
        "target_site": frappe.local.site
    }

@frappe.whitelist()
def execute_restore(file_name, confirm_text, password):
    """
    Executes database restore with full safeguards:
    1. Pre-restore automatic backup.
    2. Password re-authentication.
    3. Typing confirmation validation.
    4. Activity log creation.
    """
    _check_access("restore_backup")
    
    user = frappe.session.user
    
    # 1. Type confirmation check
    if confirm_text != "RESTORE MY BUSINESS":
        frappe.throw(_("Invalid confirmation text. You must type: RESTORE MY BUSINESS"))
        
    # 2. Password verification
    import frappe.auth
    try:
        frappe.auth.check_password(user, password)
    except frappe.AuthenticationError:
        frappe.throw(_("Invalid password. Re-authentication failed."))
        
    # Prevent directory traversal
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        frappe.throw(_("Invalid file name"))
        
    backups_dir = get_site_path("private", "backups")
    sql_path = os.path.join(backups_dir, file_name)
    if not os.path.exists(sql_path):
        frappe.throw(_("Backup file {0} not found.").format(file_name))
        
    # 3. Create full system backup before restore
    print("[Platform Center] Triggering pre-restore automatic backup...")
    from frappe.utils.backups import new_backup
    pre_backup_path = ""
    try:
        generator = new_backup(with_files=True, force=True)
        generator.get_backup(force=True)
        pre_backup_path = os.path.basename(generator.backup_path_db)
        print(f"[Platform Center] Pre-restore backup created: {pre_backup_path}")
    except Exception as e:
        frappe.log_error(f"Pre-restore Backup Failure: {str(e)}")
        # Log failure in activity log
        frappe.get_doc({
            "doctype": "Activity Log",
            "user": user,
            "operation": "Database Restore",
            "subject": f"Pre-restore backup failed for {file_name}",
            "ip_address": frappe.local.request_ip or "Unknown",
            "status": "Failed",
            "content": f"Failed to create pre-restore backup. Error: {str(e)}"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.throw(_("Restore aborted: Failed to create automatic pre-restore backup. Error: {0}").format(str(e)))

    # Find matching files and private files
    prefix = file_name.split("-")[0]
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
            
    # Retrieve root password
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
        
    success = False
    error_msg = ""
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            success = True
        else:
            error_msg = res.stderr or res.stdout or "Restoration process failed."
    except Exception as e:
        error_msg = str(e)
        
    # Write audit log entry
    frappe.get_doc({
        "doctype": "Activity Log",
        "user": user,
        "operation": "Database Restore",
        "subject": f"Database restore of {file_name}",
        "ip_address": frappe.local.request_ip or "Unknown",
        "status": "Success" if success else "Failed",
        "content": f"Backup Restored: {file_name}\nPre-restore Backup: {pre_backup_path}\nResult Status: {'Success' if success else 'Failed'}\nError: {error_msg}"
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    
    if not success:
        return {
            "success": False,
            "error": error_msg
        }
        
    return {
        "success": True,
        "message": _("Backup restored successfully. Please reload/log in again."),
        "pre_backup": pre_backup_path
    }
