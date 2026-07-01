/**
 * @file: smriti_retail_os/public/js/smriti_print_modal.js
 * @description: SMRITI Print Modal — wraps Frappe /printview inside a branded
 *   fullscreen modal so users never see raw Frappe URLs or UI shell.
 *   Replaces all window.open('/printview?...', '_blank') calls across www pages.
 * @usage: SmritiPrint.open(url [, title])
 * @author: Jawahar R Mallah
 * @version: 1.0.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function (global) {
    'use strict';

    var SmritiPrint = {};

    var MODAL_ID   = 'smriti-print-modal-overlay';
    var IFRAME_ID  = 'smriti-print-modal-iframe';
    var LOADER_ID  = 'smriti-print-modal-loader';

    // ── Inject CSS once ──────────────────────────────────────────────────────
    function _ensureStyles() {
        if (document.getElementById('smriti-print-modal-style')) return;
        var style = document.createElement('style');
        style.id = 'smriti-print-modal-style';
        style.textContent = [
            '#' + MODAL_ID + '{',
            '  position:fixed;inset:0;z-index:99999;display:flex;flex-direction:column;',
            '  background:#0F1929;',
            '}',
            '#smriti-print-modal-header{',
            '  display:flex;align-items:center;gap:14px;',
            '  padding:10px 20px;',
            '  background:linear-gradient(135deg,#1A2B5C 0%,#0F1929 100%);',
            '  border-bottom:1px solid rgba(37,99,235,0.3);',
            '  flex-shrink:0;min-height:52px;',
            '}',
            '#smriti-print-modal-brand{',
            '  display:flex;align-items:center;gap:10px;flex:1;',
            '}',
            '#smriti-print-modal-logo{',
            '  width:28px;height:28px;background:#2563EB;border-radius:6px;',
            '  display:flex;align-items:center;justify-content:center;',
            '  font-weight:800;font-size:11px;color:#fff;letter-spacing:-0.5px;font-family:Arial,sans-serif;',
            '}',
            '#smriti-print-modal-title{',
            '  font-family:Arial,sans-serif;font-size:13px;font-weight:600;',
            '  color:#F1F5F9;letter-spacing:0.2px;',
            '}',
            '#smriti-print-modal-subtitle{',
            '  font-family:Arial,sans-serif;font-size:11px;color:#64748B;margin-left:4px;',
            '}',
            '#smriti-print-modal-actions{display:flex;gap:8px;align-items:center;}',
            '.smriti-pmb{',
            '  display:inline-flex;align-items:center;gap:6px;',
            '  padding:7px 16px;border-radius:6px;font-size:12px;font-weight:600;',
            '  font-family:Arial,sans-serif;cursor:pointer;border:none;',
            '  transition:all 0.15s ease;letter-spacing:0.2px;',
            '}',
            '.smriti-pmb-print{background:#2563EB;color:#fff;}',
            '.smriti-pmb-print:hover{background:#1D4ED8;}',
            '.smriti-pmb-close{background:rgba(255,255,255,0.08);color:#94A3B8;border:1px solid rgba(255,255,255,0.1);}',
            '.smriti-pmb-close:hover{background:rgba(239,68,68,0.15);color:#F87171;border-color:rgba(239,68,68,0.3);}',
            '#' + LOADER_ID + '{',
            '  position:absolute;inset:52px 0 0 0;display:flex;flex-direction:column;',
            '  align-items:center;justify-content:center;background:#0F1929;',
            '  font-family:Arial,sans-serif;color:#64748B;font-size:13px;gap:16px;',
            '}',
            '.smriti-pm-spinner{',
            '  width:32px;height:32px;border:3px solid rgba(37,99,235,0.2);',
            '  border-top-color:#2563EB;border-radius:50%;animation:smriti-spin 0.8s linear infinite;',
            '}',
            '@keyframes smriti-spin{to{transform:rotate(360deg)}}',
            '#' + IFRAME_ID + '{',
            '  flex:1;border:none;background:#fff;',
            '  opacity:0;transition:opacity 0.2s ease;',
            '}',
            '#' + IFRAME_ID + '.loaded{opacity:1;}',
        ].join('\n');
        document.head.appendChild(style);
    }

    // ── Build modal DOM ──────────────────────────────────────────────────────
    function _buildModal(url, title) {
        var overlay = document.createElement('div');
        overlay.id = MODAL_ID;

        // Header
        var header = document.createElement('div');
        header.id = 'smriti-print-modal-header';
        header.innerHTML = [
            '<div id="smriti-print-modal-brand">',
            '  <div id="smriti-print-modal-logo">SR</div>',
            '  <div>',
            '    <span id="smriti-print-modal-title">SMRITI Retail OS</span>',
            '    <span id="smriti-print-modal-subtitle">— ' + (title || 'Print Preview') + '</span>',
            '  </div>',
            '</div>',
            '<div id="smriti-print-modal-actions">',
            '  <button class="smriti-pmb smriti-pmb-print" id="smriti-print-modal-print-btn">',
            '    ⎙&nbsp; Print',
            '  </button>',
            '  <button class="smriti-pmb smriti-pmb-close" id="smriti-print-modal-close-btn">',
            '    ✕&nbsp; Close',
            '  </button>',
            '</div>',
        ].join('');

        // Loader
        var loader = document.createElement('div');
        loader.id = LOADER_ID;
        loader.innerHTML = '<div class="smriti-pm-spinner"></div><div>Preparing document…</div>';

        // Iframe
        var iframe = document.createElement('iframe');
        iframe.id = IFRAME_ID;
        iframe.setAttribute('allowfullscreen', '');
        iframe.setAttribute('loading', 'eager');
        iframe.title = title || 'Print Preview';

        overlay.appendChild(header);
        overlay.appendChild(loader);
        overlay.appendChild(iframe);

        // Events
        document.getElementById('smriti-print-modal-close-btn') || header.querySelector('#smriti-print-modal-close-btn');

        overlay.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') SmritiPrint.close();
        });

        return { overlay: overlay, iframe: iframe, loader: loader, header: header };
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Open a printview URL inside a SMRITI-branded modal.
     * @param {string} url      - The /printview URL (or any printable URL)
     * @param {string} [title]  - Optional document title shown in header
     */
    SmritiPrint.open = function (url, title) {
        // Remove any existing modal
        SmritiPrint.close();

        _ensureStyles();

        var parts = _buildModal(url, title);
        document.body.appendChild(parts.overlay);
        document.body.style.overflow = 'hidden';

        // Wire close button (must be done after appendChild)
        var closeBtn  = parts.overlay.querySelector('#smriti-print-modal-close-btn');
        var printBtn  = parts.overlay.querySelector('#smriti-print-modal-print-btn');

        if (closeBtn) closeBtn.addEventListener('click', SmritiPrint.close);

        // Print — trigger iframe contentWindow.print()
        if (printBtn) {
            printBtn.addEventListener('click', function () {
                var f = document.getElementById(IFRAME_ID);
                if (f && f.contentWindow) {
                    try {
                        f.contentWindow.focus();
                        f.contentWindow.print();
                    } catch (e) {
                        // Cross-origin fallback — open in tab for native browser print
                        window.open(url, '_blank');
                    }
                }
            });
        }

        // Load iframe AFTER modal is in DOM
        parts.iframe.addEventListener('load', function () {
            var loader = document.getElementById(LOADER_ID);
            if (loader) loader.style.display = 'none';
            parts.iframe.classList.add('loaded');
            parts.iframe.focus();
        });

        parts.iframe.src = url;

        // Focus trap
        parts.overlay.setAttribute('tabindex', '-1');
        parts.overlay.focus();
    };

    /**
     * Close the SMRITI print modal if open.
     */
    SmritiPrint.close = function () {
        var el = document.getElementById(MODAL_ID);
        if (el) el.parentNode.removeChild(el);
        document.body.style.overflow = '';
    };

    // ── Export ────────────────────────────────────────────────────────────────
    global.SmritiPrint = SmritiPrint;

}(window));
