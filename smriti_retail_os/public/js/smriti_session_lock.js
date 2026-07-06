/**
 * @file: smriti_retail_os/public/js/smriti_session_lock.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.8.6
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

const SmritiSessionLock = (() => {
    // ── Config ────────────────────────────────────────────────────────────────
    const DEFAULT_IDLE_MINUTES = 5;
    const ACTIVITY_EVENTS      = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'click'];
    const OVERLAY_ID           = 'smriti-session-lock-overlay';
    const TIMER_ID             = 'smriti-session-lock-timer';

    let _idleMs       = DEFAULT_IDLE_MINUTES * 60 * 1000;
    let _timer        = null;
    let _locked       = false;
    let _lockedAt     = null;
    let _user         = null;
    let _clockTimer   = null;
    let _failCount    = 0;
    const MAX_FAILS   = 5;

    // ── Idle timer reset ──────────────────────────────────────────────────────
    function _resetTimer() {
        if (_locked) return;
        clearTimeout(_timer);
        _timer = setTimeout(_lock, _idleMs);
    }

    function _bindActivity() {
        ACTIVITY_EVENTS.forEach(ev => document.addEventListener(ev, _resetTimer, { passive: true }));
    }

    function _unbindActivity() {
        ACTIVITY_EVENTS.forEach(ev => document.removeEventListener(ev, _resetTimer));
    }

    // ── Lock ──────────────────────────────────────────────────────────────────
    function _lock() {
        if (_locked) return;
        _locked    = true;
        _lockedAt  = new Date();
        _failCount = 0;
        _unbindActivity();
        clearTimeout(_timer);
        _renderOverlay();
        console.info('[SMRITI Lock] Terminal locked due to inactivity.');
    }

    // ── Unlock ────────────────────────────────────────────────────────────────
    function _unlock() {
        _locked = false;
        _failCount = 0;
        const overlay = document.getElementById(OVERLAY_ID);
        if (overlay) {
            overlay.classList.add('sl-fade-out');
            setTimeout(() => overlay?.remove(), 300);
        }
        clearInterval(_clockTimer);
        _bindActivity();
        _resetTimer();
        console.info('[SMRITI Lock] Terminal unlocked.');
    }

    // ── API helper — works on both Frappe desk and standalone www pages ─────────
    function _getCsrf() {
        // Try frappe object first, then meta tag, then global var, then cookie
        if (typeof frappe !== 'undefined' && frappe.csrf_token) return frappe.csrf_token;
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.content;
        if (typeof csrf_token !== 'undefined') return csrf_token;
        const m = document.cookie.match(/csrf_token=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : 'no-csrf';
    }

    async function _apiPost(method, args = {}) {
        const csrf = _getCsrf();
        const r = await fetch('/api/method/' + method, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json', 'x-frappe-csrf-token': csrf },
            body: JSON.stringify(args)
        });
        return r.json();
    }

    // ── API calls ─────────────────────────────────────────────────────────────
    async function _verifyPassword(password) {
        try {
            const d = await _apiPost('smriti_retail_os.security_api.verify_user_password', { password });
            return d.message && d.message.success === true;
        } catch (e) {
            return false;
        }
    }

    async function _verifyManagerPin(manager_user, pin) {
        try {
            const d = await _apiPost('smriti_retail_os.security_api.validate_manager_override', {
                manager_user, pin, action: 'Session Unlock Override'
            });
            return d.message && d.message.success === true;
        } catch (e) {
            return false;
        }
    }

    // ── Overlay renderer ──────────────────────────────────────────────────────
    function _renderOverlay() {
        document.getElementById(OVERLAY_ID)?.remove();

        const frappeUser = (typeof frappe !== 'undefined' && frappe.session?.user) ? frappe.session.user : '';
        const userDisplay = (_user || frappeUser || 'Cashier').split('@')[0];
        const initials    = userDisplay.substring(0, 2).toUpperCase();

        const overlay = document.createElement('div');
        overlay.id    = OVERLAY_ID;
        overlay.innerHTML = `
<style>
#${OVERLAY_ID} {
    position: fixed; inset: 0; z-index: 99999;
    background: linear-gradient(135deg, #0A1628 0%, #0F2044 40%, #0A1628 100%);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-family: 'Inter', Arial, sans-serif;
    animation: sl-fade-in .3s ease;
}
#${OVERLAY_ID}.sl-fade-out { animation: sl-fade-out .3s ease forwards; }
@keyframes sl-fade-in  { from { opacity: 0; transform: scale(1.02); } to { opacity: 1; transform: scale(1); } }
@keyframes sl-fade-out { from { opacity: 1; } to { opacity: 0; } }

.sl-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 40px; opacity: .7; }
.sl-brand-dot { width: 10px; height: 10px; border-radius: 50%; background: #2563EB; }
.sl-brand-name { color: #94A3B8; font-size: .85rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; }

.sl-lock-icon {
    width: 72px; height: 72px; border-radius: 50%;
    background: rgba(239,68,68,.12); border: 2px solid rgba(239,68,68,.3);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 20px;
    animation: sl-pulse 2.5s ease-in-out infinite;
}
@keyframes sl-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,.3); }
    50% { box-shadow: 0 0 0 14px rgba(239,68,68,0); }
}
.sl-lock-icon svg { width: 32px; height: 32px; fill: #EF4444; }

.sl-title { color: #F1F5F9; font-size: 1.4rem; font-weight: 700; margin-bottom: 6px; }
.sl-subtitle { color: #64748B; font-size: .875rem; margin-bottom: 32px; }

.sl-avatar {
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, #1A2B5C, #2563EB);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 1.1rem; font-weight: 700;
    margin-bottom: 8px;
}
.sl-user-name { color: #94A3B8; font-size: .85rem; margin-bottom: 28px; }

.sl-card {
    background: rgba(30,41,59,.8);
    border: 1px solid rgba(45,63,94,.8);
    border-radius: 16px;
    padding: 28px 32px;
    width: 360px;
    backdrop-filter: blur(12px);
}
.sl-tabs { display: flex; border-bottom: 1px solid rgba(255,255,255,.07); margin-bottom: 20px; }
.sl-tab {
    flex: 1; padding: 8px; text-align: center;
    color: #64748B; font-size: .8rem; font-weight: 500; cursor: pointer;
    border-bottom: 2px solid transparent; transition: all .2s;
}
.sl-tab.active { color: #3B82F6; border-bottom-color: #2563EB; }

.sl-input-wrap { position: relative; margin-bottom: 16px; }
.sl-input {
    width: 100%; padding: 11px 40px 11px 14px;
    background: rgba(15,23,42,.6); border: 1px solid rgba(45,63,94,.8);
    border-radius: 8px; color: #F1F5F9; font-size: .9rem; font-family: inherit;
    outline: none; transition: border .2s;
}
.sl-input:focus { border-color: #2563EB; }
.sl-input.error { border-color: #EF4444; animation: sl-shake .3s ease; }
@keyframes sl-shake {
    0%,100% { transform: translateX(0); }
    25% { transform: translateX(-6px); }
    75% { transform: translateX(6px); }
}
.sl-eye {
    position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
    color: #64748B; cursor: pointer; font-size: 16px;
    font-family: 'Material Symbols Outlined', sans-serif;
}
.sl-select {
    width: 100%; padding: 10px 14px; margin-bottom: 12px;
    background: rgba(15,23,42,.6); border: 1px solid rgba(45,63,94,.8);
    border-radius: 8px; color: #F1F5F9; font-size: .85rem; font-family: inherit;
    outline: none;
}

.sl-btn {
    width: 100%; padding: 12px;
    background: linear-gradient(135deg, #1D4ED8, #2563EB);
    border: none; border-radius: 8px;
    color: #fff; font-size: .9rem; font-weight: 600; font-family: inherit;
    cursor: pointer; transition: opacity .2s;
    display: flex; align-items: center; justify-content: center; gap: 8px;
}
.sl-btn:hover { opacity: .9; }
.sl-btn:disabled { opacity: .5; cursor: not-allowed; }

.sl-err { color: #F87171; font-size: .78rem; text-align: center; margin-top: 10px; min-height: 18px; }
.sl-locked-time { color: #475569; font-size: .75rem; text-align: center; margin-top: 20px; }
.sl-clock { color: #334155; font-size: .75rem; text-align: center; margin-top: 6px; }
.sl-loading { display: inline-block; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,.3); border-top-color: #fff; border-radius: 50%; animation: sl-spin .6s linear infinite; }
@keyframes sl-spin { to { transform: rotate(360deg); } }
</style>

<div class="sl-brand">
    <div class="sl-brand-dot"></div>
    <div class="sl-brand-name">SMRITI Retail OS</div>
</div>

<div class="sl-lock-icon">
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
    </svg>
</div>

<div class="sl-title">Terminal Locked</div>
<div class="sl-subtitle">Enter your credentials to continue</div>

<div class="sl-avatar" id="sl-avatar">${initials}</div>
<div class="sl-user-name">${userDisplay}</div>

<div class="sl-card">
    <div class="sl-tabs">
        <div class="sl-tab active" id="sl-tab-pw" onclick="SmritiSessionLock._switchTab('pw')">🔑 Password</div>
        <div class="sl-tab" id="sl-tab-pin" onclick="SmritiSessionLock._switchTab('pin')">🔢 Manager PIN</div>
    </div>

    <!-- Password tab -->
    <div id="sl-pane-pw">
        <div class="sl-input-wrap">
            <input class="sl-input" type="password" id="sl-pw-input" placeholder="Enter your login password" autocomplete="current-password">
            <span class="sl-eye" id="sl-pw-eye" onclick="SmritiSessionLock._toggleEye('sl-pw-input','sl-pw-eye')">visibility_off</span>
        </div>
        <button class="sl-btn" id="sl-pw-btn" onclick="SmritiSessionLock._submitPassword()">
            Unlock
        </button>
    </div>

    <!-- Manager PIN tab -->
    <div id="sl-pane-pin" style="display:none">
        <select class="sl-select" id="sl-mgr-select">
            <option value="">— Select Manager —</option>
        </select>
        <div class="sl-input-wrap">
            <input class="sl-input" type="password" id="sl-pin-input" placeholder="Manager POS PIN (4–6 digits)" maxlength="6" inputmode="numeric" pattern="[0-9]*">
            <span class="sl-eye" id="sl-pin-eye" onclick="SmritiSessionLock._toggleEye('sl-pin-input','sl-pin-eye')">visibility_off</span>
        </div>
        <button class="sl-btn" id="sl-pin-btn" onclick="SmritiSessionLock._submitPin()">
            Override Unlock
        </button>
    </div>

    <div class="sl-err" id="sl-err"></div>
</div>

<div class="sl-locked-time" id="sl-locked-time">Locked at ${_lockedAt?.toLocaleTimeString()}</div>
<div class="sl-clock" id="${TIMER_ID}"></div>
`;
        document.body.appendChild(overlay);

        // Focus pw input
        setTimeout(() => document.getElementById('sl-pw-input')?.focus(), 100);

        // Enter key submit
        document.getElementById('sl-pw-input')?.addEventListener('keydown', e => {
            if (e.key === 'Enter') SmritiSessionLock._submitPassword();
        });
        document.getElementById('sl-pin-input')?.addEventListener('keydown', e => {
            if (e.key === 'Enter') SmritiSessionLock._submitPin();
        });

        // Load managers
        _loadManagers();

        // Live clock
        _clockTimer = setInterval(() => {
            const el = document.getElementById(TIMER_ID);
            if (el && _lockedAt) {
                const secs = Math.floor((Date.now() - _lockedAt.getTime()) / 1000);
                const mm   = String(Math.floor(secs / 60)).padStart(2, '0');
                const ss   = String(secs % 60).padStart(2, '0');
                el.textContent = `Idle for ${mm}:${ss}`;
            }
        }, 1000);
    }

    async function _loadManagers() {
        try {
            const d = await _apiPost('smriti_retail_os.security_api.get_managers_list');
            const select = document.getElementById('sl-mgr-select');
            if (select && d.message && d.message.length) {
                d.message.forEach(m => {
                    const opt  = document.createElement('option');
                    opt.value  = m.name;
                    opt.textContent = (m.full_name || m.name) + ' (' + m.name + ')';
                    select.appendChild(opt);
                });
            }
        } catch(e) {}
    }

    // ── Tab switch ────────────────────────────────────────────────────────────
    function _switchTab(tab) {
        document.getElementById('sl-pane-pw').style.display  = tab === 'pw'  ? '' : 'none';
        document.getElementById('sl-pane-pin').style.display = tab === 'pin' ? '' : 'none';
        document.getElementById('sl-tab-pw').className  = 'sl-tab' + (tab === 'pw'  ? ' active' : '');
        document.getElementById('sl-tab-pin').className = 'sl-tab' + (tab === 'pin' ? ' active' : '');
        document.getElementById('sl-err').textContent   = '';
        setTimeout(() => {
            (tab === 'pw'
                ? document.getElementById('sl-pw-input')
                : document.getElementById('sl-pin-input'))?.focus();
        }, 50);
    }

    // ── Eye toggle ────────────────────────────────────────────────────────────
    function _toggleEye(inputId, eyeId) {
        const inp = document.getElementById(inputId);
        const eye = document.getElementById(eyeId);
        if (!inp || !eye) return;
        inp.type = inp.type === 'password' ? 'text' : 'password';
        eye.textContent = inp.type === 'password' ? 'visibility_off' : 'visibility';
    }

    // ── Submit password ───────────────────────────────────────────────────────
    async function _submitPassword() {
        const inp = document.getElementById('sl-pw-input');
        const btn = document.getElementById('sl-pw-btn');
        const err = document.getElementById('sl-err');
        if (!inp || !btn) return;

        const pw = inp.value.trim();
        if (!pw) { err.textContent = 'Please enter your password.'; return; }

        btn.disabled = true;
        btn.innerHTML = '<span class="sl-loading"></span>';
        err.textContent = '';

        const ok = await _verifyPassword(pw);
        if (ok) {
            _unlock();
        } else {
            _failCount++;
            inp.value = '';
            inp.classList.add('error');
            setTimeout(() => inp.classList.remove('error'), 400);
            if (_failCount >= MAX_FAILS) {
                err.textContent = `${MAX_FAILS} failed attempts. Use Manager PIN to unlock.`;
                _switchTab('pin');
            } else {
                err.textContent = `Incorrect password. ${MAX_FAILS - _failCount} attempt(s) remaining.`;
            }
            btn.disabled = false;
            btn.innerHTML = 'Unlock';
        }
    }

    // ── Submit manager PIN ────────────────────────────────────────────────────
    async function _submitPin() {
        const sel = document.getElementById('sl-mgr-select');
        const inp = document.getElementById('sl-pin-input');
        const btn = document.getElementById('sl-pin-btn');
        const err = document.getElementById('sl-err');
        if (!inp || !btn || !sel) return;

        const manager = sel.value;
        const pin     = inp.value.trim();

        if (!manager) { err.textContent = 'Please select a manager.'; return; }
        if (!pin || pin.length < 4) { err.textContent = 'PIN must be 4–6 digits.'; return; }

        btn.disabled = true;
        btn.innerHTML = '<span class="sl-loading"></span>';
        err.textContent = '';

        const ok = await _verifyManagerPin(manager, pin);
        if (ok) {
            _unlock();
            // Show alert — works on desk (frappe object) or standalone (console)
            if (typeof frappe !== 'undefined' && frappe.show_alert) {
                frappe.show_alert({ message: `Terminal unlocked by manager: ${manager}`, indicator: 'green' });
            } else {
                console.info('[SMRITI Lock] Unlocked by manager:', manager);
            }
        } else {
            inp.value = '';
            inp.classList.add('error');
            setTimeout(() => inp.classList.remove('error'), 400);
            err.textContent = 'Invalid manager PIN. Please try again.';
            btn.disabled = false;
            btn.innerHTML = 'Override Unlock';
        }
    }

    // ── Public API ────────────────────────────────────────────────────────────
    function init(options = {}) {
        const minutes = options.idleMinutes || DEFAULT_IDLE_MINUTES;
        _idleMs = minutes * 60 * 1000;
        // Safely get user — works on both desk and www pages
        const frappeUser = (typeof frappe !== 'undefined' && frappe.session?.user) ? frappe.session.user : '';
        _user   = options.user || frappeUser;

        _bindActivity();
        _resetTimer();

        console.info(`[SMRITI Lock] Session lock initialized. Idle timeout: ${minutes} min.`);
    }

    function lockNow() { _lock(); }
    function isLocked() { return _locked; }
    function destroy() {
        clearTimeout(_timer);
        clearInterval(_clockTimer);
        _unbindActivity();
        document.getElementById(OVERLAY_ID)?.remove();
        _locked = false;
    }

    return { init, lockNow, isLocked, destroy, _switchTab, _toggleEye, _submitPassword, _submitPin };
})();

// Auto-init on billing pages with 5-min default
if (typeof frappe !== 'undefined' && typeof frappe.ready === 'function') {
    frappe.ready(() => {
        // Only activate on billing/POS pages, not admin pages
        const route = window.location.pathname;
        const isBillingPage = route.includes('/billing') || route.includes('smriti-billing');
        if (isBillingPage) {
            SmritiSessionLock.init({ idleMinutes: 5 });
        }
    });
} else {
    document.addEventListener('DOMContentLoaded', () => {
        const route = window.location.pathname;
        const isBillingPage = route.includes('/billing') || route.includes('smriti-billing');
        if (isBillingPage) {
            SmritiSessionLock.init({ idleMinutes: 5 });
        }
    });
}
