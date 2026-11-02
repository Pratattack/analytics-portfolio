# United Rentals Fleet & Capital Allocation

**How much cash can United Rentals return after funding its fleet?**

The base scenario leaves $597m for first-period buybacks against an illustrative $1.5bn ceiling. Stronger demand can still mean smaller distributions when fleet investment rises.

[Portfolio case study](https://prathameshsingh.com/projects/united-rentals-fleet-capital-allocation/)

## Open the project

- [Editable Excel model](outputs/URI_Financial_Model.xlsx)
- [Executive memo](outputs/report.html)
- [Five-minute presentation](outputs/URI_Five_Minute_Presentation.pptx)
- [Scenario results](outputs/URI_Scenario_Results.csv)
- [Valuation sensitivity](outputs/URI_Valuation_Sensitivity.csv)
- [Methods](METHODS.md)
- [Interview notes](INTERVIEW.md)

## Finding

Operating cash of $5,430m less $4,336m net investing outflow leaves $1,094m before financing. After the cash reserve and an illustrative $500m dividend budget, first-period repurchases are $597m. The upside case supports only $448m initially because its fleet budget is larger.

## Reproduce and audit

The shared [analysis source](../../src/), [input snapshots and provenance](../../data/), and [reproduction instructions](../../README.md) support both company models. From the shared capital-allocation-models directory, run `python src/model.py` and `python src/validate.py`. This shared engine is not an independently duplicated implementation for each company.

## Limits

Fleet cohorts, disposal ages and the rounded opening gross fleet are approximations. Future M&A is excluded. Refinancing and repayment budgets are assumptions, not commitments or contractual maturities. Terminal value is 74.9% of base DCF enterprise value. The demanding reverse margin may indicate model limits rather than mispricing. Latest balances are September 30. The quote is October 30. First-period valuation proration ignores seasonality. Other assets and non-payable liabilities remain constant. Interest uses opening debt. No employment, realized impact or stock recommendation is claimed.
