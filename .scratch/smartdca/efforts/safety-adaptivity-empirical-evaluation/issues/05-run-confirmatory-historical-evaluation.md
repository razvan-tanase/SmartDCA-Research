# 05 — Run the confirmatory historical evaluation

Type: task
Status: resolved
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

- [x] The executed configuration matches the frozen protocol and historical input fingerprints exactly; any mismatch stops before outcomes are produced.
- [x] Every declared rolling episode, horizon, safety factor, primary corrected-mean configuration, and cost scenario is attempted for DCA, neutral guarded, and corrected guarded policies under identical information and timing.
- [x] No confirmatory dataset, parameter, episode rule, estimand, uncertainty method, or exclusion rule changes after outcome access; deviations, if unavoidable, are preserved as protocol violations rather than silently incorporated.
- [x] Frictionless results verify full funding, causality, unit coverage, direct accounting, and terminal cash/unit attribution for every guarded episode.
- [x] Gross frictionless and net-of-cost results are reported separately, and observed cost-induced shortfalls are not described as violations of the existing theorem.
- [x] Episode outputs and aggregates report complete-system, signal-only, and safety-architecture comparisons; relative wealth gaps and ratios; downside quantiles; worst relative shortfall; cash drag; exposure; guardrail activation; purchase activity; and terminal cash/unit components.
- [x] Dependence-aware uncertainty intervals follow the preregistered overlapping-window method, record their block construction and seeds where applicable, and reproduce hand-checkable small-sample fixtures.
- [x] Sample counts, missing data, failures, protocol violations, and exclusions reconcile from source rows through episodes to each reported estimand.
- [x] One immutable run manifest regenerates raw episode results, aggregate tables, uncertainty outputs, and figure-ready data in a fresh environment.
- [x] The historical experiment report separates confirmatory conclusions from secondary and exploratory observations and states that realized associations do not prove universal or causal superiority.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket depends only on the validated historical-data seam; deterministic
  and stochastic studies do not gate faithful confirmatory execution.
- Claimed on `main` on 2026-08-31 after confirming ticket 04 is resolved and
  no other effort ticket is claimed. Execution is bound to replacement
  protocol `safety-adaptivity-yahoo-v2` and accepted private runner-input
  SHA-256 `d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`.
- The outcome-blind evaluator was frozen at commit `9c15cf3` before opening the
  private runner input. Its six public-contract tests, the 16-case shared-runner
  checkpoint, the 30-case historical seam, compilation, and the repository
  link audit passed; no confirmatory policy or estimand had yet been executed.
- Confirmatory outcomes were first accessed on 2026-08-31 when the exact
  accepted input completed immutable run
  `smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221`.
  The protocol's `confirmatory_outcomes_accessed=false` field remains the
  sealed registration-time state. The run records no deviation or protocol
  violation.
- The run reconciles 12,305 source observations to 1,365 attempted and included
  episodes, zero exclusions, 49,140 complete policy ledgers and comparison
  rows, 216 aggregate cells, and 36 registered uncertainty cells. Source-
  bearing artifacts remain in the ignored private bundle; the committed run
  publishes only derived outputs and cryptographic receipts.
- Independent domain review recomputed the run identity, hashes, counts,
  bootstrap cells, and full-family Holm adjustment and passed with no blocking
  scientific error. Its required wording boundaries are incorporated in the
  linked audit and report.
- The complete README verification matrix passed under CPython 3.12.14 on
  2026-08-31: 6 link-checker tests, the repository-wide Markdown link audit,
  every standalone scientific program, 16 canonical-run tests, 14
  deterministic-study tests, 39 stochastic-study tests, 30 historical-seam
  tests, and 11 confirmatory-evaluation tests. The clean stochastic replay
  completed in 1,680.654 seconds.

## Answer

The exact frozen configuration completed as immutable run
[`smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221`](../../../../../reports/experiments/runs/smartdca-historical-study-v1-5b10a2aba05f84eacfef87b421a580cf7c0dc30d2844c51be6241bc682e39221/manifest.json).
It binds protocol SHA-256
`a5194248f7b55073e60b357c01c4993c1e50ed20c9c9672daf4780db1127f2be`
and accepted runner-input SHA-256
`d49a5a6e0304a7da213082698990d46bec7f7cac2399533990f84a40183bec88`.
All 1,365 rolling episodes were included with zero exclusion, deviation, or
protocol violation.

The confirmatory result is negative. Corrected guarded versus DCA had a
negative median in all 18 non-unit primary frictionless cells, from -4.593% to
-0.335%; nine cells rejected the two-sided zero null after Holm adjustment
over the full 36-cell H1/H2 family. Corrected guarded versus neutral guarded
had 17 negative medians and one positive median, from -0.545% to +0.052%, with
no H2 Holm rejection. The neutral-guarded architecture medians were negative
in all 18 corresponding cells. None of these realized overlapping-window
associations establishes universal, causal, optimal, or expected performance.

All frictionless funding, causality, buy-only, unit-coverage, independent-DCA,
direct-accounting, terminal cash/unit, common-floor, and \(\lambda=1\) collapse
checks passed. The 36 non-unit cost-adjusted complete-system medians were also
negative, but those rows remain explicitly outside the current safety theorem.
The independently reviewed [experiment
report](../../../../../reports/experiments/confirmatory-historical-evaluation.md),
[audit note](../../../../../research/notes/confirmatory-historical-evaluation-audit.md),
and eleven-case [public
checkpoint](../../../../../reproducibility/checks/check_historical_confirmatory_evaluation.py)
preserve the exact results and their claim boundaries. Ticket 06 may now
synthesize this result with the deterministic and stochastic evidence.
