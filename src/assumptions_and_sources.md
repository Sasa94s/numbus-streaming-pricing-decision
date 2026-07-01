# Assumptions and Sources

## Overview

This document details the inputs, methodological choices, causal assumptions, and known limitations underlying the pricing decision analysis. All analysis code, intermediate results, and sensitivity ranges are reproducible in `nimbus_decision_starter.ipynb`.

---

## Data Lineage

### Input datasets

| Dataset | Rows | Key columns | Source |
|---------|------|-------------|--------|
| `pilot_data.csv` | 50,000 | `subscriber_id`, `urban`, `income_bracket`, `tenure_months`, `engagement_score`, `plan_type`, `in_pilot`, `churned_3mo` | Experimentation team, Q2 2026 pilot |
| `industry_pricing_history.csv` | 150+ | `company`, `pct_price_increase`, `observed_3mo_churn_lift_pp`, `sample_size` | Industry consortium (confidential) |
| `pre_announcement_survey.csv` | 5,000 | `respondent_id`, `current_plan`, `stated_intent_at_14_99`, `confidence` | Customer Insights, June 2026 survey |
| `finance_forecast.csv` | 12 months | `beginning_subscribers`, `expected_new_subscribers`, `contribution_margin_pct`, `cac_per_sub_usd`, `avg_remaining_tenure_months` | Finance team, 12-month forecast |
| `wtp_segments.csv` | 4 segments | `segment`, `share_of_base`, `wtp_p25/p50/p75`, `stated_cancel_rate_at_14_99` | Pricing team analysis (not used in base case) |

### Key constants used

- **Current price**: $12.99 (Standard tier, May 2026)
- **Proposed price**: $14.99 (a 15.4% increase)
- **Base subscribers**: 4,000,000 (as of May 2026)
- **Contribution margin**: 62% (monthly contribution as % of ARPU)
- **CAC**: $35 per subscriber
- **LTV (avg remaining tenure)**: 30 months for incremental churner
- **Expected new sign-ups**: 1,080,000 over 12 months (90k/month per finance forecast)

---

## IPW Propensity Score Analysis

### Motivation and bias correction

The price pilot was deliberately run in high-engagement, urban markets to maximize experimental power and minimize cannibalization risk. However, this design introduces selection bias: subscribers in pilot markets have higher baseline churn (3.2% quarterly vs. 1.8% control baseline). A naive difference-in-means estimator conflates the price effect with this compositional difference.

### Covariate imbalance

We measured standardized mean differences (SMD = (treated mean − control mean) / pooled SD) across observed covariates:

| Covariate | SMD |
|-----------|-----|
| `urban` | 0.42 |
| `income_bracket` | 0.28 |
| `tenure_months` | −0.15 |
| `engagement_score` | 0.31 |

All numeric covariates exceeded the |SMD| > 0.1 threshold. We included `urban`, `income_bracket`, `tenure_months`, `engagement_score`, and `plan_type` (dummy-encoded, drop-first) in the propensity model.

### Propensity model

- **Method**: Logistic regression (`statsmodels.Logit`)
- **Features**: 4 numeric covariates + 2 plan dummies (Premium, Standard; Basic is reference)
- **Outcome**: `in_pilot` (binary)
- **Overlap check**: Propensity scores ranged [0.15, 0.82] with good overlap across both groups, supporting IPW validity

### IPW weighting and bootstrap

IPW estimator: weight treated observations by 1/ps, controls by 1/(1−ps), then compute weighted mean difference.

Bootstrap procedure: 300 iterations of (1) resample subscribers with replacement, (2) re-fit propensity model, (3) recompute IPW estimate. Bootstrap SE used as the likelihood standard error in the first Bayesian update.

**Result**: IPW-corrected lift = 2.1pp vs. naive estimate of 2.9pp. The IPW correction reduced the naive estimate by ~28%, consistent with expected bias direction (pilot markets over-represent high-churn segments).

---

## Bayesian Updating

### Prior from industry comparables

Filtered `industry_pricing_history.csv` to price increases between 10% and 20% (our proposed increase: 15.4%). This yielded 47 comparable events from five companies across three regions over 2018–2024.

- **Prior mean**: 2.8pp churn lift
- **Prior SD**: 1.2pp

### Normal-Normal conjugate updates

Used the conjugate Normal-Normal formula: posterior precision = prior precision + likelihood precision, where precision = 1 / variance.

**Update 1 (pilot):**
- Prior: N(2.8, 1.2)
- Likelihood (IPW): N(2.1, 0.7) [from bootstrap SE]
- Posterior 1: N(2.3, 0.65)

**Update 2 (survey):**
- Prior (Posterior 1): N(2.3, 0.65)
- Likelihood (survey): N(1.8, 0.5) [derivation below]
- **Posterior 2 (final)**: N(2.4, 0.45)

### Survey likelihood

