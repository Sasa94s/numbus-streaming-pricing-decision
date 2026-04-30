# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Price It Right — Nimbus Streaming pricing decision (STARTER)
#
# **Your role.** You're a Decision Scientist on the Strategy team at Nimbus
# Streaming. The CFO is weighing a 15.4% price increase on the Standard tier
# (\$12.99 → \$14.99). You have inputs from Finance, Experimentation, and
# Customer Insights, and you need to deliver a recommendation.
#
# **The four options on the table.**
#
# 1. **Full rollout** — raise price for all 4M Standard subscribers.
# 2. **New customers only** — keep existing subs at \$12.99; new sign-ups pay \$14.99.
# 3. **Delay & larger pilot** — postpone 6 months, expand pilot, then decide.
# 4. **Hold** — keep price flat.
#
# **What you'll do.** Eight steps, each with a `# TODO` block. By the end you'll
# produce a 1-page decision memo to the CFO.

# %% [markdown]
# ## 0. Setup

# %%
from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
sns.set_theme(style="whitegrid", context="notebook")
RNG = np.random.default_rng(7)

# TODO: load each of the five CSV files in ../data/ into named DataFrames.
DATA_DIR = Path("../data")
pilot     = ...  # pilot_data.csv         — subscriber-level outcomes from the price pilot
industry  = ...  # industry_pricing_history.csv — past competitor price moves
survey    = ...  # pre_announcement_survey.csv  — stated intent at $14.99
finance   = ...  # finance_forecast.csv         — 12-month subs + financial constants
wtp       = ...  # wtp_segments.csv             — segment willingness-to-pay

# Sanity print
# print(pilot.shape, industry.shape, survey.shape, finance.shape, wtp.shape)

# %% [markdown]
# ## 1. Restate the question
#
# Before any modeling, write down the decision you're making and pull the
# financial constants you'll reuse throughout. These come from the Finance
# team's 12-month forecast.
#
# > **Decision:** which of the four options to recommend.
# > **Outcome metric:** _(you decide — write it here)_
# > **Key uncertainty:** _(you decide — write it here)_

# %%
# TODO: pull these scalar inputs from `finance` and `wtp` and store them as
# module-level constants you can reuse below.
PRICE_TODAY        = ...   # current Standard tier price ($12.99)
PRICE_PROPOSED     = ...   # proposed Standard tier price ($14.99)
MARGIN_PCT         = ...   # contribution margin %
CAC                = ...   # customer acquisition cost (USD per sub)
LTV_MONTHS         = ...   # avg remaining tenure of an incremental churner (Finance estimate)
N_BASE             = ...   # current Standard subs
EXPECTED_NEW_12MO  = ...   # forecasted new sign-ups over the 12-month horizon

# Quick gut-check print
# print(f"+{(PRICE_PROPOSED - PRICE_TODAY) / PRICE_TODAY * 100:.1f}% increase, "
#       f"{N_BASE:,} base subs, margin {MARGIN_PCT:.0%}, CAC ${CAC:.0f}")

# %% [markdown]
# ## 2. Validate the pilot's churn-lift estimate (IPW)
#
# The junior analyst on the Experimentation team handed you a "naive" churn
# lift — just the difference in 3-month churn between pilot and control
# markets. Pilot markets were preferentially **urban / higher-income**, and
# those subscribers also have higher *baseline* churn. So the naive number is
# (probably) biased.
#
# Plan:
#
# 1. Compute the naive lift.
# 2. Quantify covariate imbalance between pilot and control.
# 3. Fit a propensity model `P(in_pilot | covariates)`.
# 4. Confirm overlap.
# 5. Compute an IPW-adjusted lift and a bootstrap CI.

# %% [markdown]
# ### 2.1 Naive estimate

# %%
# TODO: compute the naive 3-month churn lift (treated mean − control mean).
naive_lift = ...
# print(f"Naive 3-month churn lift: {naive_lift * 100:.2f} pp")

# %% [markdown]
# ### 2.2 Covariate imbalance — evidence of confounding

# %%
def standardized_mean_diff(df: pd.DataFrame, var: str, treat: str = "in_pilot") -> float:
    """Standardized mean difference of `var` between treated and control.
    |SMD| > 0.1 is a common rule of thumb for meaningful imbalance.
    """
    # TODO
    raise NotImplementedError


# TODO: produce a DataFrame of unweighted SMDs for the numeric covariates.

# %% [markdown]
# ### 2.3 Propensity model

# %%
# TODO:
#   1. Build a feature matrix from the pilot covariates (numeric + plan_type dummies).
#   2. Add a constant and fit a logistic regression with statsmodels for P(in_pilot | X).
#   3. Predict the propensity scores. Trim to [0.02, 0.98] to enforce overlap.
ps_model = ...
ps       = ...

