/**
 * @file: smriti_retail_os/public/js/smriti_backup.js
 * @description: Interactive backup & restore panel with confirmation flow.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

frappe.pages['smriti-backup'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Backup & Restore Center'),
        single_column: true
    });
    new SmritiBackupController(wrapper, page);
};

class SmritiBackupController {
    constructor(wrapper, page) {
        this.wrapper = wrapper;
        this.page = page;
        this.settings = {};
        this.init();
    }

    async init() {
        this.setup_styles();
        this.render_layout();
        this.bind_events();
        await this.load_data();
    }

    setup_styles() {
        if (!document.getElementById("smriti-backup-styles")) {
            var link = document.createElement("link");
            link.id = "smriti-backup-styles";
            link.rel = "stylesheet";
            link.href = "/assets/smriti_retail_os/css/smriti_sidebar.css"; // loads standard stylesheets
            document.head.appendChild(link);
        }
        
        // Dynamically load custom backup CSS
        if (!document.getElementById("smriti-backup-page-styles")) {
            var link = document.createElement("link");
            link.id = "smriti-backup-page-styles";
            link.rel = "stylesheet";
            link.href = "/assets/smriti_retail_os/css/smriti-backup.css";
            document.head.appendChild(link);
        }
    }

    render_layout() {
        const html = `
<div class="sbc-container">
    <!-- Stat Cards -->
    <div class="sbc-stats-grid">
        <div class="sbc-stat-card">
            <div class="stat-icon">🗄️</div>
            <div class="stat-info">
                <span class="stat-label">Total Backups</span>
                <span class="stat-value" id="sbc-stat-count">0</span>
            </div>
        </div>
        <div class="sbc-stat-card">
            <div class="stat-icon">💾</div>
            <div class="stat-info">
                <span class="stat-label">Used Storage</span>
                <span class="stat-value" id="sbc-stat-size">0 KB</span>
            </div>
        </div>
        <div class="sbc-stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-info">
                <span class="stat-label">Last Database Backup</span>
                <span class="stat-value" id="sbc-stat-date">Never</span>
            </div>
        </div>
    </div>

    <!-- Main Settings & Triggers -->
    <div class="sbc-main-layout">
        <!-- Settings Column -->
        <div class="sbc-settings-panel">
            <h2>⚙️ Backup Configuration</h2>
            <form id="sbc-settings-form">
                <!-- Local Backups -->
                <div class="form-section">
                    <h3>📁 Local Backup Storage</h3>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="sbc-enable-local" name="enable_local_backup" checked>
                            Enable Local Storage
                        </label>
                    </div>
                    <div class="form-group inline-group">
                        <label for="sbc-retention">Retention Limit (Days)</label>
                        <input type="number" id="sbc-retention" name="local_retention_days" min="1" max="365" value="30">
                    </div>
                </div>

                <!-- Email SMTP Backups -->
                <div class="form-section">
                    <h3>✉️ Email (Online) Backups</h3>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="sbc-enable-email" name="enable_email_backup">
                            Enable Email Backups
                        </label>
                    </div>
                    <div class="email-smtp-fields hidden">
                        <div class="form-group">
                            <label for="sbc-recipient">Recipient Email</label>
                            <input type="email" id="sbc-recipient" name="email_recipient" placeholder="backup@yourdomain.com">
                        </div>
                        <div class="form-group">
                            <label for="sbc-host">SMTP Host</label>
                            <input type="text" id="sbc-host" name="smtp_host" placeholder="smtp.gmail.com">
                        </div>
                        <div class="form-group inline-group">
                            <label for="sbc-port">SMTP Port</label>
                            <input type="number" id="sbc-port" name="smtp_port" value="587">
                        </div>
                        <div class="form-group">
                            <label for="sbc-user">SMTP Username</label>
                            <input type="text" id="sbc-user" name="smtp_user" placeholder="SMTP Username">
                        </div>
                        <div class="form-group">
                            <label for="sbc-pass">SMTP Password</label>
                            <input type="password" id="sbc-pass" name="smtp_password" placeholder="••••••••••••">
                        </div>
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="sbc-tls" name="use_tls" checked>
                                Use SSL/TLS Secure Port
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Auto Schedule -->
                <div class="form-section">
                    <h3>📅 Automated Schedule</h3>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="sbc-enable-auto" name="enable_auto_backup" checked>
                            Enable Automated Backups
                        </label>
                    </div>
                    <div class="schedule-fields">
                        <div class="form-group">
                            <label for="sbc-frequency">Backup Frequency</label>
                            <select id="sbc-frequency" name="auto_backup_frequency">
                                <option value="Daily">Daily (Every night at 2:00 AM)</option>
                                <option value="Weekly">Weekly (Every Sunday)</option>
                                <option value="Monthly">Monthly (1st of every Month)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="sbc-backup-type">Scheduled Backup Content</label>
                            <select id="sbc-backup-type" name="backup_type">
                                <option value="Database Only">Database Only</option>
                                <option value="Database & Files">Database & File Folders</option>
                            </select>
                        </div>
                    </div>
                </div>

                <button type="submit" class="sbc-btn sbc-btn-primary" id="sbc-save-settings">💾 Save Configuration</button>
            </form>
        </div>

        <!-- Trigger Column -->
        <div class="sbc-trigger-panel">
            <h2>🚀 Manual Backups</h2>
            <p class="panel-hint">Perform immediate manual database or full site backups. Manual backups will be saved locally, and emailed if SMTP is enabled.</p>
            
            <div class="trigger-buttons">
                <button class="sbc-btn sbc-btn-ghost btn-manual-backup" data-type="Database Only">
                    🗄️ Backup Database Only
                </button>
                <button class="sbc-btn sbc-btn-ghost btn-manual-backup" data-type="Database & Files">
                    📦 Backup Database & Files
                </button>
            </div>

            <!-- Log Console -->
            <div class="sbc-console-wrapper hidden">
                <div class="console-header">
                    <span>⚙️ Execution Output</span>
                    <span class="console-dot-loader"></span>
                </div>
                <div class="console-log" id="sbc-console-log">
                    Initializing backup generator...
                </div>
            </div>
        </div>
    </div>

    <!-- Backup History -->
    <div class="sbc-history-panel">
        <h2>📜 Backup Archives</h2>
        <div class="sbc-table-wrapper">
            <table class="sbc-table">
                <thead>
                    <tr>
                        <th>Archive File Name</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Creation Date</th>
                        <th class="text-right">Actions</th>
                    </tr>
                </thead>
                <tbody id="sbc-history-tbody">
                    <tr>
                        <td colspan="5" class="sbc-empty-state">Loading archives...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
`;
        $(this.wrapper).find('.layout-main-section').html(html);
    }

    bind_events() {
        const self = this;

        // Toggle SMTP fields based on Enable checkbox
        $(this.wrapper).on('change', '#sbc-enable-email', function() {
            if ($(this).is(':checked')) {
                $('.email-smtp-fields').removeClass('hidden');
            } else {
                $('.email-smtp-fields').addClass('hidden');
            }
        });

        // Save settings form submission
        $(this.wrapper).on('submit', '#sbc-settings-form', async function(e) {
            e.preventDefault();
            const $btn = $('#sbc-save-settings');
            $btn.prop('disabled', true).text('Saving...');

            // Build settings dictionary
            const settings = {};
            $(this).serializeArray().forEach(item => {
                settings[item.name] = item.value;
            });
            // Handle checkboxes explicitly
            settings['enable_local_backup'] = $('#sbc-enable-local').is(':checked') ? 1 : 0;
            settings['enable_email_backup'] = $('#sbc-enable-email').is(':checked') ? 1 : 0;
            settings['use_tls'] = $('#sbc-tls').is(':checked') ? 1 : 0;
            settings['enable_auto_backup'] = $('#sbc-enable-auto').is(':checked') ? 1 : 0;

            try {
                const res = await frappe.call({
                    method: 'smriti_retail_os.backup_api.save_settings',
                    args: { settings: settings }
                });
                frappe.show_alert({ message: __('Settings saved successfully'), indicator: 'green' });
            } catch (err) {
                frappe.msgprint(__('Error saving settings: ') + (err.message || err));
            } finally {
                $btn.prop('disabled', false).text('💾 Save Configuration');
            }
        });

        // Trigger manual backups
        $(this.wrapper).on('click', '.btn-manual-backup', function() {
            const backupType = $(this).data('type');
            self.trigger_backup(backupType);
        });

        // Download Backup button click
        $(this.wrapper).on('click', '.btn-sbc-download', function() {
            const fileName = $(this).data('name');
            // Frappe downloads private files relative to site root via site path wrapper
            const downloadUrl = `/backups/${fileName}`;
            window.open(downloadUrl, '_blank');
        });

        // Delete Backup button click
        $(this.wrapper).on('click', '.btn-sbc-delete', function() {
            const fileName = $(this).data('name');
            frappe.confirm(__('Are you sure you want to permanently delete the backup file {0}?', [fileName]), async () => {
                try {
                    await frappe.call({
                        method: 'smriti_retail_os.backup_api.delete_backup',
                        args: { file_name: fileName }
                    });
                    frappe.show_alert({ message: __('Backup deleted'), indicator: 'red' });
                    await self.load_data();
                } catch (err) {
                    frappe.msgprint(__('Error deleting backup: ') + (err.message || err));
                }
            });
        });

        // One-Click Restore button click
        $(this.wrapper).on('click', '.btn-sbc-restore', function() {
            const fileName = $(this).data('name');
            self.confirm_and_restore(fileName);
        });
    }

    async load_data() {
        const self = this;
        try {
            // 1. Fetch settings
            const settings_res = await frappe.call({
                method: 'smriti_retail_os.backup_api.get_settings'
            });
            this.settings = settings_res.message || DEFAULT_SETTINGS;
            this.populate_settings();

            // 2. Fetch stats
            const stats_res = await frappe.call({
                method: 'smriti_retail_os.backup_api.get_backup_status'
            });
            const stats = stats_res.message || {};
            $('#sbc-stat-count').text(stats.total_count || 0);
            $('#sbc-stat-size').text(stats.total_size || '0 KB');
            $('#sbc-stat-date').text(stats.last_backup_date || 'Never');

            // 3. Fetch history
            const history_res = await frappe.call({
                method: 'smriti_retail_os.backup_api.get_backup_history'
            });
            this.populate_history(history_res.message || []);

        } catch (err) {
            console.error("Error loading backup center data:", err);
        }
    }

    populate_settings() {
        $('#sbc-enable-local').prop('checked', !!this.settings.enable_local_backup);
        $('#sbc-retention').val(this.settings.local_retention_days || 30);
        $('#sbc-enable-email').prop('checked', !!this.settings.enable_email_backup).trigger('change');
        $('#sbc-recipient').val(this.settings.email_recipient || '');
        $('#sbc-host').val(this.settings.smtp_host || '');
        $('#sbc-port').val(this.settings.smtp_port || 587);
        $('#sbc-user').val(this.settings.smtp_user || '');
        $('#sbc-pass').val(this.settings.smtp_password ? '••••••••••••' : '');
        $('#sbc-tls').prop('checked', !!this.settings.use_tls);
        $('#sbc-enable-auto').prop('checked', !!this.settings.enable_auto_backup);
        $('#sbc-frequency').val(this.settings.auto_backup_frequency || 'Daily');
        $('#sbc-backup-type').val(this.settings.backup_type || 'Database Only');
    }

    populate_history(archives) {
        const $tbody = $('#sbc-history-tbody');
        $tbody.empty();

        if (!archives.length) {
            $tbody.html(`
                <tr>
                    <td colspan="5" class="sbc-empty-state">
                        📁 No backup archives found on this site. Trigger a manual backup to start.
                    </td>
                </tr>
            `);
            return;
        }

        archives.forEach(item => {
            let badgeClass = 'badge-other';
            let badgeIcon = '📄';
            if (item.type === 'database') { badgeClass = 'badge-db'; badgeIcon = '🗄️'; }
            else if (item.type === 'files') { badgeClass = 'badge-files'; badgeIcon = '📂'; }
            else if (item.type === 'private-files') { badgeClass = 'badge-private-files'; badgeIcon = '🔒'; }
            else if (item.type === 'config') { badgeClass = 'badge-config'; badgeIcon = '⚙️'; }

            // Restore action button is only visible for Database backups
            const showRestore = item.type === 'database';
            const restoreBtn = showRestore ? `
                <button class="sbc-btn sbc-btn-danger btn-sbc-restore" data-name="${item.name}" title="Restore database from this archive">
                    🔄 Restore
                </button>
            ` : '';

            $tbody.append(`
                <tr>
                    <td class="font-medium sbc-filename" title="${item.name}">${item.name}</td>
                    <td>
                        <span class="sbc-badge ${badgeClass}">${badgeIcon} ${item.type.toUpperCase()}</span>
                    </td>
                    <td>${item.size}</td>
                    <td>${item.datetime}</td>
                    <td class="text-right">
                        <div class="sbc-actions-wrap">
                            <button class="sbc-btn sbc-btn-ghost btn-sbc-download" data-name="${item.name}">
                                ⬇ Download
                            </button>
                            ${restoreBtn}
                            <button class="sbc-btn sbc-btn-danger sbc-btn-danger-ghost btn-sbc-delete" data-name="${item.name}">
                                ✕ Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `);
        });
    }

    async trigger_backup(backupType) {
        const self = this;
        const $console = $('.sbc-console-wrapper');
        const $log = $('#sbc-console-log');
        const $btns = $('.btn-manual-backup');

        $console.removeClass('hidden');
        $btns.prop('disabled', true);
        $log.html(`[${new Date().toLocaleTimeString()}] Starting SMRITI Backup System...\n[${new Date().toLocaleTimeString()}] Content type requested: ${backupType}\n[${new Date().toLocaleTimeString()}] Triggering frappe.utils.backups.BackupGenerator...`);

        try {
            const res = await frappe.call({
                method: 'smriti_retail_os.backup_api.take_backup_now',
                args: { backup_type: backupType }
            });

            const r = res.message || {};
            if (r.status === 'success') {
                $log.append(`\n[${new Date().toLocaleTimeString()}] Success: Backup file created: ${r.file}`);
                if (r.email_sent) {
                    $log.append(`\n[${new Date().toLocaleTimeString()}] Success: Dispatch email succeeded.`);
                } else if (r.email_error) {
                    $log.append(`\n[${new Date().toLocaleTimeString()}] Warning: Email failed to dispatch: ${r.email_error}`);
                }
                $log.append(`\n[${new Date().toLocaleTimeString()}] Operations completed successfully.`);
                frappe.show_alert({ message: __('Manual Backup completed successfully'), indicator: 'green' });
            } else {
                $log.append(`\n[${new Date().toLocaleTimeString()}] Error: Backup failed: ${r.message}`);
                frappe.msgprint(__('Backup execution failed: ') + r.message);
            }
        } catch (err) {
            $log.append(`\n[${new Date().toLocaleTimeString()}] Exception: ${err.message || err}`);
            frappe.msgprint(__('Backup execution failed: ') + (err.message || err));
        } finally {
            $btns.prop('disabled', false);
            $('.console-dot-loader').addClass('hidden');
            await self.load_data();
        }
    }

    confirm_and_restore(fileName) {
        const self = this;
        
        // Step 1: Broad warning confirmation
        frappe.confirm(
            __('⚠️ CRITICAL WARNING:<br><br>You are about to restore the database to backup: <b>{0}</b>.<br><br><b>THIS OPERATION IS COMPLETELY DESTRUCTIVE.</b> It will overwrite all current sales, billing transactions, inventory quantities, and ledger entries.<br><br>Are you absolutely sure you want to proceed?', [fileName]),
            () => {
                // Step 2: Input check verification guard
                const d = new frappe.ui.Dialog({
                    title: __('Intention Verification Guard'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'warning_html',
                            options: `<p style="color:var(--text-color);margin-bottom:14px;">Please type <b>RESTORE</b> in uppercase to authorize database overwriting.</p>`
                        },
                        {
                            fieldtype: 'Data',
                            fieldname: 'confirm_text',
                            label: __('Verification Input'),
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Execute Restore'),
                    primary_action: async function(values) {
                        if (String(values.confirm_text).trim() !== 'RESTORE') {
                            frappe.msgprint(__('Verification failed. You must type RESTORE to proceed.'));
                            return;
                        }
                        d.hide();
                        self.execute_restore(fileName);
                    }
                });
                d.show();
            }
        );
    }

    async execute_restore(fileName) {
        // Show progress overlay modal
        const dialog = new frappe.ui.Dialog({
            title: __('Restoring Database'),
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'progress_html',
                    options: `
                        <div style="text-align:center;padding:24px 12px;">
                            <div class="sbc-spinner" style="margin: 0 auto 16px;"></div>
                            <h4 style="margin:0 0 8px;">Restoring files and database tables...</h4>
                            <p style="color:var(--text-muted);font-size:12px;margin:0;">Do not close or reload this window. Dropping existing tables and rebuilding system...</p>
                        </div>
                    `
                }
            ]
        });
        dialog.show();

        try {
            const res = await frappe.call({
                method: 'smriti_retail_os.backup_api.restore_backup',
                args: { file_name: fileName },
                timeout: 300000 // 5 minutes timeout for large restores
            });

            const r = res.message || {};
            dialog.hide();

            if (r.status === 'success') {
                frappe.msgprint({
                    title: __('Success'),
                    indicator: 'green',
                    message: __('Backup restored successfully. The system will now log you out to refresh your active session database.'),
                    primary_action: {
                        label: __('OK'),
                        action: function() {
                            frappe.app.logout();
                        }
                    }
                });
                // Fallback auto-logout after 5 seconds
                setTimeout(() => {
                    frappe.app.logout();
                }, 5000);
            } else {
                frappe.msgprint({
                    title: __('Restoration Failed'),
                    indicator: 'red',
                    message: __('Error during restore process: <br><pre>{0}</pre>', [r.message])
                });
            }
        } catch (err) {
            dialog.hide();
            frappe.msgprint({
                title: __('Restoration Exception'),
                indicator: 'red',
                message: __('An unexpected exception occurred during restore: <br><pre>{0}</pre>', [err.message || err])
            });
        }
    }
}
