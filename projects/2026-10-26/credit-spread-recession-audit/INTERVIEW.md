# Resume evidence and interview defense

## Two accurate resume bullets

- Built a reproducible Python/SQL macro-finance pipeline covering 648 monthly origins; evaluated 192 held-out recession-risk classifications using expanding fits, a twelve-month label gap and separate model selection.
- Audited a credit-augmented logistic model against yield-curve and unconditional baselines, documenting Brier losses of 0.1676, 0.1750 and 0.1487, with paired block sensitivity and an offline model-review workbench.

## Five implementation-based questions

**1. Why did you reject a model that beats the curve baseline?** The unconditional benchmark has lower Brier loss, the paired improvement band crosses zero, and only two positive target runs occur. One favorable comparison is insufficient.

**2. How did you reduce leakage?** Features use the previous month; each training origin's full twelve-month target must finish by the prediction origin. Penalties and thresholds use 2000–2006 origins, whose labels finish before the 2008 test. This controls economic-period overlap, but cannot reconstruct historical NBER announcements or source vintages.

**3. Why Brier loss rather than accuracy or AUROC alone?** It scores probability error. Accuracy can look good with rare events, and AUROC measures ranking rather than calibration. The candidate AUROC is about 0.711, but its probabilities still lose to the unconditional benchmark on Brier loss.

**4. What do the block bands establish?** They show sensitivity to resampling dependent historical loss sequences. Blocks of 12/24/36 months challenge the overlap assumption. They do not establish future coverage, remove revisions, or create more independent recessions.

**5. What does the threshold workbench change?** It changes historical review classifications and assumed error costs, not fitted probabilities. The 0.15 threshold came from a 5:1 calibration cost scenario and yields 120 false-alert months and two missed positive months in the test. Those are overlapping months, not 120 independent crises.

Portfolio implementation only; no production deployment, trading returns, employment or real-time forecasting record is implied.
