# 10 — Draft the deterministic and stochastic evaluation

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 08, 09
Parent: [Thesis manuscript assembly](../spec.md)

## Question

What do the frozen deterministic and seeded-stochastic studies show about safety, performance dispersion, downside, and mechanisms when their distinct evidential roles are preserved?

## What to build

A reader can inspect regenerated tables and figures for synthetic paths, understand exact mechanisms and stochastic variation, and trace every number to its accepted run without mistaking simulation for universal proof.

## Acceptance criteria

- [x] Every included deterministic, adversarial, and seeded-stochastic result is regenerated or independently reconciled against its accepted immutable bundle.
- [x] Tables and figures report the correct policy comparison, population, units, sample counts, exclusions, horizons, safety factors, and cost scope.
- [x] Strict-win and strict-loss witnesses are linked to the analytical boundaries rather than generalized beyond them.
- [x] Stochastic results report effect sizes, dispersion, downside, guardrail activation, cash drag, exposure, and terminal cash-unit attribution where available.
- [x] Deterministic counts and stochastic replications are not pooled into a new inferential unit or significance claim.
- [x] Frictionless validation and net-of-cost performance remain clearly separated.
- [x] Figure captions and table notes are self-contained and interpretable without repository-only context.
- [x] Every numerical statement, table, and figure has a current evidence-map entry and generated-source identity.
- [x] Independent domain, statistical-language, and visual checks pass, and the canonical manuscript builds cleanly.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
- Claimed for implementation on 2026-09-04 after confirming tickets 08 and 09 are resolved; the accepted manuscript and numerical-reconciliation seams will be used for test-first execution.
- Independent reviewer Pauli reconciled the deterministic catalog, all 30 displayed stochastic comparison rows, mechanism attribution, and both lambda-one receipts against the immutable runs. Domain and statistical-language review passed; visual review of the warning-free 97-page A4 build, including physical pages 58, 89, and 91, found no clipping, overlap, ambiguity, or color dependence.
- The two-axis code review found and prompted explicit per-comparison seed-range dispersion, a self-contained exploratory caption, a Chapter 7-specific lambda-one claim, direct stochastic-aggregate authority, accurate 15-cell table scopes, a corrected scientific-check count, shared stochastic-row rendering, and a frozen aggregate-cell key. Follow-up Standards and specification reviews passed with no remaining finding.
- Final repository-wide verification used CPython 3.12.14. All 27 scientific checks passed, including the 39-test byte-for-byte stochastic replay in 1,675.701 seconds and the deterministic, historical-data, confirmatory, robustness, synthesis, and publication-package replays. The managed manuscript seam passed 106 tests plus all directly intersecting exact programs, the control and Markdown-link audits, and the canonical 97-page A4 build. The managed sandbox's first direct manuscript invocation hid `latexmk` after the scientific subprocesses; the documented single-process helper then completed the identical TeX-dependent seam successfully. No accepted file under `experiments/` or `reports/experiments/runs/` changed.

## Answer

Ticket 10 is resolved. Chapter 7 and Appendix E now present the accepted deterministic, adversarial, and three-seed stochastic evidence through four byte-reproducible LaTeX assets. The slice keeps fixed-path counts separate from stochastic replications; reports all three policy comparisons with effect size, seed-range dispersion, downside, guardrail activation, cash drag, exposure, and signed cash/unit attribution; links finite witnesses to their exact analytical boundaries; and keeps frictionless safety validation distinct from net fee calculations. Seven reviewed result claims, ten table/figure claims, three governing non-claims, pinned run identities, and a fail-closed regeneration audit keep every displayed result traceable without changing any accepted protocol, input, or run-bundle byte. Ticket 11 is the sole immediate drafting frontier; ticket 12 remains blocked on it.
