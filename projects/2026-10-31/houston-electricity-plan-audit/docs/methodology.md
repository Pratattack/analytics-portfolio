# Methodology

## Data and transcription

Provider-issued residential Electricity Facts Labels were retrieved on 31 October 2026. See the exact UTC timestamp, final URL, byte size and hash in the source manifest. Document dates are distinct from retrieval dates. Pricing terms were manually transcribed into structured JSON and checked against the original labels, including visual checks of credit thresholds, base charges, delivery charges and contract terms. This is not a validated universal PDF parser.

The original 15-25-plan aspiration was narrowed after source retrieval to seven contracts with auditable monthly arithmetic. The resulting sample is not representative of the Houston market. Eleven complete PDFs were obtained from twenty-one candidate URLs. Failures, malformed downloads and incompatible contracts remain visible in the exclusion register.

## Recurring monthly calculation

Let q be billed kWh and d be billing days. The model is:

`Bill = q * (energy_cents + delivery_cents) / 100 + base_dollars + d * daily_dollars + fixed_delivery_dollars - eligible_credit_dollars`.

Credit rules use their exact inequalities. The $125 Bundle and Frontier credits apply at q >= 1,000. The historical $15 Payless credit applies at q <= 500 and is prorated for cycles shorter than 30 days. Its fixed delivery amount is also prorated for shorter cycles. The comparison profiles use 30-day cycles to match the modeled daily-charge assumptions. Plans with no daily charges use their per-cycle fixed charge.

No interpolation between the 500/1,000/2,000-kWh disclosure prices is used. The function is evaluated directly. The model permits a bill discontinuity rather than smoothing it away.

## Two delivery bases

1. **As-issued audit:** each label's disclosed delivery charges. Discount Power's labels that refer readers to a delivery table use that provider's table dated 4 October 2026, which reconciles the published examples.
2. **Normalized scenario:** $4.90 per cycle plus 6.5333 cents/kWh for every selected plan. Only delivery terms change. Older energy terms remain historical.

The source table is a provider-published tariff summary, not a separately reconciled full PUCT tariff filing. No later tariff change or address-specific surcharge is modeled.

## Validation

At each disclosed usage q, compare `100 * modeled_bill / q` with the source's published average cents/kWh. A residual no greater than 0.05 cents/kWh is consistent with rounding to one decimal cent. Display rounding is applied only after full-precision calculations. Python uses Decimal arithmetic for bill components; JavaScript uses floating-point arithmetic, with cross-language totals tested to eight decimal places across 189 input combinations.

The 21 test methods include credit boundaries, invalid inputs, daily charges, proration, contract duration, SQL reconciliation, source hashes when PDFs are available and the $750 scenario identity. These checks are automated; they are not independent human reviews. Interaction, keyboard behavior and mobile rendering have not been tested in a browser because the user excludes browser operation.

## Equal-total scenario

Steady: twelve cycles at 1,000 kWh. Uneven: 700, 650, 700, 800, 1,000, 1,300, 1,600, 1,600, 1,300, 1,000, 700, 650. Both sum to 12,000 kWh. The latter profile is a constructed illustration, not an empirical Houston usage shape. Six cycles qualify for credits instead of twelve. Difference: `6 * $125 = $750`.

## Pairwise crossing

For the two specified Discount Power contracts, common fixed and delivery components cancel. Above the credit threshold, solve `(12.7426 - 9.5137) * q / 100 - 125 = 0`, yielding approximately 3,871.29 kWh. This does not imply the contracts are interchangeable: duration and termination fees differ.

## Exclusions and limitations

No taxes, deposits, optional services, payment penalties, special municipal charges, uncertain passthroughs or other nonrecurring charges are included. EFL exit-fee amounts are shown separately; they are not added to a comparison that assumes no early termination. Move exemptions require provider verification. Paperless and prepaid requirements are retained as metadata, not valued monetarily.

Time-of-use plans require interval data; solar plans require export data and eligibility evidence. They are excluded from ranking. An OhmConnect label contains unquantifiable ERCOT pass-throughs, so its displayed average is not treated as a complete reproducible bill. Six- and nine-month contracts are excluded from twelve-cycle scenarios. The Payless document's reserved pricing discretion means unchanged multi-cycle charges are an explicit hypothetical assumption.

No estimates of demand elasticity, customer response, causal effects, typical household costs, expected savings or provider misconduct are attempted.
