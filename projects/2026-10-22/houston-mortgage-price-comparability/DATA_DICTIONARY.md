# Data dictionary and provenance

Source contract: [official public HMDA field definitions](https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields). Source field names are preserved exactly, including the API alias `loan_to_value_ratio`; this response does not have a field named `combined_loan_to_value_ratio`. Missing, exempt and blank values remain distinct source strings.

## Pinned raw financial/product projection

| Fields | Type / units | Meaning / use |
|---|---|---|
| source_row | integer ≥2 | Exact line index in original CSV, header line1; lineage, not borrower ID |
| activity_year | code | 2025 reporting year |
| lei | string | Reporting institution's LEI; preserves identity independently of display name |
| derived_msa-md, county_code, census_tract | strings | Geography 26420; countyFIPS; tract cluster, not borrower address |
| action_taken | code | 1 originated |
| loan_type, loan_purpose, lien_status | codes | Conventional1, purchase1, first lien1 |
| reverse_mortgage, open-end_line_of_credit, business_or_commercial_purpose | codes | Require2=no |
| negative_amortization, interest_only_payment, balloon_payment, other_nonamortizing_features | codes | Require2=no |
| construction_method, occupancy_type, total_units | code / string | Site-built1, principal residence1, one unit1 |
| conforming_loan_limit | code | RequireC; not independently recomputed against county/year limits |
| loan_term, intro_rate_period | months / status | Require 360 andNA respectively |
| loan_amount | roundedUSD | Public privacy-rounded amount; affects bins and fee basis |
| loan_to_value_ratio | percentage | API's combined debt/property ratio field, source name retained |
| interest_rate | percent per year | Note rate; numeric/domain check, not primary comparison outcome |
| rate_spread | percentage points | APR minus applicable APOR; primary outcome |
| total_loan_costs | USD | Gross total loan costs; require numeric; not net of credits |
| lender_credits, discount_points | USD or status | Preserved; numeric/blank/NA/Exempt counts audited; never missing→zero |
| income | USD thousands or status | Preserved for research extension; not a matching variable |
| debt_to_income_ratio | percentage / interval / status | Broad reported DTI; converted to four bands; >60/missing excluded |

`data/source_manifest.json`: original URL, retrieval date, vintage limits, original/projected/archive SHA256, row count, exact projected fields, ordered gzip part hashes/bytes. Join `data/raw/hmda.csv.gz.part*` in manifest order, gunzip to recover projection. `filers.json`: official institution LEI/name records; `aggregate.json`: separate official count/amount response. Metadata hashes are pinned. Source-row projection was compared field-for-field with all 123,445 full original rows in the executed `../energy-mortgage-toolkit/source_audit.json` audit. Original response 47,302,783 bytes; code does not need the discarded demographic fields.

## Derived and modeled output tables

| Output | Grain / definition |
|---|---|
| eligible.csv | Eligible source loan. source_row,LEI,county,tract,amount,ltv,dti_bin,interest,spread,gross_cost,cost_bps,cell. cost_bps=1 0,000×grossUSD/roundedUSD. dti_bin0:<36,1:36–42,2:43–49,3:50–60 |
| exclusion_flow.csv | Sequential counts; first exclusions partition source with eligible remainder |
| lenders.csv | Five fixed lenders. eligible_n,matched_n,retained_share,common_cells; naive and matched spread percentage points; gross-costbps; tract perturbation percentiles; replicates/clusters/name |
| common_cells.csv | Lender×shared cell: n,target_weight,spread_sum/mean,gross-costbps mean. All five use same weights |
| sensitivity.csv | Lender×grid×minimum-cell threshold; changed support/target, matched counts and mean |
| pair_stability.csv | Lender pair; tract-perturbation difference percentiles and share A lower; descriptive only |
| covariate_balance.csv | Eligible vs standardized amount/CLTV means; exposes residual within-bin imbalance, not just equal bin weights |
| pricing_disclosure.csv | Eligible lender×credit/points field availability; reported numeric zeros included in numeric count; blank/NA/Exempt distinct |
| sql_cells.csv | Independently executable SQLite group results for every eligible lender-cell |
| metrics.json | Measured aggregate counts/ranges, interpretation and false recommendation-adoption gate |
| app.html,report.html,chart.svg | Offline UI, executive report, observed chart. Scenario controls are assumptions; results are modeled |

Cell codes are ordered A amount band, L CLTV band, D DTI band, county; exact boundaries are in METHODS.md. No synthetic observations are included. Exponential cluster multipliers and hypothetical offer inputs are explicitly modeled assumptions.

## Data rights and privacy scope

Data are public HMDA modified loan records supplied for public use by FFIEC/CFPB, with official privacy modifications. They are not borrower identities. Only public numerical/product/geographic fields are projected; no demographic profiling or reidentification is attempted. Retain official source attribution and privacy rounding. Source financial facts are provided as public data, not proprietary borrower information; repository code terms do not imply ownership of government data. No additional third-party proprietary dataset is redistributed.

Published derived CSV/JSON floating values use12 significant digits for cross-platform reproducibility; pinned source snapshots retain their original values. This formatting precision is not a claim of economic accuracy.
