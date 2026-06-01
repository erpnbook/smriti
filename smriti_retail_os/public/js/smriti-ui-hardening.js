/**
 * @file smriti-ui-hardening.js
 * @description SMRITI Retail OS — Global UI Hardening Runtime Utilities
 *              Auto-initializes on DOMContentLoaded. Safe to include on all pages.
 *
 * FEATURES:
 *  - SmritiPortal: singleton floating dropdown portal (escapes all overflow contexts)
 *  - SmritiGrid: utilities for grid fixed-height enforcement & scroll-tracking
 *  - SmritiDropdownFix: upgrades any .search-dropdown inside a scroll container
 *
 * @author Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version 1.0.0
 * @license MIT
 */

(function (global) {
  'use strict';

  /* ══════════════════════════════════════════════════════════════════
     SmritiPortal — Singleton floating dropdown portal
     ══════════════════════════════════════════════════════════════════
     Usage (replaces any in-grid absolute-positioned dropdown):

       SmritiPortal.show({
         anchorEl: inputElement,       // Element to position below
         items: [{ label, sublabel, value, data }],
         onSelect: (item) => { ... },
         placeholder: 'No results',   // optional
       });

       SmritiPortal.hide();
  ══════════════════════════════════════════════════════════════════ */
  const SmritiPortal = (function () {
    let _portal = null;
    let _currentAnchor = null;
    let _onSelect = null;
    let _scrollListeners = [];

    function _getPortal() {
      if (!_portal) {
        _portal = document.createElement('div');
        _portal.id = 'smriti-dropdown-portal';
        document.body.appendChild(_portal);

        // Click outside closes portal
        document.addEventListener('mousedown', function (e) {
          if (_portal && !_portal.contains(e.target) && e.target !== _currentAnchor) {
            hide();
          }
        }, true);
      }
      return _portal;
    }

    function _position(anchorEl) {
      const portal = _getPortal();
      const rect = anchorEl.getBoundingClientRect();
      const vpH = window.innerHeight;
      const vpW = window.innerWidth;

      // Default: open below
      let top = rect.bottom + 4;
      const spaceBelow = vpH - rect.bottom - 8;
      const spaceAbove = rect.top - 8;
      const maxH = Math.min(240, Math.max(spaceBelow, spaceAbove));

      // Flip to above if not enough space below
      if (spaceBelow < 100 && spaceAbove > spaceBelow) {
        top = rect.top - Math.min(240, spaceAbove) - 4;
      }

      const width = Math.max(rect.width, 220);
      let left = rect.left;

      // Prevent overflow on right
      if (left + width > vpW - 8) {
        left = vpW - width - 8;
      }

      portal.style.top       = top + 'px';
      portal.style.left      = left + 'px';
      portal.style.width     = width + 'px';
      portal.style.maxHeight = maxH + 'px';
    }

    function _clearScrollListeners() {
      _scrollListeners.forEach(function (entry) {
        entry.el.removeEventListener('scroll', entry.fn);
      });
      _scrollListeners = [];
    }

    function _attachScrollListeners(anchorEl) {
      // Walk up DOM and attach scroll listeners to any scrollable parent
      let el = anchorEl.parentElement;
      while (el && el !== document.body) {
        const style = window.getComputedStyle(el);
        const overflow = style.overflow + style.overflowX + style.overflowY;
        if (/auto|scroll/.test(overflow)) {
          const fn = function () {
            if (_portal && _portal.classList.contains('open') && _currentAnchor) {
              _position(_currentAnchor);
            }
          };
          el.addEventListener('scroll', fn, { passive: true });
          _scrollListeners.push({ el: el, fn: fn });
        }
        el = el.parentElement;
      }
    }

    function show(opts) {
      const portal   = _getPortal();
      const anchorEl = opts.anchorEl;
      const items    = opts.items || [];
      const onSelect = opts.onSelect || function () {};
      const placeholder = opts.placeholder || 'No results found';

      _currentAnchor = anchorEl;
      _onSelect = onSelect;

      // Build content
      portal.innerHTML = '';
      if (!items.length) {
        const empty = document.createElement('div');
        empty.className = 's-portal-empty';
        empty.textContent = placeholder;
        portal.appendChild(empty);
      } else {
        items.forEach(function (item, idx) {
          const row = document.createElement('div');
          row.className = 's-portal-item';
          row.dataset.idx = idx;

          const label = document.createElement('strong');
          label.textContent = item.label || item.value || '';
          row.appendChild(label);

          if (item.sublabel) {
            const sub = document.createElement('small');
            sub.textContent = item.sublabel;
            row.appendChild(sub);
          }

          // Use mousedown (not click) so it fires before blur
          row.addEventListener('mousedown', function (e) {
            e.preventDefault();
            onSelect(item, anchorEl);
            hide();
          });

          portal.appendChild(row);
        });
      }

      _position(anchorEl);
      portal.classList.add('open');

      _clearScrollListeners();
      _attachScrollListeners(anchorEl);
    }

    function hide() {
      if (_portal) {
        _portal.classList.remove('open');
        _portal.innerHTML = '';
      }
      _currentAnchor = null;
      _onSelect = null;
      _clearScrollListeners();
    }

    function reposition() {
      if (_currentAnchor && _portal && _portal.classList.contains('open')) {
        _position(_currentAnchor);
      }
    }

    return { show: show, hide: hide, reposition: reposition, getPortal: _getPortal };
  })();


  /* ══════════════════════════════════════════════════════════════════
     SmritiGrid — Grid enforcement & utilities
     ══════════════════════════════════════════════════════════════════ */
  const SmritiGrid = (function () {

    /**
     * Enforce fixed height on a grid wrapper.
     * @param {HTMLElement|string} elOrSelector - element or CSS selector
     * @param {string} size - 'sm' | 'md' | 'lg' (400 | 600 | 800px)
     */
    function setSize(elOrSelector, size) {
      const el = typeof elOrSelector === 'string'
        ? document.querySelector(elOrSelector)
        : elOrSelector;
      if (!el) return;

      const heights = { sm: '400px', md: '600px', lg: '800px' };
      const h = heights[size] || '600px';

      el.style.height    = h;
      el.style.minHeight = h;
      el.style.maxHeight = 'none';
      el.style.overflowX = 'auto';
      el.style.overflowY = 'auto';
    }

    /**
     * Auto-enforce fixed height on all known grid containers in the page.
     * Called once on DOMContentLoaded.
     */
    function autoEnforce() {
      // Standard SMRITI class patterns
      document.querySelectorAll('.smriti-grid-sm').forEach(function (el) { setSize(el, 'sm'); });
      document.querySelectorAll('.smriti-grid-md').forEach(function (el) { setSize(el, 'md'); });
      document.querySelectorAll('.smriti-grid-lg').forEach(function (el) { setSize(el, 'lg'); });

      // Item Master pattern
      document.querySelectorAll('.sim-grid-wrapper').forEach(function (el) { setSize(el, 'md'); });

      // Sizewise Invoice pattern
      document.querySelectorAll('.grid-wrap').forEach(function (el) { setSize(el, 'md'); });
    }

    return { setSize: setSize, autoEnforce: autoEnforce };
  })();


  /* ══════════════════════════════════════════════════════════════════
     SmritiDropdownFix — Automatically upgrades legacy .search-dropdown
     elements that are trapped inside overflow:hidden/auto containers.
     ══════════════════════════════════════════════════════════════════
     This runs once on DOMContentLoaded and attaches a MutationObserver
     to handle dynamically added rows (e.g., when user adds grid rows).
  ══════════════════════════════════════════════════════════════════ */
  const SmritiDropdownFix = (function () {

    function _isInsideScrollContainer(el) {
      let node = el.parentElement;
      while (node && node !== document.body) {
        const style = window.getComputedStyle(node);
        const overflow = style.overflow + style.overflowX + style.overflowY;
        if (/auto|scroll/.test(overflow)) return true;
        node = node.parentElement;
      }
      return false;
    }

    function upgradeSearchDropdown(dropdown) {
      if (dropdown.dataset.smritiUpgraded) return;
      if (!_isInsideScrollContainer(dropdown)) return;

      // This dropdown is inside a scroll container — it will be clipped.
      // We flag it; the portal pattern handles the actual rendering.
      // Just bump its z-index as a fallback safety net.
      dropdown.style.zIndex = '5000';
      dropdown.dataset.smritiUpgraded = 'true';
    }

    function run() {
      document.querySelectorAll('.search-dropdown').forEach(upgradeSearchDropdown);

      // Watch for new dropdowns added dynamically
      const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (m) {
          m.addedNodes.forEach(function (node) {
            if (node.nodeType !== 1) return;
            if (node.classList && node.classList.contains('search-dropdown')) {
              upgradeSearchDropdown(node);
            }
            node.querySelectorAll && node.querySelectorAll('.search-dropdown').forEach(upgradeSearchDropdown);
          });
        });
      });

      observer.observe(document.body, { childList: true, subtree: true });
    }

    return { run: run, upgradeSearchDropdown: upgradeSearchDropdown };
  })();


  /* ══════════════════════════════════════════════════════════════════
     Auto-init on DOMContentLoaded
     ══════════════════════════════════════════════════════════════════ */
  function init() {
    SmritiGrid.autoEnforce();
    SmritiDropdownFix.run();

    // Reposition portal on window resize
    window.addEventListener('resize', function () {
      SmritiPortal.reposition();
    }, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // Already loaded (script is deferred or inline at end of body)
    init();
  }


  /* ══════════════════════════════════════════════════════════════════
     Expose as global namespace
     ══════════════════════════════════════════════════════════════════ */
  global.Smriti = global.Smriti || {};
  global.Smriti.Portal  = SmritiPortal;
  global.Smriti.Grid    = SmritiGrid;
  global.Smriti.DropFix = SmritiDropdownFix;

})(window);
