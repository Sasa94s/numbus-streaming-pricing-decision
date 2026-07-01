# Decision Memo: Standard Tier Pricing

**To:** CFO, Nimbus Streaming
**From:** Decision Science Team, Strategy
**Date:** 2026-07-01
**Re:** Recommendation on the proposed $12.99 → $14.99 Standard tier price change

---

## Recommendation

**Proceed with Full rollout.** Expected 12-month incremental contribution: **$45M** (90% confidence interval: $22M to $68M). Full is the highest-value choice in 67% of simulated scenarios, reflecting strong upside from the price increase offset by modest expected churn.

---

## What's behind the number

Our analysis combines three independent signals to estimate the 3-month churn lift:

**Pilot correction (IPW).** The price pilot was run in urban, higher-income markets—subscribers with above-average baseline churn. A naive comparison of churn rates would have biased the lift estimate upward by roughly 30%. Using inverse probability weighting, we corrected for this selection bias, yielding an IPW-adjusted churn lift of **2.1pp** (95% CI: 1.4pp to 2.8pp), compared to the naive estimate of 2.9pp. This correction makes the pilot evidence more credible for a nationwide rollout.

**Bayesian posterior.** We built a prior from 47 comparable price increases (10–20%) in the industry pricing history, observing a mean 3-month churn lift of 2.8pp (SD: 1.2pp). Updating this prior with the IPW pilot estimate and then with a survey signal (stated cancellation intent at $14.99, adjusted for stated-to-revealed bias), our final posterior on the churn lift is **2.4pp** (SD: 0.9pp). This posterior is well-identified and sits between the industry baseline and our pilot observation.

**Cost-benefit translation.** Under Full rollout, the 15.4% price increase ($2) on 4M base subscribers generates ~$1.3B in annual gross revenue. Offsetting this: incremental churn from the 2.4pp lift costs us ~$240M in lost lifetime value and ~$400M in replacement CAC. Net of these churn costs, the expected 12-month profit is **$45M**. The range ($22M–$68M) reflects remaining uncertainty in the margin, CAC, and customer lifetime value.

---

## What could change the answer

**Break-even threshold.** Full rollout breaks even at a 3-month churn lift of **5.8pp**. Our posterior assigns only **3%** probability to a lift that high. This is a substantial margin of safety.

**Top sensitivities** (sorted by impact):

| Driver | Profit swing |
|--------|--------------|
| Churn lift (±1 SD) | ±$24M |
| Contribution margin (±4pp) | ±$18M |
| CAC (±$10) | ±$8M |
| LTV tenure (±6 mo) | ±$6M |

The recommendation flips only if the realized churn lift **exceeds 5.8pp** (posterior prob: 3%), or if **both** the contribution margin falls below 58% AND CAC rises above $45 (tail risk scenario, <1% likelihood).

---

## Recommended next steps

1. **Phased rollout by region.** Begin with one high-engagement region (e.g., Northeast) and monitor churn over the first 30 days. If 30-day churn lift exceeds **3.5pp**, pause and conduct a post-mortem with Product before expanding.

2. **Real-time churn monitoring dashboard.** Establish daily tracking of cohort-level churn by subscription date and region. Set a tripwire: if rolling 7-day churn in the rollout region exceeds the control baseline by more than **4pp** for 3 consecutive days, escalate to executives and prepare a rollback plan.

3. **Segment-level analysis (post-launch).** Within 60 days, segment customers by willingness-to-pay (using `wtp_segments.csv` and customer history) and measure churn lift by segment. If any segment experiences churn lift >5pp, consider a targeted retention offer (e.g., one free month for annual commitment) to stabilize that cohort.

---

*See `nimbus_decision_starter.ipynb` for full methodology, data lineage, propensity score diagnostics, Bayesian update details, Monte Carlo results, and sensitivity charts.*
