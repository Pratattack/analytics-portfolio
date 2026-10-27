# Executive brief: retain the simplest probability benchmark

**Recommendation:** do not promote the credit-augmented model. The intended committee should use the work to audit model claims and plan a vintage-aware study, rather than issue current recession warnings.

| Held-out evidence | Result |
|---|---:|
| Evaluation origins | 192 months, January 2008–December 2023 |
| Positive twelve-month targets | 30 months in two contiguous runs |
| Candidate Brier loss | 0.1676 |
| Yield-curve Brier loss | 0.1750 |
| Expanding unconditional Brier loss | 0.1487 |
| Candidate-minus-curve loss | −0.00736 |
| Paired 24-month block band | −0.06712 to +0.03537 |
| Candidate false alerts / missed positive months at 0.15 | 120 / 2 |

Credit spreads improve ranking and loss relative to the curve-only model in this sample, but the unconditional benchmark has lower Brier loss. Better AUROC does not establish better calibrated probabilities. The low threshold avoids most positive-month misses at the price of many false alerts; its 5:1 cost ratio is assumed.

The tradeoff is evidence depth versus apparent sophistication. More features provide a more interesting story, but do not justify deployment. Retain the adverse benchmark result, request ALFRED vintage and NBER announcement-date reconstruction, then evaluate operational warning costs and independent crisis coverage. The resampling band cannot manufacture independent events.

## Personal understanding

I asked whether corporate-credit conditions add information to the familiar Treasury yield-curve signal. I built each prediction using an expanding historical sample, kept target windows out of future training data, and chose model settings before the later test period. The important result is that a more detailed model can beat one benchmark and still lose to a simpler one.

In an interview I would explain why I withheld model promotion. The probabilities were not strong enough to beat the unconditional baseline, the improvement over the curve model was unstable, and only two crisis-related target runs appeared in the test. Revised data and eventual NBER labels also mean this is retrospective research. A defensible research process includes rejecting a model when its evidence is insufficient.
