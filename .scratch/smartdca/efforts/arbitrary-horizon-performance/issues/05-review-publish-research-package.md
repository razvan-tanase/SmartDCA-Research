# 05 — Review and publish the arbitrary-horizon research package

Type: task
Status: resolved
Blocked by: 04
Parent: [Arbitrary-horizon guarded SmartDCA performance](../spec.md)

## Question

Independently review the complete arbitrary-horizon result against the effort specification,
the project standards, the established financial model, and every supporting
exact witness. Resolve all actionable findings, publish the accepted result in
the appropriate research files, and express its significance in a concise
Financial Computing thesis narrative without beginning the empirical study.

## What to build

The arbitrary-horizon frontier becomes a self-contained, reproducible research
checkpoint: the operational resolution, detailed evidence, executable
verification, theorem statement, glossary, and maps all agree, and the result
can be explained in the defense without centering the presentation on proof
details.

## Acceptance criteria

- [x] An independent reviewer re-derives the cash-timing identity and final wealth implication without relying on the producing derivation.
- [x] The reviewer reproduces every decisive exact witness and checks every declared path and parameter assumption.
- [x] All proof branches, scope limits, citations, artifact links, and computational claims are reviewed against the specification.
- [x] Every actionable review finding is resolved or recorded as a blocker before publication.
- [x] The accepted positive or negative result has one theorem page linked to its detailed evidence and executable check.
- [x] The project glossary and research map use the settled terminology and scope.
- [x] All retained local links resolve and the scientific verification gates pass after the final changes.
- [x] A concise thesis-facing explanation states the problem, failed universal ambition, safety pivot, arbitrary-horizon finding, and why the result advances the work.
- [x] The empirical study, dynamic safety ratchet, minimax policy design, and manuscript assembly remain separate future work.
- [x] Subsequent research remains separately authorized and unclaimed.

## Comments

- Created from the approved ticket decomposition of the effort specification on
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
[theorem statement](../../../../../research/theorems/arbitrary-horizon-performance-boundary.md),
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
[effort map](../map.md), and the [master map](../../../map.md). The two
experiment reports retain the code fingerprints and run IDs of their original
executions. A separate publication replay records the shared engine fingerprint
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

At resolution, the empirical study, dynamic safety ratchet, minimax policy
design, and manuscript assembly remained separate work. The empirical effort
later began; this ticket itself stays complete.
