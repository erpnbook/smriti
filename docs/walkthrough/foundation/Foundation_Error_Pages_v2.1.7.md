# SMRITI Engineering Walkthrough — Branded Error Experience v2.1.7

- **Date:** 2026-07-07
- **Area:** Foundation
- **Version:** v2.1.7
- **Author:** Jawahar Ramkripal Mallah
- **Owner:** AITDL

---

## 1. Purpose
This walkthrough documents the implementation of the SMRITI Branded 404 & Error Experience, replacing generic Nginx error templates and default Frappe error layouts with a centralized, premium design that inherits user theme preferences and complies with the SMRITI Design System.

## 2. Scope
* Dedicated error pages package (`smriti_retail_os/error_pages/`) serving custom layouts dynamically via Frappe.
* Public static fallback assets (`smriti_retail_os/public/error_pages/`) serving custom layouts statically via Nginx.
* Configuration routing additions in `hooks.py` and template redirects in `www/`.
* Updated expected SHA-256 hashes in `tests/test_branding_integrity.py`.

## 3. Files Created
* [__init__.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/__init__.py)
* [error_page.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/error_page.html)
* [error_page.css](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/error_page.css)
* [error_page.js](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/error_page.js)
* [404.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/404.html)
* [403.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/403.html)
* [500.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/500.html)
* [503.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/error_pages/503.html)
* [404.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/error_pages/404.html)
* [403.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/error_pages/403.html)
* [500.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/error_pages/500.html)
* [503.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/error_pages/503.html)
* [error_page.css](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/error_pages/error_page.css)
* [error_page.js](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/error_pages/error_page.js)

## 4. Files Modified
* [hooks.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/hooks.py)
* [www/404.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/404.html)
* [www/smriti-404.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-404.html)
* [www/403.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/403.html)
* [www/smriti-403.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-403.html)
* [www/500.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/500.html)
* [www/smriti-500.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-500.html)
* [www/503.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/503.html)
* [www/smriti-503.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-503.html)
* [tests/test_branding_integrity.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tests/test_branding_integrity.py)

## 5. Architecture Decisions
1. **Decoupled Serving Layers:** Dynamic templates are resolved through Frappe via `error_page.html` (Jinja inclusion) to inherit session contexts. Static templates are placed in `public/error_pages/` to allow direct serving by Nginx without invoking Frappe processes.
2. **Client-Side Hydration:** Diagnostic fields (URL paths, timestamps, support reference IDs) are hydrated via client-side Javascript to maintain page statics and avoid server overhead.

## 6. Design Rationale
* **Token Consistency:** Page elements leverage the central `--smriti-*` tokens to reflect real-time active light/dark themes dynamically.
* **Smart Suggestion Parsing:** URL paths are inspected by Javascript client-side to dynamically output targeted shortcuts matching the user's intent.

## 7. Implementation Summary
* Developed glassmorphic layout wrappers centered on-screen.
* Programmed inline SVG animations (magnifying glass, padlock, server cables) corresponding to each HTTP error class.
* Enabled random alphanumeric Reference ID generator following HREP structure `SMRITI-ERR-YYYYMMDD-XXXXXX`.
* Mapped default routes `/404`, `/403`, `/500`, and `/503` under `hooks.py` `website_route_rules`.

## 8. Tests Executed
* Executed regression suite inside the development container:
  `bench run-tests --module smriti_retail_os.tests.test_branding_integrity`
* Executed CSS token compiler validation script:
  `python smriti_retail_os/tools/validate_tokens.py smriti_retail_os/public/`

## 9. Verification Results
* **Branding Integrity Tests:** Passed (8/8 tests OK, verifying modified file hashes matched the expected inputs).
* **Token Validator:** Passed (The new files `error_page.css` and `error_page.js` do not introduce any new contract errors or duplicates).

## 10. Known Limitations
* For Nginx-served static error views, server-side python stack traces are unavailable in Developer Mode (JS degrades gracefully and informs the user that stack traces are server-only).

## 11. Future Work
* Integrate a global Frappe request exception middleware class to automatically capture Python Tracebacks and output them directly into the 500 error panel when Developer Mode is enabled.

## 12. Related ADRs
* `ADR-0002` SMRITI Business Layer Independence
* `ADR-0009` SMRITI Platform Primitives and Services Standard

## 13. Related RFCs
* None
