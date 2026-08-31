# 05 — Run the confirmatory historical evaluation

Type: task
Status: claimed
Blocked by: 04
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

What realized performance do the three frozen policies produce across the
preregistered rolling S&P 500 and Bitcoin episodes, safety factors, horizons,
and cost scenarios when analyzed with the declared dependence-aware method?

## What to build

A researcher can execute the locked confirmatory historical configuration once,
preserve every raw episode and exclusion, reproduce dependence-aware summaries,
and inspect gross safety, net performance, complete-system effects, signal-only
effects, mechanism attribution, and limitations without post-outcome tuning.

## Acceptance criteria

- [ ] The executed configuration matches the frozen protocol and historical input fingerprints exactly; any mismatch stops before outcomes are produced.
- [ ] Every declared rolling episode, horizon, safety factor, primary corrected-mean configuration, and cost scenario is attempted for DCA, neutral guarded, and corrected guarded policies under identical information and timing.
- [ ] No confirmatory dataset, parameter, episode rule, estimand, uncertainty method, or exclusion rule changes after outcome access; deviations, if unavoidable, are preserved as protocol violations rather than silently incorporated.
- [ ] Frictionless results verify full funding, causality, unit coverage, direct accounting, and terminal cash/unit attribution for every guarded episode.
- [ ] Gross frictionless and net-of-cost results are reported separately, and observed cost-induced shortfalls are not described as violations of the existing theorem.
- [ ] Episode outputs and aggregates report complete-system, signal-only, and safety-architecture comparisons; relative wealth gaps and ratios; downside quantiles; worst relative shortfall; cash drag; exposure; guardrail activation; purchase activity; and terminal cash/unit components.
- [ ] Dependence-aware uncertainty intervals follow the preregistered overlapping-window method, record their block construction and seeds where applicable, and reproduce hand-checkable small-sample fixtures.
- [ ] Sample counts, missing data, failures, protocol violations, and exclusions reconcile from source rows through episodes to each reported estimand.
- [ ] One immutable run manifest regenerates raw episode results, aggregate tables, uncertainty outputs, and figure-ready data in a fresh environment.
- [ ] The historical experiment report separates confirmatory conclusions from secondary and exploratory observations and states that realized associations do not prove universal or causal superiority.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket depends only on the validated historical-data seam; deterministic
  and stochastic studies do not gate faithful confirmatory execution.
- Claimed on `main` on 2026-08-31 after confirming ticket 04 is resolved and
  no other effort ticket is claimed. Execution is bound to replacement
  protocol `safety-adaptivity-yahoo-v2` and accepted private runner-input
  SHA-256 `d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`.

## Answer

_Not yet resolved._
