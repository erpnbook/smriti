# SMRITI Implementation Plan — Branded Error Experience

- **Document ID:** Foundation-Error-Pages-v2.1.7
- **Title:** SMRITI Branded 404 & Error Experience
- **Module:** Foundation
- **Phase:** Phase 1
- **Version:** v2.1.7
- **Status:** Draft
- **Author:** Jawahar Ramkripal Mallah
- **Owner:** AITDL
- **Last Updated:** 2026-07-07

---

## 1. Objective
Replace the generic, unbranded Nginx `404 Not Found nginx/1.22.1` page and raw Frappe web/desk error templates with a fully branded SMRITI Error Experience that integrates seamlessly with the SMRITI Design System (including the SMRITI Midnight theme, light/dark modes, and WCAG-compliant styling).

## 2. Business Motivation
SMRITI Retail OS is an enterprise-grade retail platform. Exposing raw stack traces, generic Nginx error templates, or developer-focused messages to checkout cashiers, store managers, and corporate admins compromises the premium user experience, increases support ticket volumes, and raises security concerns by leaking internal stack/environment information. A centralized, branded, and descriptive error environment provides professional fallback options and actionable recommendations.

## 3. Scope
* **Dedicated Error Module:** Create `smriti_retail_os/error_pages/` containing templates for `404.html`, `403.html`, `500.html`, `503.html`.
* **Reusable UI Components:** Create a single reusable engine consisting of `error_page.html` (skeleton layout), `error_page.css` (glassmorphic styling using SMRITI tokens), and `error_page.js` (hydrating dynamic parameters like timestamps, suggestion routes, and developer diagnostics).
* **Nginx Integration:** Configure and document Nginx overrides to redirect all server-level HTTP errors (404, 500, 502, 503, 504) to the SMRITI static templates.
* **Frappe/Website Integration:** Route all uncaught website route failures and permission errors to the custom SMRITI error views.
* **HREP Compliance:** Expose user-friendly severity classes, error code mappings, and client-side help text, hiding raw python/SQL tracebacks unless developer mode is explicitly enabled.

## 4. Current State
* If Nginx fails or cannot connect to the Frappe backend, it displays:
  ```
  404 Not Found
  nginx/1.22.1
  ```
* If Frappe encounters an unknown route, it displays `www/404.html` or `www/smriti-404.html`, which currently contain static, hardcoded HTML templates.
* Similarly, `www/403.html` and `www/smriti-403.html` handle permissions, but are not synchronized with the theme resolver or the dynamic suggestions engine.
* No unified module exists for 500 (Internal Server Error) or 503 (Service Unavailable) overrides.

## 5. Gap Analysis
1. **Design Token Alignment:** Existing error templates do not load the canonical `smriti_tokens.css` or coordinate with `smriti_ui_resolver.js` to inherit user theme choices.
2. **Dynamic Suggestions:** Missing context-aware routing suggestions (e.g. recommending Sales Studio if a URL contains "sale").
3. **Diagnostics & HREP:** Missing automated timestamps, transaction support reference IDs (`SMRITI-ERR-YYYYMMDD-XXXXXX`), and safe developer mode toggles.
4. **Nginx Fallback:** When Frappe is offline, Nginx fallback pages are plain text and unbranded.

## 6. Architecture Impact
* **Routing Layer:** Enhances the `hooks.py` `website_route_rules` to map all canonical HTTP error status requests.
* **Static Assets Layer:** Exposes reusable scripts and stylesheets via the `public/` assets pipeline to ensure they are available even when gunicorn/backend services are offline.
* **Branding Integrity:** Integrates with the regression suite in `test_branding_integrity.py` to lock down error template hashes.

## 7. Proposed Design
* **Glassmorphic Neumorphic Card:** A premium, modern centered glass panel containing:
  - Branded header (SMRITI monogram and wordmark).
  - Floating visual illustration (CSS-animated inline SVG specific to the error code).
  - High-impact gradient text for status code (e.g. `404`, `500`).
  - Severity-colored subtitles and actionable descriptions.
  - Buttons: Go Back (history-based), Home, Dashboard, and Search.
