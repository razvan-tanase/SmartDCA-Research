# 08 — Draft the finite- and arbitrary-horizon performance boundaries

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 07
Parent: [Thesis manuscript assembly](../spec.md)

## Question

Can the analytical chapter explain exactly when guarded SmartDCA wins, ties, or loses on a realized ledger without turning finite witnesses or ledger-conditioned boundaries into universal performance claims?

## What to build

A reader can inspect finite examples, score and floor mechanisms, and the terminal cash-unit classification to understand precisely what theory can and cannot say about adaptive performance.

## Acceptance criteria

- [x] The two-purchase evaluation-price boundary and the irrelevance of beta at that horizon are stated within their proved scope.
- [x] The three-purchase beta-sensitive boundary and exact flip witness are presented as existence and classification evidence rather than a general parameter ranking.
- [x] The arbitrary-horizon cash-timing identity is explained as a model-general accounting decomposition.
- [x] Corrected-neutral score crossing is separated from guarded cash single crossing, including the role of policy-specific clipped floors.
- [x] Reference-aligned guardrail feedback is stated as a sufficient condition without being mislabeled necessary.
- [x] The terminal-inventory relation H plus P times U is used as the exact necessary-and-sufficient realized-ledger classification.
- [x] Finite witnesses, weak-single-valley analysis, arbitrary-horizon results, and stochastic questions remain visibly distinct.
- [x] The body emphasizes meaning and decisive equations while detailed proofs, cases, and exact witnesses are placed in appendices.
- [x] All theorem wording, equality directions, notation, and evidence mappings pass independent domain review and the canonical build.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
- Claimed for implementation on 2026-09-04 after ticket 07 was verified resolved.
- Independent domain, Standards, and specification review on 2026-09-04 checked the finite thresholds and endpoints, beta-sensitive state dependence and witness, arbitrary-horizon identities, cash-crossing assumptions and direction, terminal-inventory trichotomy, evidence-layer boundaries, notation, and direct authorities. Follow-up domain review passed with no remaining finding after the two-purchase cash scalar became `c_a`, the three-purchase term `g` was tied to date-two state and observed `p_3`, the scope table linked canonical and detailed authorities directly, and theorem-local mutation probes replaced chapter-wide substring checks. Standards and specification follow-up reviews also passed with no remaining finding.
- Final verification on 2026-09-04 passed the complete repository catalog: 221 unit tests, all 25 scientific checks, direct manuscript controls, and the repository Markdown-link audit. The managed macOS seam additionally passed all 86 focused tests and built the canonical 70-page A4 PDF. Chapter 5 pages 26--34, Table 5.2, and Appendix B pages 48--53 were visually inspected; the LaTeX log contains no overfull or underfull boxes, undefined references, or package warnings. The submission gate remains expectedly closed only on retained institutional placeholders.

## Answer

Ticket 08 is resolved. Chapter 5 now moves from exact two- and three-purchase evaluation-price boundaries through the model-general cash-timing identity, weak-single-valley falsification, qualified guardrail-feedback mechanism, and the necessary-and-sufficient terminal-cash/unit classification. Table 5.2 keeps finite witnesses, deterministic searches, arbitrary-horizon theorems, and later stochastic questions in their proper evidence layers. Appendix B retains the complete reductions, witnesses, derivations, sharpness cases, and affine proof. Eight reviewed claim records, five notation records, the universal-superiority non-claim, and a section-local fail-closed boundary audit keep the manuscript tied to canonical evidence. Ticket 09 is the next unblocked drafting frontier.
