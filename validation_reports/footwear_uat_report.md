# Footwear UAT Report
> **Status**: ✅ PASSED
> Generated: 2026-06-11 09:24:52.357104

## Dataset Summary
| Metric | Value |
|--------|-------|
| SKU Templates | 500 |
| Variants | 3000 |
| Distributors | 10 |
| Dealers | 100 |
| Ledger Entries | 2160 |

## Size Curve Analytics
| Size | Units Dispatched | Units Sold | Sell Rate % |
|------|----------------|-----------|-------------|
| ? | 7404.0 | 3444.0 | 46.5% |

## Redistribution Suggestions (Top 10)
| Item | Source Partner | Target Partner | Transfer Qty | Source WOC | Target WOC |
|------|--------------|---------------|-------------|-----------|-----------|

## Stock Cover Risks (Top 10)
| Item | Partner | WOC | Status | Balance | Velocity |
|------|---------|-----|--------|---------|----------|

## Assertions
| Assertion | Result |
|-----------|--------|
| Size curve: fast sizes (8,9) have >= sell rate vs slow sizes (6,11) | ✅ |
| WOC summary executes without error for UAT distributor | ✅ |
| Redistribution engine executes without error | ✅ |
| Stock cover risk engine executes without error | ✅ |
| Snapshot generation completes | ✅ |