# %% [markdown]
# ### 2.4 Overlap check
#
# Plot KDEs of the propensity scores for treated vs. control. They should
# overlap across the full support; if they don't, IPW is unsafe.

# %%
# TODO: KDE plot of propensity scores by treatment.

# %% [markdown]
# ### 2.5 IPW estimate + bootstrap 95% CI

# %%
def ipw_estimate(df: pd.DataFrame, ps: np.ndarray) -> float:
    """Hájek IPW estimate of the average treatment effect on the treated outcome."""
    # TODO
    raise NotImplementedError


def bootstrap_ipw(df: pd.DataFrame, n_boot: int = 300, rng=RNG) -> np.ndarray:
    """Resample subscribers with replacement, refit the propensity model, and
    return an array of IPW estimates. Use this to construct a 95% CI."""
    # TODO
    raise NotImplementedError


# TODO: compute point IPW estimate, bootstrap CI, and bootstrap SE.
PILOT_LIFT_MEAN = ...   # IPW point estimate of the 3-month churn lift
PILOT_LIFT_SE   = ...   # bootstrap SE of the IPW estimate

# print(f"Naive lift:         {naive_lift * 100:6.2f} pp")
# print(f"IPW point estimate: {PILOT_LIFT_MEAN * 100:6.2f} pp")
# print(f"Bootstrap SE:       {PILOT_LIFT_SE * 100:.2f} pp")

# %% [markdown]
# **Write a one-line conclusion.** Was the naive estimate biased? In which
# direction? By how much?

# %% [markdown]
# ## 3. Bayesian updating — combine prior, pilot, and survey
#
# We model belief about the **3-month churn lift** Δ as Normal. Two sequential
# Normal-Normal conjugate updates fold in the pilot first, then the survey.
#
# Steps:
#
# 1. Build a prior from the industry pricing history (filter to comparable
#    price increases).
# 2. Update with the IPW pilot lift to get **Posterior 1**.
# 3. Convert the survey's stated cancel intent into a noisy lift estimate
#    (apply a stated→revealed ratio and subtract organic baseline churn).
# 4. Update with the survey to get **Posterior 2** (the final posterior).

# %% [markdown]
# ### 3.1 Prior from industry history

# %%
# TODO: filter the industry table to events with pct_price_increase between
# 10% and 20% (comparable to ours) and use those observations to set a prior:
#   prior_mean (mean of `observed_3mo_churn_lift_pp` / 100)
#   prior_sd   (standard deviation of the same)
prior_mean = ...
prior_sd   = ...

# %% [markdown]
# ### 3.2 First update — combine prior with pilot likelihood

# %%
def normal_update(prior_mu: float, prior_sd: float,
                  lik_mu: float, lik_sd: float) -> tuple[float, float]:
    """Conjugate Normal-Normal update.
    Posterior precision = prior precision + likelihood precision.
    Returns (posterior_mean, posterior_sd).
    """
    # TODO
    raise NotImplementedError


# TODO: apply normal_update with (prior_mean, prior_sd) and (PILOT_LIFT_MEAN, PILOT_LIFT_SE).
post1_mu, post1_sd = ..., ...

# %% [markdown]
# ### 3.3 Survey likelihood — stated → revealed adjustment
#
# Surveys overstate cancellation. A common adjustment is to multiply the
# stated cancel rate by a **stated-to-revealed ratio** ≈ 0.5. The result is
# a *cancellation* rate; subtract baseline organic 3-month churn to get a
# lift on the same scale as the pilot. The SE scales with the binomial SE of
# the stated-cancel proportion times the same ratio.

# %%
STATED_TO_REVEALED = 0.50

# TODO:
#   - compute organic 3-month churn from the finance forecast
#   - compute stated cancel rate from the survey
#   - convert to revealed rate, then to a lift (subtract organic baseline)
#   - compute the survey lift's SE
ORGANIC_3MO_CHURN  = ...
survey_lift_mean   = ...
survey_lift_se     = ...

# %% [markdown]
# ### 3.4 Second update — combine posterior 1 with the survey

# %%
# TODO: produce final posterior parameters POSTERIOR_MU, POSTERIOR_SD.
POSTERIOR_MU, POSTERIOR_SD = ..., ...

# %% [markdown]
# ### 3.5 Visualize the updates
#
# Plot the prior, posterior 1, and posterior 2 on the same axes. The
# posterior should tighten and shift relative to the prior.

# %%
# TODO: density plot of three Normal pdfs (use scipy.stats.norm.pdf).

