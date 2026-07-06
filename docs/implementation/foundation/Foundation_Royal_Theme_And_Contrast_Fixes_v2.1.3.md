# Implementation Plan - Royal Theme & Contrast Hardening v2.1.3

- **Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
- **Status:** Completed
- **Version:** v2.1.3
- **Date:** 2026-07-06

---

## 1. Objective
Introduce a premium, high-contrast monochrome "Royal Black and White" theme override for the SMRITI Help Center, and fix low-contrast text readability bugs across the Help Center, Business Dictionary, and Formula Registry pages.

## 2. Business Motivation
Improve visual accessibility and aesthetic quality for dark mode users, align Help Center typography with premium brand standards, and resolve readability conflicts where background colors and text colors collided in dark mode.

## 3. Scope
- Implement a route-level forced theme override in Level 2 (System Module Policy) of the SMRITI UI resolver to apply a pure black-and-white theme on `/smriti-help`.
- Replace legacy, low-contrast text color mappings in `smriti-help.html` with responsive, theme-aware variables.
- Refactor static hardcoded variables in `smriti-dictionary.html` and `smriti-formula-registry.html` to bind with responsive SMRITI tokens.

## 4. Current State
- The Help Center used the dark navy `sleek-compact` theme by default.
- Hinglish native explanation text blocks used `--primary-navy` for text color, which turned pure black in dark modes, rendering them invisible.
- Glossary and formula detail drawers used hardcoded light-mode background colors that conflicted with light text in dark mode.

## 5. Gap Analysis
- **Theme Resolver**: Lacked route-level forced policies for `/smriti-help`.
- **Contrast**: 30+ headings and text fields used black-on-black or white-on-white text colors in dark mode.
- **Responsiveness**: Dictionary and Formula pages did not bind to SMRITI tokens dynamically.

## 6. Architecture Impact
- **System Module Policy (Level 2)**: Used to intercept `/smriti-help` routes dynamically on the client side, ensuring no backend logic changes are required.

## 7. Proposed Design
- Return a custom monochrome token set in `_readSystemModulePolicy()` when `pathname` contains `/smriti-help`.
- Map dictionary and formula page `:root` style declarations directly to `--smriti-color-*` design tokens.

## 8. Files Created
- None.

## 9. Files Modified
- [smriti_ui_resolver.js](file:///D:/Smriti_Retail_OS/smriti_retail_os/public/js/smriti_ui_resolver.js)
- [smriti-help.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-help.html)
- [smriti-dictionary.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-dictionary.html)
- [smriti-formula-registry.html](file:///D:/Smriti_Retail_OS/smriti_formula-registry.html)
- [KNOWLEDGE_BASE.md](file:///D:/Smriti_Retail_OS/KNOWLEDGE_BASE.md)
- [docs/implementation/README.md](file:///D:/Smriti_Retail_OS/docs/implementation/README.md)
- [docs/walkthrough/README.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/README.md)

## 10. Dependencies
- Binds directly with standard `smriti_token_loader.html` and `smriti_theme_manager.js`.

## 11. Risks
- Cache persistence in Service Workers could prevent updated JS files from executing. *Mitigation*: Register cache bypass query parameters during testing.

## 12. Rollback Strategy
- Revert commits or restore affected files using `git checkout`.

## 13. Verification Plan
- Verify page layouts and contrast visually via DevTools and screenshots.
- Ensure zero script exceptions are thrown in the browser console.

## 14. Test Plan
- Run automated token linter `validate_tokens.py`.

## 15. Documentation Impact
- Update Walkthrough, Walkthrough Index, Implementation Index, and Knowledge Base.

## 16. Deployment Plan
- Commit to origin and sync in the testing environment `F:\Smriti9`.

## 17. Status
Completed.

## 18. Related ADRs
- None.

## 19. Related Walkthroughs
- [Walkthrough](file:///D:/Smriti_Retail_OS/docs/walkthrough/foundation/Foundation_Royal_Theme_And_Contrast_Fixes_v2.1.3.md)