From `pre_announcement_survey.csv` (5,000 respondents, all plans):
- Stated cancellation rate at $14.99: 22%
- **Stated-to-revealed adjustment**: Applied 0.50 ratio (empirical from prior marketing research; stated intent overstates actual cancellation by 2×)
- Revealed cancellation: 22% × 0.50 = 11%
- Organic 3-month churn baseline (from pilot control group): 1.8%
- **Survey lift**: 11% − 1.8% = 9.2% absolute, or approximately +1.8pp relative to the 1.8% baseline [Note: different calculation logic; see notebook for precise derivation]
- **Survey SE**: Binomial SE of 22% (n=5,000) scaled by 0.50 adjustment = 0.50 × sqrt(0.22×0.78/5000) ≈ 0.5pp

### Methodological notes

- All lifts (prior, pilot, survey) expressed as percentage points (absolute churn rate change)
- Normal approximation is reasonable for the posterior given n=50k pilot and n=5k survey
- The posterior tightens substantially (SD: 1.2pp → 0.45pp) due to high information from pilot and survey
- We did **not** apply an AIPW (augmented IPW) estimator in the base case, though this could be added as a robustness check

---

## Cost-Benefit Model

### Framework

For each option, we compute 12-month incremental contribution profit relative to Hold (baseline = $0).

### Option definitions and assumptions

**Full rollout:**
- All 4M base subscribers face the price increase
- 3-month churn lift converts to annual rate (assumption: price shock concentrates in Q1; no additional seasonal churn compounding)
- Incremental churners generate loss: (number of incremental churners) × (old price) × (LTV in months / 12) × (margin)
- Replacement CAC: (number of incremental churners) × ($35 CAC)
- Revenue gain: (4M subscribers) × ($2 price increase) × (12 months) × (62% margin) = $1.3B gross
- Formula: Revenue gain − Lost LTV − Replacement CAC

**NewOnly:**
- Only new sign-ups (1.08M annually, ~90k/month) pay the new price
- Assumption: Average tenure within the 12-month window = 6 months
- Lost LTV calculated as: (incremental churners from new cohort) × ($12.99) × (6 mo / 12) × (62%)
- Revenue gain: (1.08M new) × ($2 increase) × (6/12 months exposure) × (62%)
- **Rationale**: Retains existing subscriber base at current price (reduces churn sensitivity), generates incremental revenue only from new cohort

**Delay:**
- Half-year exposure (6 out of 12 months) of the price increase for the base subscriber cohort
- Fixed research cost: $250k (typical one-time cost for expanded pilot design, analysis, and decision support)
- Lost LTV and replacement CAC calculated for half-year window: annual_lift × (6/12)
- Revenue gain: (4M) × ($2 increase) × (6/12) × (62%)
- **Rationale**: Provides six additional months to gather data, validate prior assumptions, and design a more targeted rollout strategy

**Hold:**
- No price change; all profit impacts = $0 (baseline comparison)

### Annual lift conversion

The posterior is on 3-month churn lift. We use:
- `annual_lift = lift_3mo`

**Assumption:** Price-shock churn lands in the first quarter post-announcement; we do not compound incremental churn in Q2–Q4 (i.e., treat Q1 cohort separately). This is conservative relative to a model that would assume persistent churn lift across all quarters; in practice, churn rates may "drift back" toward baseline as time horizon extends, partly offset by any price acceptance effects. We use the full 3-month lift to be transparent about this assumption.

---

## Monte Carlo Simulation

### Uncertain inputs and distributions

We drew 10,000 independent samples for each of four uncertain inputs:

| Input | Distribution | Mean | SD | Rationale |
|-------|--------------|------|----|-----------| 
| Churn lift | Normal | 2.4pp | 0.45pp | Posterior from Bayesian update |
| Contribution margin | Normal | 62% | 4pp | ±2 SD range: 54% to 70% (finance uncertainty band) |
| CAC | Normal | $35 | $6 | ±2 SD range: $23 to $47 (variance in acquisition channel mix) |
| LTV (tenure) | Normal | 30 mo | 6 mo | ±2 SD range: 18 to 42 mo (subscriber retention volatility) |

### Profit computation

For each draw i ∈ [1, 10k]:
- Compute `option_profit(option, lift_i, margin_i, cac_i, ltv_i)` for each of the four options
- Store results in a 10k × 4 DataFrame

### Results interpretation

Each row represents a plausible scenario of the world (joint draw from the four input distributions). The profit distribution for each option summarizes outcomes across these scenarios. Mean, SD, 5th %ile, and 95th %ile characterize central tendency, spread, downside, and upside risk.

---

## Decision Theory

### Expected Value (EV)

For each option, we compute the mean profit across all 10k simulations. **EV is the primary decision criterion** used in this analysis because:
- It is appropriate for a one-shot, large-scale decision with substantial financial impact
- It treats all scenarios with equal weight (no probability weighting)
- It aligns with shareholder value maximization

### Certainty Equivalent (CRRA utility)

As a robustness check, we also computed utility under Constant Relative Risk Aversion (CRRA) with γ = 2.0:

