# Walkthrough - Foundation Royal Theme & Contrast Fixes v2.1.3

Implementation of the premium "Royal Black and White" theme override for the SMRITI Help Center, and contrast accessibility hardening across help, dictionary, and formula registry pages has been successfully completed.

## 1. Purpose
Resolve accessibility contrast bugs on the SMRITI Help Center page where text elements (such as Hinglish definitions and FAQ questions) rendered invisible in dark mode due to incorrect token mapping. Introduce a premium monochrome Royal Black and White aesthetic for `/smriti-help`.

## 2. Scope
- Add route-level forced overrides for `/smriti-help` in Level 2 System Module Policy of the SMRITI UI resolver.
- Re-style low-contrast text elements on the Help Center.
- Migrate Business Dictionary and Formula Registry pages to responsive SMRITI tokens.

## 3. Files Created
- None.

## 4. Files Modified
- [smriti_ui_resolver.js](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/js/smriti_ui_resolver.js)
- [smriti-help.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-help.html)
- [smriti-dictionary.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-dictionary.html)
- [smriti-formula-registry.html](file:///D:/Smriti_Retail_OS/smriti_formula-registry.html)
- [KNOWLEDGE_BASE.md](file:///D:/Smriti_Retail_OS/KNOWLEDGE_BASE.md)
- [docs/walkthrough/README.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/README.md)

## 5. Architecture Decisions
- **Level 2 Resolver Overrides**: Leveraged the client-side system module policy layer to dynamically alter token maps based on route, keeping structural changes out of the backend views.

## 6. Design Rationale
- Standard CSS style sheets are overridden dynamically by the custom properties written into the document `:root`.
- Light/Dark mode is derived automatically by the luminance of the page background color.

## 7. Implementation Summary
- Added checking logic in `_readSystemModulePolicy()` to return a high-contrast black-and-white palette if the route contains `/smriti-help`.
- Mapped all `color: var(--primary-navy)` text elements to `color: var(--text-dark)`.
- Replaced static light-mode values with responsive tokens in `:root` of dictionary and formula layouts.

## 8. Tests Executed
- Executed `validate_tokens.py` to check for style violations.
- Inspected calculated styles of `body` inside the browser console.

## 9. Verification Results
- `classes: "dark-mode smriti-theme-royal-black-white"`, `theme: "dark"` applied on load.
- Hinglish native text and FAQ cards render with high contrast and are 100% readable.

## 10. Known Limitations
- Service Worker caching can persist stale JS files during deployment. Cache storage must be cleared manually if changes are not immediately visible.

## 11. Future Work
- Consolidate common styles of explainability drawers into a shared css file.

## 12. Related ADRs
- None.

## 13. Related RFCs
- None.
