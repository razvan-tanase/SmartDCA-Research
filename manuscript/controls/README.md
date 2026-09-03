# Thesis architecture and evidence controls

This directory is the drafting contract established before continuous thesis
prose. It fixes the approved three-question narrative, the complete chapter and
appendix route, contribution boundaries, claim authorities, notation, review
workflow, and release transitions. The controls describe a structural shell,
not a submission candidate: unresolved institutional and supervisor-owned
inputs remain in the separate [institutional contract](../contract/institutional-contract.md).

## Registers

| Register | Authority |
|---|---|
| [`architecture.json`](architecture.json) | Working title, three research questions and conservative answers, safety-versus-adaptivity spine, chapter dependencies, reader outcomes, and body-versus-appendix rules. |
| [`contributions.json`](contributions.json) | Mathematical, computational, methodological, empirical, and integrative contribution matrix with evidence and novelty boundaries. |
| [`non-claims.json`](non-claims.json) | Claims the thesis rejects and the wording required in their place. |
| [`claims.json`](claims.json) | Stable claim-to-evidence entries for every canonical definition and theorem, current empirical headline, and selected manuscript table and figure. |
| [`notation.json`](notation.json) | Governing symbols, first-use locations, and every intentional repository-to-manuscript reconciliation. |
| [`governance.json`](governance.json) | Terminology, citations, generated assets, dependencies, supervisor feedback, and release-state rules. |
| [`supervisor-feedback.json`](supervisor-feedback.json) | Dated feedback ledger. It is intentionally empty until actual feedback is received. |

[`control-manifest.json`](control-manifest.json) names the complete package.
Every register record has a globally stable `id`, a `mandatory` flag, and a
`review_state`. Accepted state values are `accepted`, `reviewed`, `planned`,
`pending`, `blocked`, and `unresolved`; only `accepted` and `reviewed` satisfy a
mandatory record. The public validator fails when files or required fields are
missing, identifiers collide, review-state values are unknown, mandatory
records remain unresolved, evidence paths do not exist, or the structural shell
drifts from the accepted architecture:

```bash
python manuscript/check_controls.py
```

`python manuscript/build.py` runs that check before LaTeX. The submission gate
also consumes the same verdict once the controls manifest is declared as a
release input. Passing the control check means the drafting architecture is
internally ready; it does not resolve personal, institutional, supervisor, or
final-release decisions.

## Change workflow

1. Change the authoritative evidence or approved manuscript decision first.
2. Update the affected register entry without strengthening its scope.
3. Add a new stable ID for a new claim or asset; never silently reuse an old ID
   for a different statement.
4. Update the notation mapping and structural shell when a chapter-visible
   term, symbol, or location changes.
5. Regenerate or reconcile every affected table and figure.
6. Run the control check, manuscript tests, canonical build, link check, and
   the scientific check attached to every changed scientific claim.
7. Record actual supervisor feedback in the feedback ledger; route scientific
   changes into separately tracked work.

Detailed proofs and exhaustive cases remain in repository evidence and later
appendices. The body keeps assumptions, decisive equations, theorem meaning,
algorithm logic, empirical design, results, and interpretation at the depth
needed by a Financial Computing committee.