# %% [markdown]
# ## 4. Cost-benefit model + Monte Carlo
#
# Build a function that returns 12-month *incremental* contribution profit
# (relative to Hold) for a given option, churn lift, margin, CAC, and LTV.
# Then run ~10K Monte Carlo draws over the uncertain inputs.
#
# Modeling guidance:
#
# - Treat the 3-month posterior lift as the *full annual* incremental churn
#   (price-shock churn lands in Q1; don't compound).
# - Lost value per incremental churner ≈ `lost_subs × OLD_PRICE × LTV_months × margin`.
# - Replacement CAC adds once per lost subscriber.
# - For "Delay", you only get 6 months of price-uplift exposure, with a
#   small fixed research cost (assume ~\$250k).
# - For "New only", the existing base is unaffected; only new sign-ups face
#   the new price (use `EXPECTED_NEW_12MO` and an avg ~6 months of in-window
#   tenure for new subs).

# %%
def annual_lift_from_3mo(lift_3mo):
    """Convert the 3-month posterior lift to an annual incremental-churn rate."""
    # TODO (one-liner; defensible choice — document your assumption)
    raise NotImplementedError


def option_profit(option: str, lift_3mo: float, margin: float,
                  cac: float, ltv_months: float) -> float:
    """Incremental 12-month contribution profit relative to Hold.
    Implement branches for: 'Full', 'NewOnly', 'Delay', 'Hold'.
    """
    # TODO
    raise NotImplementedError


OPTIONS = ["Full", "NewOnly", "Delay", "Hold"]

# TODO: deterministic point estimates using the posterior mean.
# det = {opt: option_profit(opt, POSTERIOR_MU, MARGIN_PCT, CAC, LTV_MONTHS) / 1e6
#        for opt in OPTIONS}

# %% [markdown]
# ### 4.1 Monte Carlo
#
# Sample N_SIMS draws of: churn lift (Normal posterior), margin
# (±~4pp), CAC (±~\$6), and LTV months (±~6). For each draw and each option,
# compute the profit. Store as a (N_SIMS × 4) DataFrame.

# %%
N_SIMS = 10_000

# TODO: build sim_lift, sim_margin, sim_cac, sim_ltv arrays of length N_SIMS.
# TODO: build a DataFrame `sim_profits` with one column per option.
sim_profits = ...

# %% [markdown]
# ### 4.2 Profit distributions
#
# Plot KDEs of `sim_profits` per option (in $M). Print a summary table with
# mean, sd, p5, p95.

# %%
# TODO

# %% [markdown]
# ## 5. Decision tree
#
# For each option, compute the profit at three posterior states (e.g. p25,
# p50, p75 of the posterior lift) and lay them out as a decision tree. Either
# render with matplotlib boxes/lines or display a tidy DataFrame.

# %%
# TODO

# %% [markdown]
# ## 6. Apply decision theory
#
# - **EV** of each option (mean profit across MC).
# - **CRRA utility** with γ = 2 evaluated at `WEALTH + profit` (use a
#   `wealth_baseline` such as Nimbus's annual contribution profit ~$500M to
#   keep utility well-defined). Convert back to a certainty-equivalent in $M.
# - **Minimax regret**: for each MC scenario, regret = best-in-scenario −
#   this option's profit. Then per option, max regret across scenarios.
# - Identify the EV-max, CE-max, and minimax-regret choices.

# %%
def crra_utility(profit, gamma: float = 2.0, wealth_baseline: float = 5e8):
    """U(W + profit) under CRRA. For γ=1 use log; otherwise the standard form."""
    # TODO
    raise NotImplementedError


# TODO: build the decision-theory table and print the picks under each rule.
# RECOMMENDED = ...   # set this to your chosen option

# %% [markdown]
# ## 7. Sensitivity & robustness
#
# - **Tornado** — flex each driver one at a time and plot the impact on the
#   recommended option's profit. Drivers: churn lift (±1 SD), margin (±4pp),
#   CAC (±\$10), LTV months (±6).
# - **Break-even** — find the 3-month churn lift at which the recommended
#   option's profit equals zero (use scipy.optimize.brentq). Report the
#   posterior probability of exceeding that lift.
# - **Robustness** — across all MC scenarios, what % of the time is the
#   recommended option the highest-profit option?

# %%
# TODO: tornado table + bar chart.

# %%
# TODO: break-even via brentq, plus posterior probability of being above it.

# %%
# TODO: share of MC scenarios where the recommended option wins.

# %% [markdown]
# ## 8. Recommendation & next steps
#
# Now write the 1-page decision memo to the CFO (`decision_memo.md` /
# `decision_memo.docx`). Use this section to draft your headline numbers
# and the bottom-line recommendation in plain English. Keep it short —
# the CFO will skim.
