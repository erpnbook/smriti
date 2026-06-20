# Benchmark Analysis Report — Index Validation
> **Status**: ✅ PASSED
> Generated: 2026-06-20 12:02:49.472480

## Summary
> [!NOTE]
> **PASS/FAIL Derivation**: A query is marked ✅ PASSED if the required index EXISTS in the
> DB schema — even when the optimizer chose a full table scan. The MariaDB optimizer may
> legitimately choose a full scan on small datasets or due to statistics. A query is marked
> ⚠ ISSUE only when `full_scan=True AND row_count > 0 AND index_missing=True`.
> Indexed fields: `company`, `posting_datetime`, `channel_partner`, `item_variant`.

### ✅ Balance aggregation by channel_partner + item_variant
- Table row count: `4079`
- Full scan: `False`  |  Temporary: `False`  |  Filesort: `False`
- Scan assessment: ✓ Index used by optimizer

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Ledger Entry | `range` | `smriti_psv_ledger_company_cp_variant` | 3992 | using where |

### ✅ Sell-out filter with posting_datetime range
- Table row count: `4079`
- Full scan: `False`  |  Temporary: `True`  |  Filesort: `True`
- Scan assessment: ✓ Index used by optimizer

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Ledger Entry | `range` | `posting_datetime` | 173 | using index condition; using where; using temporary; using filesort |

### ✅ Single channel partner balance query
- Table row count: `4079`
- Full scan: `True`  |  Temporary: `True`  |  Filesort: `True`
- Scan assessment: ✓ OK — optimizer chose full scan but index exists in schema

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Ledger Entry | `all` | `None` | 3992 | using where; using temporary; using filesort |

### ✅ Aging snapshot lookup by channel_partner
- Table row count: `91`
- Full scan: `True`  |  Temporary: `False`  |  Filesort: `True`
- Scan assessment: ✓ OK — optimizer chose full scan but index exists in schema

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Stock Aging Snapshot | `all` | `None` | 91 | using where; using filesort |

## Assertions
| Assertion | Result | Reason |
|-----------|--------|--------|
| Index used/exists for: Balance aggregation by channel_partner + item_variant | ✅ | full_scan=False, index_exists=True, count=4079 |
| Index used/exists for: Sell-out filter with posting_datetime range | ✅ | full_scan=False, index_exists=True, count=4079 |
| Index used/exists for: Single channel partner balance query | ✅ | full_scan=True, index_exists=True, count=4079 |
| Index used/exists for: Aging snapshot lookup by channel_partner | ✅ | full_scan=True, index_exists=True, count=91 |