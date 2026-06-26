/**
 * SMRITI Status Sentinel Client Controller
 * Project: SMRITI Retail OS
 * Copyright (c) AITDL
 */
(function() {
    'use strict';

    const CONFIG = {
        sentinelPath: '/status/status_sentinel.json',
        healthCheckPath: '/',
        pollInterval: 3000,
        redirectDelay: 1000
    };

    function checkSystemStatus() {
        // 1. Try to read S3 Status Sentinel
        fetch(CONFIG.sentinelPath)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Sentinel file not available');
                }
                return response.json();
            })
            .then(data => {
                updateUI(data);
                if (data.system_status === 'online') {
                    triggerRedirect();
                }
            })
            .catch(error => {
                // Rule 4: Fail-Safe degradation. If status.json fails, fallback to simple backend poll.
                console.warn('S³ Sentinel unavailable, degrading to standard healthcheck:', error.message);
                fallbackHealthcheck();
            });
    }

    function fallbackHealthcheck() {
        // Try to hit the root path directly to check if backend is back up
        fetch(CONFIG.healthCheckPath, { method: 'HEAD', cache: 'no-store' })
            .then(response => {
                // If it resolves with 200/302, Gunicorn is back online
                if (response.status >= 200 && response.status < 400) {
                    triggerRedirect();
                }
            })
            .catch(() => {
                // Backend still offline, do nothing and wait for next poll
            });
    }

    function updateUI(data) {
        // If data indicates migration operations are active
        const ops = data.operations || {};
        const migration = ops.migration || {};
        
        const progContainer = document.getElementById('progress-container');
        const progBar = document.getElementById('progress-bar');
        const progLabel = document.getElementById('progress-label');
        
        if (migration.active) {
            if (progContainer) progContainer.style.display = 'block';
            if (progLabel) {
                progLabel.style.display = 'block';
                progLabel.innerText = migration.current_step || 'Updating schemas...';
            }
            if (progBar) {
                const pct = migration.progress_pct || 0;
                progBar.style.width = pct + '%';
            }
        } else {
            if (progContainer) progContainer.style.display = 'none';
            if (progLabel) progLabel.style.display = 'none';
        }
    }

    let isRedirecting = false;
    function triggerRedirect() {
        if (isRedirecting) return;
        isRedirecting = true;
        
        // Show success / recovery screen or redirect immediately
        console.log('SMRITI is online! Redirecting...');
        setTimeout(() => {
            // Redirect back to root or billing context safely
            window.location.href = '/';
        }, CONFIG.redirectDelay);
    }

    // Initialize polling
    function init() {
        checkSystemStatus();
        setInterval(checkSystemStatus, CONFIG.pollInterval);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