* **Suggestion Engine:** JS parses `window.location` and suggests target routes matching the user's intent.
* **Diagnostics Panel:** Expandable dashboard displaying Requested Path, Timestamp, Reference ID, and environment context.
* **Theme Sync:** Loads the `smriti_token_loader` to automatically match light/dark preferences.

## 8. Files Created
* `smriti_retail_os/error_pages/`:
  - `__init__.py`: Package entry point.
  - `error_page.html`: Common skeleton layout.
  - `error_page.css`: Responsive typography and layout rules.
  - `error_page.js`: Client-side suggestions, diagnostics, and diagnostics toggle.
  - `404.html`: Template wrapper for Not Found.
  - `403.html`: Template wrapper for Access Denied.
  - `500.html`: Template wrapper for Server Error.
  - `503.html`: Template wrapper for Service Unavailable.
* `smriti_retail_os/public/error_pages/`:
  - `404.html`: Static fallback version for Nginx.
  - `403.html`: Static fallback version for Nginx.
  - `500.html`: Static fallback version for Nginx.
  - `503.html`: Static fallback version for Nginx.
  - `error_page.css`: Copy of stylesheet for static serving.
  - `error_page.js`: Copy of javascript for static serving.

## 9. Files Modified
* [hooks.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/hooks.py): Map route rules and exception redirects.
* [www/404.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/404.html): Align with new branded layout.
* [www/smriti-404.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-404.html): Align with new branded layout.
* [www/403.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/403.html): Align with new branded layout.
* [www/smriti-403.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-403.html): Align with new branded layout.
* [tests/test_branding_integrity.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tests/test_branding_integrity.py): Update expected file hashes.
* [docs/implementation/README.md](file:///D:/Smriti_Retail_OS/docs/implementation/README.md): Update chronological plan registry.

## 10. Dependencies
* `smriti_tokens.css` (Midnight theme system default)
* `smriti_ui_resolver.js` (Theme manager integration)

## 11. Risks
* **Nginx Configuration Parsing:** Incorrect config could block asset fetching or create routing loops for static files.
* **Test Failure:** Modifying template files without updating `test_branding_integrity.py` will fail automated CI tests.

## 12. Rollback Strategy
* Revert the modifications to `hooks.py` and `test_branding_integrity.py`.
* Restore previous `www/404.html` and `www/403.html` templates via `git checkout`.
* Remove the `smriti_retail_os/error_pages/` and `smriti_retail_os/public/error_pages/` directories.

## 13. Verification Plan
### Automated Tests
- Run `bench run-tests --module smriti_retail_os.tests.test_branding_integrity` to verify that all hashes are matched and there are no route leaks.
- Run `python3 smriti_retail_os/tools/validate_tokens.py smriti_retail_os/public/` to verify CSS token compliance.

### Manual Verification
- Test unknown routes: Navigate to `/invalid-url` and verify that the branded 404 page appears.
- Test permission limits: Trigger a permission exception and verify 403 styling.
- Verify light/dark theme toggle synchronization.
- Test simulated offline state and verify diagnostic tags.

## 14. Test Plan
* Validate responsive design (Mobile, Tablet, Desktop) using browser developer tools.
* Test screen reader accessibility using ARIA attributes.
* Validate suggestion links under varying URL structures.

## 15. Documentation Impact
* Create `docs/implementation/SMRITI_ERROR_PAGES.md` containing architectural decisions and deployment parameters.
* Update `CHANGELOG.md` with version `v2.1.7` modifications.

## 16. Deployment Plan
1. Commit changes to development repository on `D:\Smriti_Retail_OS`.
2. Sync changes to the testing environment on `F:\Smriti9` using `git pull`.
3. Clear bench cache and restart the bench.
4. Mount or apply the custom Nginx template and reload the service.

## 17. Status
* Draft

## 18. Related ADRs
* `ADR-0002` SMRITI Business Layer Independence
* `ADR-0009` SMRITI Platform Primitives and Services Standard

## 19. Related Walkthroughs
* None (New implementation)
