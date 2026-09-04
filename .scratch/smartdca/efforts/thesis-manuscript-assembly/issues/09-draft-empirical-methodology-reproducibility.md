# 09 — Draft the empirical methodology and reproducibility chapter

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 05, 07
Parent: [Thesis manuscript assembly](../spec.md)

## Question

Can a reviewer reconstruct the complete empirical design and its inferential limits before reading outcomes, including how each policy, comparison, evidence layer, and immutable artifact is defined?

## What to build

A reviewer can understand and reproduce the registered evaluation from declared protocols, inputs or receipts, policies, estimands, statistics, run identities, and environment assumptions without hidden conversation context.

## Acceptance criteria

- [x] The chapter distinguishes the DCA comparator, neutral guarded selector, and corrected guarded rule under identical timing, deposits, horizons, and costs.
- [x] Complete-system, signal-only, and architecture-only comparisons are defined separately.
- [x] Historical series semantics, provider provenance, source receipts, retained-input fingerprints, private-data restrictions, and redistribution boundaries are explicit.
- [x] Deterministic paths, seeded stochastic families, primary rolling historical episodes, and registered robustness evidence have separate declared roles.
- [x] Deposit schedules, horizons, evaluation dates, safety factors, corrected-mean configuration, cost scenarios, exclusions, and validation rules match the frozen protocol.
- [x] Estimands, downside summaries, mechanism measures, block resampling, finite-run p-values, multiplicity family, and Holm adjustment are stated exactly.
- [x] Confirmatory hypotheses, secondary analyses, registered robustness, and exploratory interpretation remain distinct.
- [x] Frictionless theorem coverage and net-of-cost empirical scope are separated before results are introduced.
- [x] The reproducibility statement identifies accepted software, environment, protocols, input identities, run identities, review receipts, and clean build routes.
- [x] Every methodological statement is mapped to protocol or literature authority, independently checked, and rendered successfully.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
- Claimed on 2026-09-04 after tickets 05 and 07 were verified resolved. The implementation will replace the Chapter 6 and Appendices C--D placeholders with the frozen three-policy design, evidence-tier and inference boundaries, historical provenance, and clean reproduction routes; add reviewed claim mappings and a dedicated fail-closed audit; and preserve every accepted protocol, input, receipt, and run bundle byte-for-byte.
- Independent domain review on 2026-09-04 compared the chapter, appendices, protocols, source and preparation receipts, robustness plan, uncertainty artifact, runner, package review, claims, notation, and rendered PDF. Follow-up cleared the corrected fee-inclusive execution algebra, runtime split, bootstrap and Holm scope, public replay route, provider-replacement wording, receipt boundaries, collision-free notation, section-local citations, distinct artifact lifecycle rules, and table-specific traceability. The fresh 88-page A4 build has no overfull boxes, undefined references or citations, or package warnings; Chapter 6 pages 45--54 and Appendices C--D pages 73--81 were independently inspected and passed.
- The two-axis code review found and prompted corrections for reproducibility-workflow drift, repeated mutation-test setup, artifact-layer mutability wording, Table C.1 traceability, and final tracking synchronization. The dedicated audit now also locks the workflow route and both methodology table claims; follow-up Standards and specification reviews passed with no remaining finding.
- Final verification used CPython 3.12.14. The eight isolated empirical seam modules passed 135 tests, including byte-for-byte canonical, deterministic, stochastic, historical, synthesis, and package-review replays; the managed focused suite passed 96 tests plus all directly intersecting exact scientific programs; the post-review methodology and manuscript-control rerun passed 23 tests; the corrected canonical build passed; and the Markdown-link and diff checks were clean. No accepted file under `experiments/` or `reports/` changed.

## Answer

Ticket 09 is resolved. Chapter 6 now defines the fair three-policy comparison, evidence roles, frozen historical design, exact estimands and inference, theorem-versus-cost boundary, and accepted reproduction model before any outcome chapter. Appendices C--D expose the registered axes, exclusions, bootstrap and Holm rules, software environments, versioned artifact lifecycle, accepted run identities, public replay, authorized private reconciliation, and clean build commands. Seven reviewed methodology claims, two table claims, three notation records, the cited evidence audit, and the fail-closed control keep the prose tied to accepted protocols and artifacts without changing any retained empirical byte. Tickets 10 and 11 are the parallel unblocked drafting frontiers.
