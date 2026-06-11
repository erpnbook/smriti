# Compatibility Matrix Validation Report
> **Status**: ✅ PASSED
> Generated: 2026-06-11 09:24:51.498889

## Scenario Matrix
| Scenario | Description | Balance | Expected | Correct |
|----------|-------------|---------|----------|---------|
| A | Legacy-only fallback | 150.0 | 150.0 | ✅ |
| B | New engine only | 220.0 | 220.0 | ✅ |
| C | Mixed: new tables take priority | 120.0 | 120.0 | ✅ |

## Scenario Details

### A — Legacy-Only Fallback
> New PSV Ledger has no entries. Fallback should return legacy data.
- Balance returned: `150.0`
- Expected: `150.0`

### B — New Engine Only
> Only new PSV Ledger entries exist. New engine must return correct totals.
- Balance returned: `220.0`
- Expected: `220.0`

### C — Mixed: New Must Win
> Both legacy PSA (+500) and new PSV (+120) exist. New engine must win.
- Balance returned: `120.0`
- Expected: `120.0` (NOT `500.0`)
- New wins: `True`
- Legacy ignored: `True`

## Assertions
| Assertion | Result |
|-----------|--------|
| Scenario A: Legacy fallback balance=150 | ✅ |
| Scenario A: Legacy fallback sell-in=200 | ✅ |
| Scenario B: New engine balance=220 | ✅ |
| Scenario C: New PSV wins (balance=120, not 500) | ✅ |