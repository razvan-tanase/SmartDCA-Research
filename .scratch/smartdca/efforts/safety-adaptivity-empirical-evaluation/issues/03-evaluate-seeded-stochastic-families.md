# 03 — Evaluate seeded stochastic path families

Type: task
Status: resolved
Blocked by: 01
Parent: [Safety-adaptivity empirical evaluation](../spec.md)

## Question

How does the realized safety-adaptivity trade-off change under reproducible
synthetic processes with controlled trend, mean reversion, volatility, regime,
and jump characteristics?

## What to build

A researcher can rerun every declared stochastic family from saved parameters
and seeds, obtain the complete three-policy result distribution for the
preregistered configurations, and inspect sensitivity, downside, attribution,
failures, and a bounded report without treating simulation as a universal proof.

## Acceptance criteria

- [x] The executed stochastic families cover declared trend, mean-reversion, volatility, regime-switching, and jump constructions with economically interpretable parameter ranges.
- [x] Every simulated path is fully determined by a saved generator version, family configuration, and seed; identical inputs reproduce identical paths and results.
- [x] The complete predeclared grid is executed for all three policies under identical deposits, horizons, evaluation rules, safety factors, primary corrected-mean configurations, and cost scenarios.
- [x] Primary configurations remain distinct from exploratory parameter sensitivity, and every attempted configuration is retained so the best outcome cannot be selected silently.
- [x] Results include effect-size distributions, downside quantiles, worst observed relative shortfall, cash drag, exposure, guardrail activation, purchase activity, and terminal cash/unit attribution for all three policy comparisons.
- [x] Frictionless safety and accounting invariants are checked path by path; net-of-cost results are reported separately and do not inherit the theorem label.
- [x] Generator and runner failures, excluded paths, and numerical or configuration errors are machine-readable and included in reported sample counts.
- [x] Aggregate statistics independently reconcile with episode-level outputs, and rerunning from the manifest regenerates raw results, tables, and figure-ready data.
- [x] The experiment report distinguishes controlled sensitivity from historical evidence and avoids claims of stochastic optimality, causal superiority, or universal performance.
- [x] The ticket, report, checks, effort map, and repository verification gates agree at resolution.

## Comments

- Created from the user-approved seven-ticket decomposition on 2026-08-25.
- This ticket may proceed in parallel with tickets 02 and 04 after ticket 01
  resolves.
- Claimed on `main` after confirming ticket 01 is resolved and no other ticket
  is claimed. The approved complete-run seam and frozen policy grid govern the
  implementation.
- The review-corrected durable run is
  `smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25`.
  An independent clean replay regenerated every substantive artifact byte for
  byte in 1,568 seconds, and the complete 14-command scientific matrix passed;
  its final stochastic module ran 39 tests in 1,652.268 seconds.
- Specification re-review passed without a finding. Standards re-review found
  no documented-standard violation. Its two remaining nonblocking architecture
  judgments concern low-level helpers shared conceptually with
  `deterministic_study.py` and the 2,656-line size of `stochastic_study.py`.
  Extracting the former would alter the already reviewed deterministic source
  identity; splitting the latter would alter this run's bound source identity
  and require another complete regeneration and replay. Both are deferred as
  separate architecture work rather than expanding this ticket.

## Answer

The saved [stochastic design](../../../../../experiments/inputs/seeded-stochastic-families-v1.json)
and generator produce ten declared configurations—one primary and one
exploratory sensitivity for each of trend, mean reversion, stochastic
volatility, regime switching, and jump diffusion. Three saved seeds and the
12-, 36-, and 60-month horizons determine 90 path attempts. All 90 generated,
with zero exclusions or configuration, numerical, generator, input, or runner
failures.

Immutable run
[`smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25`](../../../../../reports/experiments/runs/smartdca-stochastic-v1-78c05259beccc59ab5605e1ac291e01cb899361705862e88ba2e73d2fb2fbf25/manifest.json)
binds the frozen protocol, saved study, generated runner input, generator and
shared-runner sources, and CPython 3.12. It retains 3,240 complete policy
ledgers, 3,240 comparison rows, 1,080 aggregate cells, complete figure-ready
data, and generated report tables. Independent regrouping reconciles all
49,684 study values and 42,124 shared-runner values with zero mismatch; clean
replay regenerated every substantive artifact byte for byte.

The controlled result is mixed rather than a superiority finding. In the
primary 60-month frictionless `lambda=0.75` slice, median corrected-versus-DCA
gaps are positive for mean reversion and jump diffusion but negative for trend,
stochastic volatility, and regime switching. Corrected versus neutral is also
not uniformly positive: the primary regime construction has a negative median
and downside tail. Exploratory sensitivities change signs and tails again, so
the evidence establishes dependence on the controlled process, seed, horizon,
and safety factor—not a stochastic optimum or expected market advantage.

At `lambda=1`, both guarded policies collapse transaction by transaction to
DCA on every path and cost scenario. Every frictionless ledger passes causal
prefix, full-funding, buy-only, unit-coverage, direct-wealth, shared-floor,
independent-DCA, and terminal cash/unit checks. The 2,160 cost-adjusted ledgers
are labeled outside the current safety theorem. Forced generator,
configuration, and runner-boundary failures also leave typed immutable
receipts, even though the durable run itself has none.

The independently reviewed [experiment report](../../../../../reports/experiments/seeded-stochastic-families.md)
and [audit note](../../../../../research/notes/seeded-stochastic-family-evaluation-audit.md)
record the distributions, downside, cash drag, exposure, guardrail activation,
purchase activity, attribution, provenance, and limits. Both remain draft until
the effort's registered historical-slice promotion gate; resolving this ticket
does not convert controlled simulation into historical or universal evidence.
