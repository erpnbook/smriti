# SMRITI Branded Error Experience — Deployment & Customization Guide

- **Document ID:** SMRITI-ERROR-PAGES
- **Title:** SMRITI Branded Error Experience
- **Module:** Foundation
- **Version:** v1.0.0
- **Status:** Active
- **Last Updated:** 2026-07-07

---

## 1. Architecture

The SMRITI Branded Error Experience uses a dual-layered design to provide a highly polished, responsive fallback interface regardless of server status:

1. **Jinja-Rendered Layer (Frappe):** Accessed when the Frappe server is online. It routes requests through Frappe's website router to custom Jinja templates inside `smriti_retail_os/www/` or `smriti_retail_os/error_pages/`, dynamically resolving session details and loading tokens.
2. **Static Fallback Layer (Nginx):** Accessed when the Frappe server is offline or experiencing server errors (500, 502, 503, 504). Nginx serves fully pre-rendered static files located in `public/error_pages/` directly to the client.

Both layers load the central token registry (`smriti_tokens.css`) to align automatically with the active light/dark theme, and execute client-side hydration (`error_page.js`) for timestamps, support reference IDs, and route suggestions.

---

## 2. Folder Structure

```
smriti_retail_os/
├── error_pages/                  # Reusable Jinja-based templates (Frappe)
│   ├── __init__.py
│   ├── error_page.html           # Reusable skeleton layout
│   ├── error_page.css            # Common layout stylesheet
│   ├── error_page.js             # Suggestions and diagnostics script
│   ├── 404.html                  # Page Not Found
│   ├── 403.html                  # Permission Denied
│   ├── 500.html                  # Internal Server Error
│   └── 503.html                  # Service Unavailable
│
├── public/                       # Static public assets (Nginx & CDN)
│   └── error_pages/
│       ├── error_page.css        # Linked stylesheet
│       ├── error_page.js         # Linked hydration script
│       ├── 404.html              # Static Page Not Found
│       ├── 403.html              # Static Permission Denied
│       ├── 500.html              # Static Internal Server Error
│       └── 503.html              # Static Service Unavailable
│
└── www/                          # Frappe Website Router mappings
    ├── 403.html
    ├── smriti-403.html
    ├── 404.html
    ├── smriti-404.html
    ├── 500.html
    ├── smriti-500.html
    ├── 503.html
    └── smriti-503.html
```

---

## 3. Customization Guide

### Modifying Messages & Descriptions
To customize user-facing descriptions (e.g. changing help text for access control), edit the respective wrapper template:
- For Frappe pages: Modify the variables at the top of `smriti_retail_os/error_pages/{404,403,500,503}.html`.
- For Nginx pages: Modify the `<p class="error-message">` block directly inside `smriti_retail_os/public/error_pages/{404,403,500,503}.html`.

### Adding Suggestion Mappings
To modify or append smart suggestion keywords based on the requested URL paths:
1. Open `error_page.js` (edit both `smriti_retail_os/error_pages/error_page.js` and `smriti_retail_os/public/error_pages/error_page.js`).
2. Add a new object inside the `mappings` array of the `hydrateSuggestions` function:
   ```javascript
   { key: 'keyword-in-url', label: 'Emoji Title of Suggested Page', route: '/target-route' }
   ```

---

## 4. Deployment Steps

1. **Deploy Source Files:** Pull or sync the modified code repository into the target server directory (e.g. `/home/frappe/frappe-bench/apps/smriti_retail_os`).
2. **Clear Cache:** Clear the site's cache to force Frappe to resolve the revised template mappings in `hooks.py`:
   ```bash
   bench --site <site-name> clear-cache
   ```
3. **Build Static Assets:** Compile assets and ensure symlinks are correctly established:
   ```bash
   bench build
   ```
4. **Apply Nginx Configurations:** Configure the reverse proxy to capture HTTP status codes and route them to the static error pages folder.

---

## 5. Nginx Configuration

Add the following parameters inside the site's server block configuration template (typically `/templates/nginx/frappe.conf.template` or the main Nginx virtual host configuration):

```nginx
# ── SMRITI Branded Error Experience Overrides ──

# Intercept backend error codes and serve custom static views
proxy_intercept_errors on;
fastcgi_intercept_errors on;

# Map status codes to custom error pages
error_page 404 /assets/smriti_retail_os/error_pages/404.html;
error_page 500 /assets/smriti_retail_os/error_pages/500.html;
error_page 502 503 504 /assets/smriti_retail_os/error_pages/503.html;

# Keep Nginx error routing context clean
location ~ ^/assets/smriti_retail_os/error_pages/ {
    root /home/frappe/frappe-bench/sites;
    try_files $uri =404;
    access_log off;
    expires 1d;
}
```

*Note: Reload the Nginx service to apply changes:*
```bash
sudo nginx -s reload
```

---

## 6. Testing Checklist

- [ ] **404 Route Test:** Navigate to `/this-page-does-not-exist` and verify that the glassmorphic card renders with code `404` and magnifying glass illustration.
- [ ] **403 Route Test:** Request an unauthorized administrative route (e.g., `/app/user-permission`) and verify lock illustration.
- [ ] **Offline Mode Check:** Disconnect server network, trigger a reload, and verify Nginx fallback page renders cleanly.
- [ ] **Developer Mode Check:** Turn developer mode on (or append `?debug=1` to URL) and verify that the collapsible diagnostics details display the Developer Mode environment and debug panels.
- [ ] **Theme Mode Sync:** Toggle hybrid-dark/hybrid-light theme in SMRITI Sidebar and verify error pages adapt instantly.
