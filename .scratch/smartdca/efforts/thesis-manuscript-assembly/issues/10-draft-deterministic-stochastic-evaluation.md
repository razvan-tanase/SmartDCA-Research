# 10 — Draft the deterministic and stochastic evaluation

Type: task
Status: open
Triage: ready-for-agent
Blocked by: 08, 09
Parent: [Thesis manuscript assembly](../spec.md)

## Question

What do the frozen deterministic and seeded-stochastic studies show about safety, performance dispersion, downside, and mechanisms when their distinct evidential roles are preserved?

## What to build

A reader can inspect regenerated tables and figures for synthetic paths, understand exact mechanisms and stochastic variation, and trace every number to its accepted run without mistaking simulation for universal proof.

## Acceptance criteria

- [ ] Every included deterministic, adversarial, and seeded-stochastic result is regenerated or independently reconciled against its accepted immutable bundle.
- [ ] Tables and figures report the correct policy comparison, population, units, sample counts, exclusions, horizons, safety factors, and cost scope.
- [ ] Strict-win and strict-loss witnesses are linked to the analytical boundaries rather than generalized beyond them.
- [ ] Stochastic results report effect sizes, dispersion, downside, guardrail activation, cash drag, exposure, and terminal cash-unit attribution where available.
- [ ] Deterministic counts and stochastic replications are not pooled into a new inferential unit or significance claim.
- [ ] Frictionless validation and net-of-cost performance remain clearly separated.
- [ ] Figure captions and table notes are self-contained and interpretable without repository-only context.
- [ ] Every numerical statement, table, and figure has a current evidence-map entry and generated-source identity.
- [ ] Independent domain, statistical-language, and visual checks pass, and the canonical manuscript builds cleanly.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
