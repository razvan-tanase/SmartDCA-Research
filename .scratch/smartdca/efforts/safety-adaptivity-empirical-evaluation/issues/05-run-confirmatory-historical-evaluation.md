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
- Final specification review against pre-task base `5d2c7a1` found that the
  public run executes primary horizons and coverage plus cost robustness, but
  not the protocol's five robustness coverage values or 6/24/120-month
  quarterly episodes. It also found that the sealed confirmatory-only tier
  classifier would mislabel those rows if reused. Ticket 05 remains claimed
  while a separately identified post-confirmatory robustness extension closes
  both gaps without mutating the completed run.
- The outcome-blind correction is frozen by execution-plan SHA-256
  `2cc155f6c63a74a0dce7cad202d6a5870a6f59bf239733ce2ad5e117919eae14`
  and robustness-engine SHA-256
  `c909f8d87bf954771da24c0313bd6e749bc050cee1177528a862f479afbcdd72`.
  Independent pre-execution domain review passed the quarterly 0/3/.../H-3
  deposit interpretation, all registered coverage/horizon projections, the
  grid-aware tier classifier, post-outcome disclosure, and private-retention
  boundary. Six public fixture tests passed; no robustness policy outcome had
  yet been executed.
- Robustness outcomes were accessed on 2026-09-01 when immutable run
  `smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184`
  completed. It executed the five registered monthly robustness coverage
  values on all 1,365 sealed episodes and all nine coverage values on 428
  quarterly 6/24/120-month episodes, with zero exclusion, deviation, or
  protocol violation. The primary confirmatory run and its 36-test Holm family
  remain unchanged.
- The robustness run reconciles 108,378 ledgers and comparison rows to 810
  aggregate cells: 792 robustness and 18 monthly `lambda=1` frictionless
  secondary cells. All cells are descriptive with uncertainty not run. Source-
  bearing schedules, outcomes, and ledgers remain in the ignored private
  bundle; only five derived artifacts and the manifest are committed.
- Independent post-run domain review recomputed both nested run IDs, all
  private and public hashes, schedule projections, counts, generated table
  rows, tier labels, and transaction-level `lambda=1` collapse. It passed with
  no blocking scientific correction and required within-schedule,
  descriptive-only wording, explicit BTC 120-month `N=4`, theorem/cost
  separation, and no raw-wealth comparison across cadences.

## Result

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
preserve the exact results and their claim boundaries.

The separately registered post-confirmatory robustness extension completed as
immutable run
[`smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184`](../../../../../reports/experiments/runs/smartdca-historical-robustness-v1-0991d999e1a8070a2a6eb8046b08a91d0e42341995610a602372c52dfab14184/manifest.json).
All 30 monthly robustness-coverage frictionless complete-system medians and all
48 quarterly non-unit frictionless complete-system medians were negative. The
monthly signal-only medians were all negative; the quarterly signal-only rows
had 40 negative and eight positive medians, with all eight positive rows in
the 6-month BTC-USD cells. These are descriptive median relative-wealth gaps,
not new H1/H2 or significance results.

The extension passed the same funding, causality, buy-only, frictionless unit-
coverage, independent-DCA, direct-accounting, terminal cash/unit, common-floor,
`lambda=1` collapse, and cost-scope checks across both schedules. The 156
non-unit cost-adjusted complete-system medians were negative but remain outside
the current theorem. Quarterly raw wealth is not compared with monthly raw
wealth because cadence changes deposit counts. The four alternate corrected-
mean configurations remain deferred; the acceptance criterion requires the
primary configuration and is now complete. The updated [report](../../../../../reports/experiments/confirmatory-historical-evaluation.md),
[audit note](../../../../../research/notes/confirmatory-historical-evaluation-audit.md),
and [robustness checkpoint](../../../../../reproducibility/checks/check_historical_robustness_evaluation.py)
preserve the exact extension and its limits.

## Answer

_Pending final Standards and specification review against the pre-task base._
