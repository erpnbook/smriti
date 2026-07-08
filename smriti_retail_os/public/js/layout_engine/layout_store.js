/**
 * @file:    public/js/layout_engine/layout_store.js
 * @desc:    SMRITI Retail OS Layout Engine — Unified state store.
 *           Reads/writes localStorage and syncs to server via layout_service.py.
 *           Legacy bridge: reads smriti-sidebar-* keys on first load.
 * @version: 1.0.0
 * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
 */

(function (global) {
    "use strict";

    var NS = "srle.";                          // localStorage namespace
    var LEGACY_POS_KEY = "smriti-sidebar-position";
    var LEGACY_COLLAPSED_KEY = "smriti-sidebar-collapsed";
    var LEGACY_GROUPS_KEY = "smriti-sidebar-collapsed-groups";
    var LEGACY_FAVS_KEY = "smriti-sidebar-favorites";

    var DEFAULTS = {
        position:         "left",
        collapsed:        false,
        icon_only:        false,
        sidebar_width:    260,
        last_workspace:   "",
        collapsed_groups: [],
        favorites:        []
    };

    var _cache = null;   // in-memory copy after first load

    /**
     * Migrates legacy smriti-sidebar-* localStorage keys into srle.* namespace.
     * Runs once per browser; writes srle.migrated=true to prevent re-running.
     */
    function _migrateLegacy() {
        if (localStorage.getItem(NS + "migrated") === "true") return;
        try {
            var pos = localStorage.getItem(LEGACY_POS_KEY);
            if (pos) localStorage.setItem(NS + "position", pos);

            var col = localStorage.getItem(LEGACY_COLLAPSED_KEY);
            if (col) localStorage.setItem(NS + "collapsed", col);

            var grp = localStorage.getItem(LEGACY_GROUPS_KEY);
            if (grp) localStorage.setItem(NS + "collapsed_groups", grp);

            var fav = localStorage.getItem(LEGACY_FAVS_KEY);
            if (fav) localStorage.setItem(NS + "favorites", fav);

            localStorage.setItem(NS + "migrated", "true");
        } catch (e) { /* localStorage may be restricted */ }
    }

    function _readAll() {
        if (_cache) return _cache;
        _migrateLegacy();
        var out = {};
        for (var k in DEFAULTS) {
            if (!DEFAULTS.hasOwnProperty(k)) continue;
            var raw = localStorage.getItem(NS + k);
            if (raw === null) {
                out[k] = DEFAULTS[k];
            } else {
                try { out[k] = JSON.parse(raw); }
                catch (e) { out[k] = DEFAULTS[k]; }
            }
        }
        _cache = out;
        return _cache;
    }

    var Store = {
        /**
         * Returns a single preference value.
         * @param {string} key
         * @param {*} defaultVal  — returned if key is unset
         */
        get: function (key, defaultVal) {
            var all = _readAll();
            return all.hasOwnProperty(key) ? all[key] : (defaultVal !== undefined ? defaultVal : null);
        },

        /**
         * Sets a single preference value in localStorage and in-memory cache.
         * @param {string} key
         * @param {*} value
         */
        set: function (key, value) {
            _readAll();   // ensure cache is warm
            _cache[key] = value;
            try { localStorage.setItem(NS + key, JSON.stringify(value)); }
            catch (e) { /* quota exceeded — silently ignore */ }

            // Keep legacy keys in sync so existing pages continue to work
            if (key === "position")         try { localStorage.setItem(LEGACY_POS_KEY, value); } catch (e) {}
            if (key === "collapsed")        try { localStorage.setItem(LEGACY_COLLAPSED_KEY, String(value)); } catch (e) {}
            if (key === "collapsed_groups") try { localStorage.setItem(LEGACY_GROUPS_KEY, JSON.stringify(value)); } catch (e) {}
            if (key === "favorites")        try { localStorage.setItem(LEGACY_FAVS_KEY, JSON.stringify(value)); } catch (e) {}
        },

        /**
         * Returns all stored preferences as a plain object.
         */
        getAll: function () {
            return Object.assign({}, _readAll());
        },

        /**
         * Resets all preferences to defaults (localStorage + cache).
         */
        reset: function () {
            for (var k in DEFAULTS) {
                if (DEFAULTS.hasOwnProperty(k)) {
                    try { localStorage.removeItem(NS + k); } catch (e) {}
                }
            }
            _cache = null;
        },

        /**
         * Syncs current preferences to the server via layout_service.py.
         * Silently fails if Frappe is unavailable.
         */
        syncToServer: function () {
            if (!global.frappe || !global.frappe.call) return;
            var prefs = this.getAll();
            global.frappe.call({
                method: "smriti_retail_os.layout_engine.layout_service.save_layout_preferences",
                args: { prefs: JSON.stringify(prefs) },
                callback: function () {},
                error: function () {}   // silent
            });
        },

        /**
         * Restores preferences from the server, merges into localStorage.
         * @param {function} [callback]  — called with the merged prefs dict
         */
        restoreFromServer: function (callback) {
            if (!global.frappe || !global.frappe.call) {
                if (callback) callback(this.getAll());
                return;
            }
            var self = this;
            global.frappe.call({
                method: "smriti_retail_os.layout_engine.layout_service.get_layout_preferences",
                callback: function (r) {
                    if (r && r.message) {
                        var serverPrefs = r.message;
                        for (var k in serverPrefs) {
                            if (serverPrefs.hasOwnProperty(k)) {
                                self.set(k, serverPrefs[k]);
                            }
                        }
                        _cache = null;  // invalidate cache so next getAll re-reads
                    }
                    if (callback) callback(self.getAll());
                },
                error: function () {
                    if (callback) callback(self.getAll());
                }
            });
        }
    };

    global.SRLE_Store = Store;

}(window));
