# Two projects — October 18, 2026

## Healthcare: outpatient access and capacity

This project tests whether appointment policies solve access problems or simply move them between request types. It compares four policies using ten development and thirty holdout demand streams, with a separate set of demand and staffing stress cases. Under the invented assumptions, flexible slot release plus four extra staffed slots per day meets both access targets, at an additional modeled cost of $53,600 over the evaluation window. All requests and staffing parameters are synthetic.

My understanding: I should distinguish faster booking from higher eventual visit volume or profitability. Protected urgent slots can hurt routine access unless unused slots are released, and staffing can be the actual bottleneck. I would defend the recommendation by showing both request groups, the unbooked denominator, the paired comparison and the extra cost. I would also explain that the model's no-abandonment assumption means faster access does not create additional eventual visits in this simulation.

## Urban mobility: forecasting and capacity economics

This project forecasts observed bike-share rentals using only information available before the planning day, selects among five models on an earlier validation window, and evaluates 184 subsequent days. The selected ridge model achieves test WAPE of 13.35%, compared with 18.70% for a seven-day baseline. Hypothetical capacity costs imply $145,115 less cost on that historical test period, with empirical interval coverage below the nominal target. The rentals are public 2011–2012 data; costs and capacity policies are invented.

My understanding: Better prediction is useful only when it improves an actual decision. I can explain how different costs for shortages and unused capacity lead to a buffered capacity rule, why target-derived variables would leak the answer, and why time-series evaluation must preserve the information timeline. I would describe the savings as modeled rather than realized, and I would not claim this dataset can determine bike counts or measure lost demand.

## Verification and publication

Each project includes ten unit tests plus independent integration/reconciliation checks and a clean byte-identical output rebuild. Verification JSON files and test logs are bundled. These are three automated verification stages, not three independent human reviews. HTML structure and SVG markup are checked; no full browser visual review is claimed. Source code and reports are published in a public portfolio, not hosted as live operating applications.

The daily project task is enabled for 13:13 America/Chicago, beginning October 19. Automatic model selection is used because the scheduler does not expose a model selector.
