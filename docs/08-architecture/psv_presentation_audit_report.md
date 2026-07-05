---
Document ID: "ARCH-023"
Title: "PSV Presentation Audit Report"
Owner: "Architecture Team"
Audience: "Architect"
Module: "PSV"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# PSV Presentation Audit Report
**Audit Date**: 2026-06-24
**Auditor**: AITDL (AI Agent — Antigravity - Original Review)
**Project Owner**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
**Authority**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
**Scope**: `smriti_retail_os/www/smriti-presentation.html` — PSV & CGE slides

---

## Audit Verdict

```
PSV_MATH_AUDIT = PASS

Errors found    : 2
Errors fixed    : 2
Errors remaining: 0
```

---

## Finding 1 — FIXED ✅

**Document**: `smriti-presentation.html` — CGE Customer Health Score slide
**Type**: Math error — display weights did not sum to 100%
**Commit**: `c28939a`

| Element | Before | After |
|---------|--------|-------|
| Visit Frequency weight | `25%` | `40%` |
| Campaign Engagement weight | `17%` | `20%` |
| Sum displayed | `40+25+17 = 82%` ❌ | `40+40+20 = 100%` ✅ |

**Root cause**: Display text was from an old draft. JS (`calcCgeHealth`) and Formula Registry (`TST-HEALTH`) already used correct weights `40/40/20`. Classic "draft text never updated" bug.
**Instances fixed**: 6 string replacements.
**Runtime verification**: `ALL_PASS = true` via browser evaluate_script.

---

## Finding 2 — FIXED ✅

**Document**: `docs/kb/kgf/formula-registry.md` — SAL-001 Sell Through %
**Type**: Terminology mismatch — variable name inconsistent across documents
**Commit**: `401944b`

| Document | Variable Used | Was Wrong? |
|----------|--------------|-----------|
| Formula Registry (SAL-001) | `opening_stock_qty` ← old | ✅ Fixed to `dispatched_qty` |
| Blueprint Python code | `dispatched` | ✅ Correct |
| `psv_sell_through.py` (actual code) | `dispatched` | ✅ Correct |
| Presentation JS | `primary` (= dispatched) | ✅ Correct |

**Fix**: Updated Formula Registry to `sold_qty / dispatched_qty`. Added PSV-specific variable definition note. Founder approved: 2026-06-24.

---

## Formulas Verified Correct ✅

| Formula | Expression | Verified |
|---------|-----------|---------|
| Weeks of Cover (INV-002) | `140 / 35 = 4.0 weeks` | ✅ |
| Sell-Through % (SAL-001) | `850 / 1,000 × 100 = 85%` | ✅ |
| ROI Stockouts | `50,000 × 6% = 3,000 items` | ✅ |
| Customer Health Score (TST-HEALTH) | `0.4+0.4+0.2 = 1.0` | ✅ |
| Dynamic Health Score (slide) | `40+32+10 = 82 (valid weighted score)` | ✅ |
| ROI Margin Recovery | `3,000 × ₹500 = ₹15,00,000` | ✅ (assumption now visible) |

---

## Cross-Document Consistency

| Check | Status |
|-------|--------|
| Formula Registry ↔ Blueprint | ✅ Aligned (post-fix) |
| Formula Registry ↔ Code | ✅ Aligned |
| Presentation ↔ Formula Registry | ✅ Aligned (post-fix) |
| One-Pager ↔ Formula Registry | ✅ Aligned |
| Presentation ↔ One-Pager | ✅ Consistent |


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |