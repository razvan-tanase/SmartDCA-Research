# 01 — Freeze the institutional contract and establish the manuscript build

Type: task
Status: open
Triage: ready-for-agent
Blocked by: none
Parent: [Thesis manuscript assembly](../spec.md)

## Question

Can the authoritative institutional and supervisor requirements be frozen before prose expands, and can one canonical manuscript source already produce a minimally compliant PDF without hidden local assumptions?

## What to build

A master's candidate can inspect one approved manuscript contract, build a minimal thesis shell from the declared environment, and see unresolved institutional inputs fail visibly before they can reach a submission candidate.

## Acceptance criteria

- [x] The official template and every available university, faculty, program, and supervisor requirement are captured from authoritative sources with provenance and access dates.
- [x] The contract records language, working title status, submission date, expected extent, required front matter, citation style, page and typography rules, file format, metadata, archival requirements, and supervisor-specific constraints.
- [x] Any requirement that cannot be established authoritatively is assigned to the candidate or supervisor as an explicit unresolved decision rather than guessed.
- [x] The canonical authoring and build format is selected only after the official template is inspected, and the decision preserves one authoritative source with derived rendered releases.
- [ ] One documented clean-environment command builds a minimal body, appendix, bibliography, generated-asset placeholder, and submission-format PDF.
- [x] The rendered shell is checked against every institutional requirement that can already be tested.
- [x] The release check fails when a required institutional value, placeholder, citation, or build input remains unresolved.
- [x] The contract and build instructions are understandable without hidden conversation context, and continuous chapter drafting has not begun.

## Comments

- Created from the user-approved 17-ticket decomposition on 2026-09-01.
- This ticket is a vertical manuscript slice: its prose, citations, evidence mappings, generated assets where applicable, and canonical build must agree before resolution.
- Implemented locally on 2026-09-02 in commit `85b6595`: the candidate-supplied official ACS template is retained byte-for-byte, its requirements are mirrored in the frozen contract, and the LaTeX shell, bibliography, generated-asset seam, PDF checks, and fail-closed release gate are documented and tested.
- Local verification: 14 manuscript/release tests pass; direct LaTeX build passes; the rendered PDF is nine A4 pages with bilingual covers, one-page synopsis/abstract, body, appendix, generated asset, and bibliography; `git diff --check` passes; the release gate exits 1 for the intentionally unresolved candidate/supervisor decisions and visible placeholders.
- Interrupted publication on 2026-09-02: the selected GitHub connector reached its enforced usage limit after uploading 15 of 33 blobs. No remote commit, branch ref, or workflow run was created. Docker is not installed in this workspace, so the clean-container command could not be executed locally. Resume by publishing commit `85b6595` through GitHub and verifying the `manuscript-shell` workflow before resolving this ticket.
- The repository-wide verification command was started after the focused checks and reached the pre-existing `check_stochastic_family_study` replay, which remained CPU-bound for roughly 64 minutes without emitting a failure. It was interrupted to avoid an unbounded wait; no full-suite pass is claimed.
