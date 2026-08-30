---
profile: smartdca-okf/0.5
type: research-ticket
title: "Evaluate seeded stochastic path families"
description: "Open task ticket executing reproducible stochastic sensitivity experiments across declared market-process families."
knowledge_role: operational
status: draft
original_record: true
ticket_type: task
ticket_status: open
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-30T09:34:27Z
generation_run: urn:uuid:e54b04fe-969e-4f95-81f4-1121a2423495
---
# 03 — Evaluate seeded stochastic path families

Type: task
Status: open
Label: ready-for-agent
Blocked by: 01, 08
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

- [ ] The executed stochastic families cover declared trend, mean-reversion, volatility, regime-switching, and jump constructions with economically interpretable parameter ranges.
- [ ] Every simulated path is fully determined by a saved generator version, family configuration, and seed; identical inputs reproduce identical paths and results.
- [ ] The complete predeclared grid is executed for all three policies under identical deposits, horizons, evaluation rules, safety factors, primary corrected-mean configurations, and cost scenarios.
- [ ] Primary configurations remain distinct from exploratory parameter sensitivity, and every attempted configuration is retained so the best outcome cannot be selected silently.
- [ ] Results include effect-size distributions, downside quantiles, worst observed relative shortfall, cash drag, exposure, guardrail activation, purchase activity, and terminal cash/unit attribution for all three policy comparisons.
- [ ] Frictionless safety and accounting invariants are checked path by path; net-of-cost results are reported separately and do not inherit the theorem label.
- [ ] Generator and runner failures, excluded paths, and numerical or configuration errors are machine-readable and included in reported sample counts.
- [ ] Aggregate statistics independently reconcile with episode-level outputs, and rerunning from the manifest regenerates raw results, tables, and figure-ready data.
- [ ] The experiment report distinguishes controlled sensitivity from historical evidence and avoids claims of stochastic optimality, causal superiority, or universal performance.
- [ ] The ticket, report, checks, effort map, and repository verification gates agree at resolution.

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
- Resolution is blocked at the repository LLM-Wiki publish gate. All 32
  validator fixtures pass under the repository-available CPython 3.11, but
  strict validation reports 47 base findings and 273 profile findings. Every
  direct finding belongs to the pre-existing `.agents/**/*.md` corpus added by
  baseline commit `ea7cca3`; the sole `index.md` finding is the corresponding
  missing-path inventory. No ticket-owned path adds a validator finding.
  Clearing this requires a separate versioned profile/path decision or a
  repository-corpus decision, so this ticket remains claimed and unresolved;
  no significance gate is entered and ticket 04 remains unclaimed.
- Interrupted on 2026-08-30 under the Wayfinder rule: the repository/profile
  decision is now isolated in [ticket 08](08-exclude-agents-from-okf-bundle.md),
  which is the sole claimed ticket. The reviewed stochastic evidence and its
  durable run remain unchanged while this ticket is open and blocked.

## Answer

_Not yet resolved._