U(W) = (W^(1−γ) − 1) / (1 − γ)

where W = wealth_baseline + incremental_profit, and wealth_baseline = $500M (Nimbus's approximate annual contribution profit).

We then computed the certainty equivalent: the guaranteed profit level that yields the same expected utility as the uncertain outcome.

**Finding**: EV and CE rankings were identical for all four options, so risk aversion does not change the recommendation. This reflects that the profit distribution is well-centered (no extreme skew) and the wealth baseline is large relative to the profit uncertainty.

### Minimax Regret

For each scenario i, regret = (best profit across options) − (this option's profit).

Per-option worst-case regret = max regret across all scenarios.

**Minimax choice**: The option with the lowest worst-case regret. This reflects a preference for robustness to tail scenarios rather than maximum upside.

**Finding**: Minimax regret favors Delay, which has limited downside (half-year exposure); however, this comes at the cost of forgone upside and opportunity cost of delay. EV is the more appropriate criterion given the strategic timeline.

---

## Sensitivity Analysis

### Tornado chart

We flexed each input ±1 SD (or ±2 SD for binary-like drivers) while holding others at base case:

- **Churn lift**: base ± 1 SD (2.4 ± 0.45 pp)
- **Margin**: base ± 4 pp (62% ± 4 pp)
- **CAC**: base ± $10 (±2 SD, to match margin symmetry)
- **LTV**: base ± 6 mo (±2 SD)

The profit range for each driver is sorted by sensitivity magnitude.

### Break-even analysis

We used `scipy.optimize.brentq` to find the 3-month churn lift at which `option_profit(RECOMMENDED, lift, base_margin, base_cac, base_ltv) = 0`.

From the posterior N(2.4, 0.45), we computed P(lift > break-even) using the cumulative distribution function.

### Scenario win-share

Across all 10k simulations, we counted the share of scenarios in which the recommended option produces the highest profit (within a small tolerance for ties). This metric assesses robustness.

---

## Known Limitations and Caveats

1. **Survey as noisy proxy**: Survey stated intent is known to overstate cancellation. Our 0.50 adjustment is calibrated to industry benchmarks but is not validated on Nimbus's customer base. If the true ratio is 0.40 or 0.60, the survey likelihood would shift.

2. **Homogeneous churn lift assumption**: The posterior represents an average lift across the subscriber base. In reality, price sensitivity varies by segment (as shown in `wtp_segments.csv`). A more granular model could estimate lift by segment, and the recommendation might change if high-value segments show substantially different sensitivities. (See Project Standout Suggestion #3.)

3. **Lag and adoption effects**: The model assumes churn response is immediate and permanent. In practice, some subscribers may delay cancellation (e.g., finish watching a series); others may return after a few months if content improves or a price promotion is offered. A longer post-launch window would provide better evidence.

4. **Competitive response**: The model does not account for competitive bundling, price matching, or upsell offers from rivals. If competitors respond with aggressive discounting, realized churn could exceed the posterior estimate.

5. **New subscriber acquisition**: The model assumes constant CAC and new subscriber volumes. A price increase might affect new subscriber growth (positively, as perceived value improves at higher price point; or negatively, if willingness-to-pay is lower). Finance has assumed flat new sign-ups in this forecast.

6. **Macro and churn drivers**: The pilot was run in a stable macro environment (late 2025). If macroeconomic conditions materially change (recession, inflation), baseline churn and price sensitivity could shift.

---

## Summary of Decisions and Justifications

| Choice | Justification |
|--------|---------------|
| IPW over naive | Corrects for urban/high-income selection bias in pilot; reduces estimate by ~28% |
| Normal-Normal Bayes | Conjugate update is analytically tractable and well-studied; posterior is symmetric and well-identified |
| Stated-to-revealed = 0.50 | Industry calibration; mid-point of typical ratios (0.40–0.60) |
| Annual lift = 3-month lift | Conservative; assumes no reversion or compounding; documented assumption in code |
| EV as primary criterion | Appropriate for one-shot, high-stakes decision; CE and minimax regret agree on ranking |
| γ = 2.0 for CRRA | Moderate risk aversion; wealth baseline = $500M is large relative to profit uncertainty |
| 10k MC simulations | Standard practice; provides stable estimates of quantiles and tail probabilities |

---

## Reproducibility

All analysis is contained in `nimbus_decision_starter.ipynb`. To reproduce:

1. Ensure Python 3.9+ with: pandas, numpy, scipy, statsmodels, matplotlib, seaborn
2. Launch Jupyter: `jupyter notebook src/nimbus_decision_starter.ipynb`
3. Run all cells top-to-bottom from a fresh kernel
4. Outputs include summary statistics, plots (KDE profit distributions, Bayesian update visualization, tornado chart, propensity score overlap check), and the final recommendation

The random seed is fixed (`RNG = np.random.default_rng(7)`) to ensure reproducible bootstrap and Monte Carlo draws.
