# Crocs Brand Economics & Cash Allocation

**Can Crocs fund buybacks while reducing debt?**

The base scenario funds $600m in first-period buybacks and $134m in debt reduction. Test the brand margins behind that cash, and separate EPS growth from operating recovery.

[Portfolio case study](https://prathameshsingh.com/projects/crocs-brand-cash-allocation/)

## Open the project

- [Editable Excel model](outputs/CROX_Financial_Model.xlsx)
- [Executive memo](outputs/report.html)
- [Five-minute presentation](outputs/CROX_Five_Minute_Presentation.pptx)
- [Scenario results](outputs/CROX_Scenario_Results.csv)
- [Valuation sensitivity](outputs/CROX_Valuation_Sensitivity.csv)
- [Methods](METHODS.md)
- [Interview notes](INTERVIEW.md)

## Finding

First-period operating cash of $801m less $80m capex supports $600m of buybacks and $134m of residual debt repayment after the reserve. In the downside, operating cash falls to $363m and net leverage reaches 1.73x. A hypothetical $200m nondeductible impairment reduces profit and assets without itself reducing cash.

## Reproduce and audit

The shared [analysis source](../../src/), [input snapshots and provenance](../../data/), and [reproduction instructions](../../README.md) support both company models. From the shared capital-allocation-models directory, run `python src/model.py` and `python src/validate.py`. This shared engine is not an independently duplicated implementation for each company.

## Limits

Brand contribution margins are analyst assumptions, not disclosed cash margins. PPE and finite intangibles use a combined depreciation pool. Buyback share settlements use a fixed-price proxy. Terminal value is 64.4% of base DCF enterprise value. No probabilities or investment recommendation are assigned. Latest balances are September 30. The quote is October 30. First-period valuation proration ignores seasonality. Other assets and non-payable liabilities remain constant. Interest uses opening debt. No employment, realized impact or stock recommendation is claimed.
