# Data dictionary and source scope

All monetary values are USD, unrounded in machine-readable outputs; percentages are fractions unless a field says `bps`. SEC scale and sign are applied before storage. Explicit dash facts represent zero; nil facts are rejected. Gzip snapshots and member contents are SHA-256 pinned. The [source manifest](data/source_manifest.json) gives original public SEC URLs, entity, CIK, accession and original-document hash. The [pin inventory](data/pinned_archives.json) gives numerical archive hashes. No issuer narrative text is redistributed.

## Observations

| Dataset | Unit / meaning |
|---|---|
| `data/raw/*-2025-inline.json.gz` | Original numeric facts with concept, context, dates, entity, dimensions, scale, sign, unit measure and source ID |
| `data/raw/*.json.gz` | Companyfacts and submissions snapshots; SEC concept/units arrays and filing metadata |
| SKT 2021 / 2024 inline snapshots | Additional original OP-scope historical CFO facts |
| `outputs/source_lineage.csv` | 65 current selected facts; ticker, field, concept, value, context dimensions, filing dates and exact archive / pointer |
| `outputs/debt_maturities.csv` | 36 issuer/year principal buckets: 2026, 2027, 2028, 2029, 2030 and thereafter |
| `outputs/debt_basis_bridge.csv` | Sum of face maturities, selected book debt, dollar / percentage difference and review tolerance |
| `outputs/comparative_cfo.csv` | 42 annual CFO facts for 2019–2025 with accession and source pointer |
| `outputs/historical_cfo_changes.csv` | 36 consecutive annual changes, current / previous CFO and fractional growth |

## Entity and cash-flow interpretation

| Issuer | Scope / explicit choice |
|---|---|
| KIM | Consolidated unsecured maturity context only; unconsolidated-JV mortgage schedule excluded. Book measure NotesPayable. Ordinary-dividend cash-flow measure retained. |
| REG | Listed parent CIK 910606. Cash including restricted less restricted cash. Common, preferred and minority distributions summed. |
| FRT | Consolidated debt and capital-lease book measure. Common/preferred plus minority/redemption cash returns; broader distribution scope flagged. |
| BRX | Consolidated LongTermDebt book measure; cash-flow PaymentsOfCapitalDistribution. |
| SKT | `dei:LegalEntityAxis = skt:TangerPropertiesLimitedPartnershipMember` for the entire current ladder and historical CFO. Parent values are not substituted. |
| SPG | Consolidated LongTermDebt; common/preferred and minority cash distributions summed. |

Opening cash and book debt are December 31, 2025 instants; CFO and distributions are the full 2025 annual interval. Maturity amounts are face principal, not estimated market debt values or financing offers. Selection code in `../reit_pipeline.py` states the exact concepts / dimensions; the lineage table is authoritative for each numerical selection.

## Modeled outputs and assumptions

| Output / field | Interpretation |
|---|---|
| `sql_maturity_exposure.csv` | Next-12-month, five-year, total and two-year concentration from `analysis.sql` |
| `scenario_solutions.csv` | 90 persistent-shock cases; CFO level shortfall, spread in basis points, feasibility, minimum rollover and cash-floor gap |
| `cash_waterfalls.csv` | 450 annual cash rows for the persistent grid; annual maturity, incremental interest / fee, closing cash and shortfall |
| `recovery_sensitivity.csv` | 48 conditional two-year / five-year shock comparisons |
| `rollover_frontier.csv` | Minimum feasible rollover over scenario settings, not a forecast probability |
| `financing_review.csv` | Per-issuer exposure and worst conditional cash-floor gap; diligence queue, not a credit rating |
| `application_data.json` | Embedded observed inputs and modeled tables used for browser reconciliation |
| `metrics.json` | Audited counts / sums and scenario findings, compared with `data/expected_results.json` |

Maintenance capex 10% of base CFO, cash floor 10% of base CFO, issuance fee 1% of refinanced principal, fixed distributions, common rollover share, half-year new-debt interest and maturity beyond the five-year horizon are assumptions. Scenario CFO shortfall and spread are user choices. Null minimum rollover means infeasible rather than zero. No assumed revolver availability, asset-sale proceeds or equity proceeds are embedded.
