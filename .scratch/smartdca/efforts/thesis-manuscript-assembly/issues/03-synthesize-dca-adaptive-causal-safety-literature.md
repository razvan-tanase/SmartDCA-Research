# 03 — Synthesize DCA, adaptive accumulation, and causal-safety literature

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 02
Parent: [Thesis manuscript assembly](../spec.md)

## Question

How should the thesis position DCA, adaptive accumulation rules, sequential portfolio decisions, and safety constraints without conflating recurring investment, market timing, universal guarantees, and realized performance?

## What to build

A committee reader can understand what prior financial and computational work exists, which comparison problem this thesis studies, and why causal budget feasibility and a relative-wealth floor form a distinct contribution boundary.

## Acceptance criteria

- [x] The search covers DCA and recurring investment, adaptive accumulation or value-aware contribution rules, causal or online portfolio decisions, and portfolio safety constraints.
- [x] Primary studies, original methodological sources, and authoritative surveys are preferred, with search and inclusion boundaries recorded.
- [x] DCA is distinguished from lump-sum timing, rebalancing, retrospectively budget-matched strategies, and individualized investment advice.
- [x] Prior adaptive strategies are compared on information timing, funding, comparator, performance criterion, and guarantee type.
- [x] Universal, expected, probabilistic, and realized claims are kept distinct throughout the synthesis.
- [x] The literature section explains why the project's sequential admissibility, same-deposit comparator, and cash-inclusive terminal wealth are economically material.
- [x] Every externally dependent statement has a supporting bibliography entry and claim-to-evidence record.
- [x] Citation and novelty review finds no unsupported positioning claim, and the manuscript build remains clean.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
- Claimed on 2026-09-03. The implementation will add one bounded primary-source search record and synthesis note, the corresponding bibliography and claim-to-evidence entries, the DCA/adaptive/causal-safety literature slice in Chapter 2, and a focused fail-closed verification seam before the canonical manuscript build and independent review.
- Independent review on 2026-09-03 found and corrected the SmartDCA spending-ratio direction and the Edleson excerpt-access boundary. Follow-up citation and novelty review then passed with no findings. Standards review found duplicated citation parsing and a false-negative uncited-source test; the parser is now shared and the corrected negative test passes.
- Verification on 2026-09-03 passed the four focused literature tests, the 29 manuscript control/build/release tests, the control and link checks, and the canonical manuscript build. The final 29-page A4 PDF's four literature pages and three bibliography pages were rendered and visually inspected with no defects attributable to this slice.

## Answer

Ticket 03 is resolved. Chapter 2 now positions recurring-deposit DCA against staged lump-sum investment, adaptive contribution methods, online portfolio and one-way-trading guarantees, and safety-first, portfolio-insurance, drawdown, and conservative-learning objectives. A bounded 21-source evidence note records the search and inclusion limits, the five required comparison dimensions, claim semantics, and a conservative novelty verdict. Five reviewed claim-to-evidence records, a shared citation parser, and a fail-closed literature audit keep the manuscript, bibliography, and source note synchronized.
