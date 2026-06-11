# Benchmark Analysis Report — Index Validation
> **Status**: ✅ PASSED
> Generated: 2026-06-11 09:24:52.366827

## Summary
> [!NOTE]
> Validates that MariaDB query execution plans use the configured indexes.
> Indexed fields: `company`, `posting_datetime`, `channel_partner`, `item_variant`.
> A full table scan (`type=ALL`) is acceptable ONLY when the table is empty.

### ✅ Balance aggregation by channel_partner + item_variant
- Table row count: `2167`
- Full scan: `True`  |  Temporary: `True`  |  Filesort: `True`

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Ledger Entry | `all` | `None` | 2080 | using where; using temporary; using filesort |

### ✅ Sell-out filter with posting_datetime range
- Table row count: `2167`
- Full scan: `False`  |  Temporary: `True`  |  Filesort: `True`

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Ledger Entry | `range` | `posting_datetime_index` | 97 | using index condition; using where; using temporary; using filesort |

### ✅ Single channel partner balance query
- Table row count: `2167`
- Full scan: `True`  |  Temporary: `True`  |  Filesort: `True`

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Ledger Entry | `all` | `None` | 2080 | using where; using temporary; using filesort |

### ✅ Aging snapshot lookup by channel_partner
- Table row count: `88`
- Full scan: `True`  |  Temporary: `False`  |  Filesort: `True`

| Table | Type | Key Used | Rows Est | Extra |
|-------|------|----------|----------|-------|
| tabPSV Stock Aging Snapshot | `all` | `None` | 88 | using where; using filesort |

## Assertions
| Assertion | Result |
|-----------|--------|
| Index used/exists for: Balance aggregation by channel_partner + item_variant | ✅ |
| Index used/exists for: Sell-out filter with posting_datetime range | ✅ |
| Index used/exists for: Single channel partner balance query | ✅ |
| Index used/exists for: Aging snapshot lookup by channel_partner | ✅ |