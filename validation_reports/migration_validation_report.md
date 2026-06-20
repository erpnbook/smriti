# Migration Validation Report
> **Status**: ✅ PASSED
> Generated: 2026-06-20 12:02:48.268539

## Dry Run
| Metric | Value |
|--------|-------|
| Customers Scanned | 3 |
| Partners Created | 2 |
| Partners Skipped | 1 |
| Brands Created | 0 |
| Errors | 0 |
| Execution Time | 0.023s |

## Actual Run
| Metric | Value |
|--------|-------|
| Customers Scanned | 3 |
| Partners Created | 2 |
| Errors | 0 |
| Execution Time | 0.211s |

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