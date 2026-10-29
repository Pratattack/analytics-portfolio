# Did import-duty exposure change, or did the sourcing basket change?

Import-duty ratios and sourcing mix can move in different directions. A strict comparison exposes a major coverage gap before turning historical duty differences into a budget scenario.

## Finding
Full-population historical duty ratios rise from 8.57% to 12.61% for transformers/converters/inductors and from 14.11% to 16.97% for accumulators; semiconductor-device ratios move from 7.23% to 7.27%. Only 46.7% of 2026 accumulator value enters the strict cross-year panel, so its decomposition cannot be generalized to the whole category.

## Decision use
Inspect product comparability and coverage before treating an origin-level average as a sourcing opportunity. The tool tests which hypothetical supplier premium and switching cost would offset a historical duty difference; it does not select a supplier or quote a legal tariff.

## Evidence and method
Official Census August 2025 and August 2026 detailed import archives. Primary comparison: January-August YTD imports for consumption and calculated duties. Prespecified HS4 groups 8504, 8507 and 8541. Scenario budgets and switching costs are hypothetical.

Fixed-width extraction and exact reconciliation to independently published commodity totals. Positive-value, identical-description HTS10/origin panels separate starting-basket rate changes from composition. Report matched value coverage and August-only sensitivity. Sourcing pairs standardize both origins to a common source basket with at least 80% coverage; SQL independently reconciles totals.

## Limits
Calculated duties are not final collections or causal tariff incidence. Same-code cells can conceal quality and supplier changes. Countries are not suppliers. Current legal rates, origin eligibility, quotes, capacity, freight and switching feasibility are not established. Historical retrieved files may contain revisions, and modeled budget differences are not observed savings.
