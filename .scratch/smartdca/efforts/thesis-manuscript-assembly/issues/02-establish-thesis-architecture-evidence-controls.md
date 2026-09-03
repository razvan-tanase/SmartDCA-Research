# 02 — Establish the thesis architecture and evidence controls

Type: task
Status: resolved
Triage: ready-for-agent
Blocked by: 01
Parent: [Thesis manuscript assembly](../spec.md)

## Question

Can the approved three-question thesis narrative be represented as a buildable chapter architecture with stable terminology, contribution boundaries, and evidence controls before continuous prose is drafted?

## What to build

A supervisor or implementing agent can navigate the complete thesis skeleton, understand what each chapter proves or reports, and trace every seeded headline claim to its authoritative evidence and accepted scope.

## Acceptance criteria

- [x] The working title, three research questions, conservative answers, and safety-versus-adaptivity narrative are fixed as the manuscript spine.
- [x] Every planned chapter and appendix has a purpose, prerequisites, intended reader outcome, and explicit body-versus-appendix placement rule.
- [x] A contribution matrix distinguishes mathematical, computational, methodological, empirical, and integrative contributions.
- [x] A non-claim matrix records at least the rejected new-mean-class claim, universal-superiority claim, confirmed incremental signal-value claim, and frictional-safety extension.
- [x] One claim-to-evidence register records stable identifiers, wording, claim class, scope, authority, manuscript location, citation needs, and review state.
- [x] The register is seeded with every canonical definition, theorem, empirical headline, planned table, and planned figure already known to belong in the thesis.
- [x] One notation register governs symbols and records every intentional reconciliation between repository notation and manuscript notation.
- [x] Chapter dependencies, terminology authority, citation workflow, generated-asset policy, supervisor-feedback log, and release-state transitions are documented.
- [x] The canonical build renders the complete structural shell and rejects duplicate identifiers or unresolved mandatory control entries.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
- Claimed on 2026-09-02. The public verification seams are `python manuscript/check_controls.py` for the architecture and evidence controls and `python manuscript/build.py` for the rendered structural shell; the canonical build must fail before LaTeX when mandatory controls are invalid.


- Follow-up on 2026-09-03: implementation commit `a864f6c8ccf4fadb72faae737f3449ad20c895fc` was published on [`agent/implement-thesis-architecture-controls`](https://github.com/razvan-tanase/SmartDCA-Research/tree/agent/implement-thesis-architecture-controls). GitHub Verification run [240](https://github.com/razvan-tanase/SmartDCA-Research/actions/runs/33709252227) completed successfully: both the scientific `checks` job and the clean-container `manuscript-shell` job passed.
- Independent Standards and specification reviews reported no findings after the path-containment and fail-closed release-control hardening.
- The protected `main` ref remains unchanged; the implementation branch is ready for merge.

## Answer

Ticket 02 is resolved on the implementation branch. The thesis spine, chapter and appendix architecture, contribution and non-claim boundaries, claim-to-evidence and notation registers, governance controls, complete structural shell, duplicate/unresolved rejection, and build-time control gate are versioned and verified. Tickets 03, 04, and 05 are now the next unblocked literature strands. The release checker continues to reject the shell until the explicitly owned institutional and supervisor decisions are supplied.