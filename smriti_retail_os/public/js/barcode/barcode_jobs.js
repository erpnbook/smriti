/**
 * @file: smriti_retail_os/public/js/barcode/barcode_jobs.js
 * @description: WebSocket state updates, job retry handler, and polling listener.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

function initRealtime() {
    if (typeof io !== 'undefined') {
        try {
            window.BarcodeStudioState.socket = io();
            const socket = window.BarcodeStudioState.socket;
            socket.on('connect', () => {
                socket.emit('subscribe_user');
            });
            socket.on('smriti.barcode.print_status', (data) => {
                if (data && data.event_version === 1) {
                    refreshPrintJobsDashboard();
                    if (data.status === 'Success') {
                        toast(`Print job ${data.job_id} successfully sent to printer!`, 'success');
                    } else if (data.status === 'Failed') {
                        toast(`Print job ${data.job_id} failed to print.`, 'error');
                    }
                    BarcodeEvents.emit(BarcodeEvents.JOB_STATUS_CHANGED, data);
                }
            });
        } catch (e) {
            console.error("Socket.io initialization failed:", e);
        }
    }
}

function pollPrintJobStatus(jobId, attemptsLeft = 15) {
    if (attemptsLeft <= 0) {
        toast(`Print job ${jobId} status polling timed out. Check dashboard queue.`, 'info');
        return;
    }
    setTimeout(async () => {
        try {
            const res = await api('smriti_retail_os.barcode_api.get_print_job_status', { job_id: jobId });
            if (res && res.status) {
                refreshPrintJobsDashboard();
                if (res.status === 'Success') {
                    toast(`Print job ${jobId} successfully sent to printer!`, 'success');
                } else if (res.status === 'Failed') {
                    toast(`Print job ${jobId} failed to print.`, 'error');
                } else {
                    pollPrintJobStatus(jobId, attemptsLeft - 1);
                }
                BarcodeEvents.emit(BarcodeEvents.JOB_STATUS_CHANGED, res);
            }
        } catch (err) {
            console.error("Error polling print job status", err);
            pollPrintJobStatus(jobId, attemptsLeft - 1);
        }
    }, 2000);
}

async function refreshPrintJobsDashboard() {
    try {
        const jobs = await api('smriti_retail_os.barcode_api.get_recent_print_jobs', { limit: 20 });
        const listContainer = document.getElementById('dashboard-queue-list');
        if (!listContainer) return;
        
        if (!jobs || jobs.length === 0) {
            listContainer.innerHTML = '<div style="color:var(--text-sub); text-align:center; padding: 10px;">No recent jobs</div>';
            return;
        }
        
        listContainer.innerHTML = jobs.map(j => {
            let badgeColor = 'var(--text-muted)';
            if (j.status === 'Queued') badgeColor = 'var(--accent)';
            else if (j.status === 'Sending') badgeColor = 'var(--primary-lt)';
            else if (j.status === 'Success') badgeColor = 'var(--success)';
            else if (j.status === 'Failed') badgeColor = 'var(--danger)';
            
            const showRetry = j.status === 'Failed';
            const actionBtn = showRetry 
                ? `<button class="topbtn" onclick="triggerRetryPrintJob('${j.job_id}')" style="padding: 2px 6px; font-size: 10px; margin-left: auto; border-color: var(--danger); color: var(--danger);"><span class="material-symbols-outlined" style="font-size: 12px;">replay</span> Retry</button>` 
                : (j.status === 'Success' 
                   ? `<span style="font-size: 10px; color: var(--text-muted); margin-left: auto; font-style: italic;">Success</span>` 
                   : `<span style="font-size: 10px; color: var(--text-muted); margin-left: auto; font-style: italic;">Processing</span>`);

            return `
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 6px; font-size: 0.8rem; gap: 6px;">
                    <div style="display: flex; flex-direction: column; gap: 2px; width: 60%;">
                        <div style="font-weight: 600; font-family: 'JetBrains Mono', monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${j.job_id}</div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${j.template_name || 'Built-in Default'} (${j.labels_count} qty)</div>
                    </div>
                    <span style="display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; background: rgba(255,255,255,0.05); color: ${badgeColor}; border: 1px solid ${badgeColor}40;">${j.status}</span>
                    ${actionBtn}
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error("Error refreshing print queue dashboard", err);
    }
}

async function triggerRetryPrintJob(jobId) {
    try {
        toast(`Retrying print job ${jobId}...`, 'info');
        const res = await api('smriti_retail_os.barcode_api.retry_print_job', { job_id: jobId });
        if (res && res.job_id) {
            toast(`New print job enqueued: ${res.job_id}`, 'success');
            pollPrintJobStatus(res.job_id);
            refreshPrintJobsDashboard();
        }
    } catch (err) {
        toast(`Retry failed: ${err.message || err}`, 'error');
    }
}
