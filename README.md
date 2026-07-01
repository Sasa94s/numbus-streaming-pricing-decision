# Price It Right — Nimbus Streaming Pricing Decision

**Status: ✅ Complete**

This repository contains the completed analysis for the *Price It Right* capstone project (Udacity Applied Statistics Nanodegree, Course 4).

**Decision**: Recommend **Full rollout** of the $12.99 → $14.99 Standard tier price increase. Expected 12-month incremental contribution: **$45M** (90% confidence interval: $22M–$68M).

## Analysis Overview

You're a Decision Scientist at Nimbus Streaming, tasked with recommending whether to raise the Standard tier from $12.99 to $14.99 (15.4% increase) across 4M subscribers. The analysis combines:

- **IPW Propensity Scoring**: Corrects for urban/high-income bias in the price pilot
- **Bayesian Updating**: Integrates industry benchmarks, pilot data, and survey intent into a posterior on churn lift
- **Cost-Benefit Modeling**: Translates churn uncertainty into dollar outcomes for 4 strategic options
- **Monte Carlo Simulation**: Propagates uncertainty through 10K scenarios
- **Decision Theory**: Evaluates options under Expected Value, CRRA utility, and Minimax Regret

## Repo Layout

```
.
├── data/                              # five input CSVs
│   ├── pilot_data.csv                 # 50k subscribers, pilot vs. control
│   ├── industry_pricing_history.csv   # 150+ comparable price increases
│   ├── pre_announcement_survey.csv    # 5k respondents, stated intent at $14.99
│   ├── finance_forecast.csv           # 12-month forecast, margin, CAC, LTV
│   └── wtp_segments.csv               # 4 WTP segments (optional standout analysis)
├── src/
│   ├── nimbus_decision_starter.ipynb         # full analysis (executable, 43 cells)
│   ├── decision_memo.md                      # CFO recommendation memo (BLUF format)
│   ├── assumptions_and_sources.md            # methodology & limitations (275 lines)
│   └── decision_memo_template.md             # original template (reference)
├── PROJECT.md                         # project requirements & rubric
└── README.md                          # this file
```

## Deliverables

### 1. `src/nimbus_decision_starter.ipynb` (38 KB)
Fully executed Jupyter notebook with all outputs visible. Sections:
- **Setup**: Load 5 datasets, extract constants
- **Naive Churn Lift**: Baseline estimate (biased upward)
- **Covariate Imbalance & Propensity Model**: SMDs, logistic regression, overlap check
- **IPW Estimation & Bootstrap**: 300 bootstrap iterations, 95% CI on pilot lift
- **Bayesian Prior**: Industry comparables (10–20% price increases)
- **Posterior Updates**: Sequential updates with pilot, then survey data
- **Bayesian Visualization**: Prior and two posteriors on same plot
- **Cost-Benefit Functions**: Option-specific profit calculations (Full/NewOnly/Delay/Hold)
- **Monte Carlo**: 10K simulations over 4 uncertain inputs
- **Profit Distributions**: Histograms and summary statistics by option
- **Decision Tree**: Profits at 25th/50th/75th percentile churn lift states
- **Decision Theory**: EV, CRRA utility (γ=2.0), Minimax Regret rankings
- **Sensitivity Analysis**: Tornado chart, break-even lift, scenario win-share
- **Robustness**: Percentage of scenarios where recommended option wins

### 2. `src/decision_memo.md` (3.8 KB)
One-page executive memo to CFO:
- **Recommendation (BLUF)**: Full rollout, $45M expected profit, 90% CI
- **What's Behind the Number**: IPW correction, Bayesian posterior, cost-benefit translation
- **What Could Change the Answer**: Break-even lift (5.8pp), top sensitivities, conditions for flip
- **Next Steps**: 3 actions including real-time churn monitoring tripwire

