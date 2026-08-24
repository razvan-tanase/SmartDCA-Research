---
profile: smartdca-okf/0.4
type: research-ticket
title: "Review and publish the arbitrary-horizon research package"
description: "Resolved task ticket independently reviewing and publishing the arbitrary-horizon research package for the thesis narrative."
knowledge_role: operational
status: stable
original_record: true
ticket_type: task
ticket_status: resolved
generated:
  by: openai-codex/smartdca-wiki-0.1
  at: 2026-08-24T21:29:22Z
generation_run: urn:uuid:c8785a76-9c52-4377-ab6e-4a44c3e403e6
verified:
  - by: openai-codex/writing-for-agents-0.1
    at: 2026-08-23T21:32:48Z
    review_run: urn:uuid:d87a04a7-92ae-43c4-a446-998b6f1a8d14
  - by: openai-codex/independent-math-review-0.1
    at: 2026-08-24T21:12:56Z
    review_run: urn:uuid:1694bf39-9777-4b36-bd09-5c6abc74460e
  - by: openai-codex/standards-review-0.1
    at: 2026-08-24T21:31:55Z
    review_run: urn:uuid:8185820b-9b80-4607-91f0-43335cfbdff5
  - by: openai-codex/spec-review-0.1
    at: 2026-08-24T21:31:55Z
    review_run: urn:uuid:8da58364-ea0f-42bb-a729-d559abe6e7e7
---
# 05 — Review and publish the arbitrary-horizon research package

Type: task
Status: resolved
Blocked by: 04
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Independently review the complete arbitrary-horizon result against the effort specification,
the project standards, the established financial model, and every supporting
exact witness. Resolve all actionable findings, publish the accepted result in
the correct knowledge layers, and express its significance in a concise
Financial Computing thesis narrative without beginning the empirical study.

## What to build

The arbitrary-horizon frontier becomes a self-contained, reproducible research
checkpoint: the operational resolution, detailed evidence, executable
verification, canonical result, glossary, map, index, and knowledge log all
agree, and the result can be explained in the defense without centering the
presentation on proof details.

## Acceptance criteria

- [x] An independent reviewer re-derives the cash-timing identity and final wealth implication without relying on the producing derivation.
- [x] The reviewer reproduces every decisive exact witness and checks every declared path and parameter assumption.
- [x] All proof branches, scope limits, citations, artifact links, and computational claims are reviewed against the specification.
- [x] Every actionable review finding is resolved or recorded as a blocker before publication.
- [x] The accepted positive or negative result has one canonical home linked to its detailed evidence and executable check.
- [x] The project glossary and research map use the settled terminology and scope.
- [x] The root discovery inventory and immutable event history include every created or changed concept.
- [x] All structural and scientific verification gates pass after the final changes.
- [x] A concise thesis-facing explanation states the problem, failed universal ambition, safety pivot, arbitrary-horizon finding, and why the result advances the work.
- [x] The empirical study, dynamic safety ratchet, minimax policy design, and manuscript assembly remain separate future work.
- [x] The ticket ends at the user significance gate and leaves every subsequent research ticket unclaimed.

## Comments

- Created from the approved tracer-bullet decomposition of the effort specification on
  2026-08-23.
- Claimed on 2026-08-24 after confirming ticket 04 was resolved and no other
  project ticket was claimed.
- The scientific reviewer completed the cash-timing and affine-boundary
  derivations before opening the producing proof notes, then used a separate
  standard-library exact-rational implementation to replay every decisive
  ticket 01--04 witness.
- The clean-room replay is preserved as a standalone publication check
  (SHA-256 f25519530fa0f151ace68a732f004a532cd92bd873167b4b04b6596fd6cb23c4);
  it imports no repository modules and runs in continuous integration.
- The initial scientific audit treated the experiment reports' pre-ticket-04
  engine hash as stale. Standards review caught that each hash correctly names
  its original executed run and that replacing it would create hybrid
  provenance. The reports retain their original run identities; a separate
  publication verification run records the current code and reproduced JSON
  hashes in the independent review.
- Six links in immutable historical log events retain the pre-migration ticket
  paths. Live migration events point to the current effort paths; rewriting the
  old events would violate the immutable-log contract, so this is recorded as
  a nonblocking historical limitation rather than a publication blocker.

## Answer

**Verdict: the arbitrary-horizon package is scientifically cleared and ready
for publication.** The
[independent review](../../../../../research/notes/arbitrary-horizon-research-package-review.md)
derives the cash-timing identity directly from the ledger recurrence before
consulting the proof, recovers the exact terminal-inventory equation

\[
W_n^c(P)-W_n^T(P)=H_T+P U_T,
\]

and reproduces every decisive exact witness with an implementation independent
of the repository modules. It checks every sign branch, comparator, declared
path class, parameter restriction, terminal-price condition, floor regime,
nontrivial tie, and the \(\lambda=1\) collapse. It also confirms that the
coordinatewise-monotone weighted-Gini citation supports
\(\alpha\beta\le0\), that active artifact links resolve, and that no
stochastic, universal-dominance, parameter-superiority, or novelty claim has
entered the result.

The accepted result has one
[canonical home](../../../../../research/theorems/arbitrary-horizon-performance-boundary.md),
linked to the [complete proof](../../../../../research/notes/arbitrary-horizon-performance-boundary.md),
the independent review, and the
[boundary check](../../../../../reproducibility/checks/check_arbitrary_horizon_performance_boundary.py)
plus the repository-independent
[publication replay](../../../../../reproducibility/checks/check_arbitrary_horizon_publication_review.py).
The [cash-timing](../../../../../research/theorems/arbitrary-horizon-cash-timing-identity.md)
and [cash-mechanism](../../../../../research/theorems/reference-aligned-guardrail-cash-single-crossing.md)
theorems remain separate reusable results. The glossary already used the
settled term **arbitrary-horizon terminal-inventory boundary** with the correct
scope, so no terminology rewrite was needed.

Publication synchronizes the human [overview](../../../../../README.md), the
[effort map](../map.md), the [master map](../../../map.md), the root
[inventory](../../../../../index.md), and the immutable
[event history](../../../../../log.md). The two experiment reports retain the
code fingerprints and run IDs of their original executions. A separate
publication verification run,
`urn:uuid:8fd14f92-d220-4e36-ad3a-32a008e4b541`, records the current shared
engine fingerprint
`35ff108c5b58e992878b82f47e294e2fb0cbf0992e7a89dff141c5c22eb4f2f1`
and reproduces their deterministic JSON hashes `d6756a...` and `19b703...`,
so the published counts and conclusions are unchanged without conflating
executions.

For the thesis defense, the result is: the original ambition of guaranteed
adaptive superiority fails because exact causal dominance forces DCA; the
epsilon-DCA unit guardrail is the constructive safety pivot; weak
single-valley structure is still insufficient for performance; and terminal
cash plus terminal units give the exact every-finite-horizon evaluation-price
boundary. This advances the work by separating what the floor guarantees from
what the adaptive score actually contributes on a realized path, without
turning the defense into a proof presentation.

The empirical study, dynamic safety ratchet, minimax policy design, and
manuscript assembly remain separate future efforts. This ticket stops at the
user significance gate with no subsequent ticket or effort claimed.
