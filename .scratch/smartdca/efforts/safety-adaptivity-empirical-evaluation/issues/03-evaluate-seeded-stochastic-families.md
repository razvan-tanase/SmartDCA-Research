---
profile: smartdca-okf/0.4
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
  at: 2026-08-25T07:52:38Z
generation_run: urn:uuid:a5d8aafb-5c01-48a5-8177-23ed524a00a7
---
# 03 — Evaluate seeded stochastic path families

Type: task
Status: open
Label: ready-for-agent
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

## Answer

_Not yet resolved._
