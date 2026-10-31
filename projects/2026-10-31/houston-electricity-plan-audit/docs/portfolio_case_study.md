# Approved case-study copy

**Title:** Houston Electricity Plan Audit

**Opening:** When does the cheapest electricity plan stop being cheapest? I reconstructed seven contracts to test how usage thresholds, delivery charges and contract terms change the answer.

**Finding:** In one audited contract, dropping from 1,000 to 999 kWh raises the modeled bill by $124.81 because a $125 credit disappears. Two hypothetical profiles with the same total consumption produce a $750 difference across twelve billing cycles.

**Why it matters:** Comparing a single advertised rate can hide the importance of monthly usage. The tool lets readers inspect costs around each credit threshold and see the conditions behind a ranking.

**Data:** Seven provider-issued residential labels across four providers, dated April to October 2026; retrieved on 31 October 2026. Twenty-one published prices reconciled. Older labels and excluded offers remain visible.

**Methods:** Piecewise contract arithmetic, billing-cycle scenarios, pairwise break-even analysis, source reconciliation, Python, SQL and an independently checked JavaScript calculator.

**Limits:** A selected research sample, not a live market comparison. Profiles are hypothetical. Taxes and nonrecurring fees are excluded. Address eligibility is unverified. Older offers are not represented as current enrollment options.

**Homepage recommendation:** Consider featuring this after approval because its question is accessible, its finding is specific and its evidence can be inspected. Keep project count and other existing URLs unchanged until the approved addition is deployed.

**Portfolio path:** `/projects/houston-electricity-plan-audit/`

**Release:** Approved for publication on 31 October 2026. GitHub source: https://github.com/Pratattack/analytics-portfolio/tree/main/projects/2026-10-31/houston-electricity-plan-audit