### 3. `src/assumptions_and_sources.md` (14 KB)
Comprehensive technical documentation:
- **Data Lineage**: Source, size, key columns for each input
- **IPW Methodology**: Covariate imbalance, propensity model, bootstrap procedure
- **Bayesian Updating**: Prior construction, conjugate Normal-Normal formula, stated-to-revealed adjustment
- **Cost-Benefit Model**: Option definitions, assumptions (tenure, pricing, research cost)
- **Monte Carlo**: Distributions, ranges, and rationale for each uncertain input
- **Decision Theory**: EV, CRRA utility function, Minimax regret definition
- **Sensitivity Analysis**: Tornado ranges, break-even derivation, win-share metric
- **Known Limitations**: 6 documented caveats (survey proxy, segment heterogeneity, lag effects, competitive response, etc.)
- **Reproducibility**: Random seed fixed for exact replication

## Key Findings

| Metric | Value |
|--------|-------|
| IPW-corrected churn lift | 2.1pp (95% CI: 1.4–2.8pp) |
| Posterior mean (after Bayesian updates) | 2.4pp |
| Expected 12-month profit (Full) | $45M |
| 90% confidence interval | $22M–$68M |
| Break-even churn lift | 5.8pp (posterior prob: 3%) |
| Full rollout win-share | 67% of simulated scenarios |
| Top sensitivity | Churn lift (±$24M) |

## How to Run

### Jupyter Notebook (Interactive)

```bash
# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install pandas numpy scipy statsmodels matplotlib seaborn jupyter

# Launch notebook
jupyter notebook src/nimbus_decision_starter.ipynb
```

The notebook runs top-to-bottom from a fresh kernel. All cells produce outputs and plots.

### Verify Execution

```bash
# Check that notebook was executed with outputs
python3 -c "import json; nb = json.load(open('src/nimbus_decision_starter.ipynb')); print(f'✓ {len([c for c in nb[\"cells\"] if c.get(\"outputs\")])} cells have outputs')"
```

## Project Requirements Met

✅ All cells in notebook execute top-to-bottom from fresh kernel  
✅ Five datasets loaded into named DataFrames  
✅ Decision & outcome metric stated; key uncertainty identified  
✅ Covariate imbalance measured (SMD); IPW implemented with 300 bootstrap iterations  
✅ Propensity scores computed & overlap verified  
✅ Prior built from industry comparables (10–20% price increase band)  
✅ Normal-Normal conjugate updates applied (prior → Posterior 1 → Posterior 2)  
✅ Survey likelihood computed with stated-to-revealed adjustment (0.50)  
✅ Bayesian visualization (prior & both posteriors)  
✅ Cost-benefit model: all 4 options with documented assumptions  
✅ Monte Carlo: 10K simulations, uncertain inputs drawn from appropriate distributions  
✅ Decision tree: 4 options × 3 states of world  
✅ Decision theory: EV, CRRA utility, Minimax regret evaluated  
✅ Sensitivity analysis: tornado chart, break-even lift, robustness win-share  
✅ Decision memo: BLUF, sensitivities, next steps including monitoring tripwire  
✅ Assumptions document: full methodology, lineage, limitations  

## Optional Standout Elements

- ✅ **Well-defended recommendation**: Full rollout supported across all three decision criteria (EV, CRRA, Minimax Regret)
- 🔄 **AIPW (doubly-robust estimator)**: Not implemented in base case; can be added as future enhancement
- 🔄 **Hybrid WTP-based pricing**: `wtp_segments.csv` available but not used in base recommendation; potential for segment-level analysis

## Notes

- **Random seed**: Fixed (`RNG = np.random.default_rng(7)`) for reproducible Monte Carlo draws
- **Plots**: All matplotlib output renders in Jupyter; saved as cell outputs
- **Units**: Churn lift in percentage points; profits in dollars, summary tables in millions
- **Margin of safety**: Break-even lift (5.8pp) is 2.4× the posterior mean (2.4pp), with <3% probability of being breached
