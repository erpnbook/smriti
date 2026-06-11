# Migration Validation Report
> **Status**: ✅ PASSED
> Generated: 2026-06-11 10:11:37.450192

## Dry Run
| Metric | Value |
|--------|-------|
| Customers Scanned | 1 |
| Partners Created | 1 |
| Partners Skipped | 0 |
| Brands Created | 1 |
| Errors | 0 |
| Execution Time | 0.015s |

## Actual Run
| Metric | Value |
|--------|-------|
| Customers Scanned | 1 |
| Partners Created | 1 |
| Errors | 0 |
| Execution Time | 0.042s |

## Balance Reconciliation
| Metric | Value |
|--------|-------|
| Items Checked | 2 |
| Balance Parity | ✅ Yes |

### Per-Item Detail
| Item Code | Legacy Balance | New Balance | Match |
|-----------|--------------|-------------|-------|
| MIG-ITEM-A | 70.0 | 70.0 | ✅ |
| MIG-ITEM-B | 40.0 | 40.0 | ✅ |

## Assertions
| Assertion | Result |
|-----------|--------|
| Dry run produced zero errors | ✅ |
| Actual run produced zero errors | ✅ |
| Legacy and new ledger balances are identical | ✅ |